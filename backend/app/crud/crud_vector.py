from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, literal_column
from app.models.models import Document, DocumentChunk, Conversation, Message

def search_similar_chunks_db(
    db: Session,
    query_embedding: List[float],
    subject_id: Optional[int] = None,
    limit: int = 10,
    similarity_metric: str = "cosine"
) -> List[Tuple[DocumentChunk, float]]:
    """
    Busca chunks similares a un embedding de consulta usando pgvector desde la BD.
    """
    if not query_embedding or len(query_embedding) == 0:
        return []
        
    embedding_str = f"CAST(ARRAY[{', '.join(map(str, query_embedding))}] AS vector)"

    if similarity_metric == "cosine":
        distance_expression = literal_column(f"({DocumentChunk.embedding.key} <=> {embedding_str})")
        convert_score = lambda x: 1.0 - x
    elif similarity_metric == "l2":
        distance_expression = literal_column(f"({DocumentChunk.embedding.key} <-> {embedding_str})")
        convert_score = lambda x: 1.0 / (1.0 + x)
    else:
        distance_expression = literal_column(f"({DocumentChunk.embedding.key} <#> {embedding_str})")
        convert_score = lambda x: -x

    # Construir la consulta base
    query = select(
        DocumentChunk,
        distance_expression.label("distance")
    )
    
    # Si se proporciona subject_id, filtrar por los documentos de esa asignatura
    if subject_id:
        query = query.join(Document, DocumentChunk.document_id == Document.id)
        query = query.filter(Document.subject_id == subject_id)
    
    # Ordenar por distancia y limitar resultados
    query = query.order_by("distance").limit(limit)
    results = db.execute(query).all()

    return [(row.DocumentChunk, convert_score(row.distance)) for row in results]

def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    """
    Obtiene una conversación por su ID desde la BD.
    """
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def create_user_message(
    db: Session,
    conversation_id: int,
    message_text: str = None,
    image_id: int = None,
    embedding: List[float] = None
) -> Message:
    """
    Crea un mensaje del usuario en la BD.
    """
    user_msg = Message(
        text=message_text,
        is_bot=False,
        conversation_id=conversation_id,
        embedding=embedding,
        image_id=image_id
    )
    
    db.add(user_msg)
    db.flush()
    db.refresh(user_msg)
    
    return user_msg

def create_bot_message(
    db: Session,
    conversation_id: int,
    message_text: str,
    embedding: List[float] = None
) -> Message:
    """
    Crea un mensaje del bot en la BD.
    """
    bot_msg = Message(
        text=message_text,
        is_bot=True,
        conversation_id=conversation_id,
        embedding=embedding
    )
    
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)
    
    return bot_msg

def get_document_title_by_id(db: Session, document_id: int) -> Optional[str]:
    """
    Obtiene el título de un documento por su ID desde la BD.
    """
    result = db.query(Document.title).filter(Document.id == document_id).first()
    return result[0] if result else None

def get_messages_by_conversation_id(db: Session, conversation_id: int, limit: int = 10) -> List[Message]:
    """
    Obtiene los mensajes de una conversación desde la BD.
    """
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(limit).all()

def count_documents_by_subject_id(db: Session, subject_id: int) -> int:
    """
    Cuenta los documentos de una asignatura desde la BD.
    """
    return db.query(Document).filter(Document.subject_id == subject_id).count()

def get_documents_by_subject_id(db: Session, subject_id: int) -> List[Document]:
    """
    Obtiene los documentos de una asignatura desde la BD.
    """
    return db.query(Document).filter(Document.subject_id == subject_id).all()

def count_chunks_by_document_id(db: Session, document_id: int) -> int:
    """
    Cuenta los chunks de un documento desde la BD.
    """
    return db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).count()

def get_sample_chunk_by_document_id(db: Session, document_id: int) -> Optional[DocumentChunk]:
    """
    Obtiene un chunk de muestra de un documento desde la BD.
    """
    return db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).first()

def count_total_chunks(db: Session) -> int:
    """
    Cuenta el total de chunks en la BD.
    """
    return db.query(DocumentChunk).count()

def count_chunks_by_subject_id(db: Session, subject_id: int) -> int:
    """
    Cuenta los chunks relacionados con una asignatura desde la BD.
    """
    return db.query(DocumentChunk).\
        join(Document, DocumentChunk.document_id == Document.id).\
        filter(Document.subject_id == subject_id).count()
