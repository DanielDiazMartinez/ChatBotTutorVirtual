from fastapi import HTTPException
from sqlalchemy import and_, select, literal_column
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional

from ..models.models import (
    Document, 
    DocumentChunk,
    CosineDistance, 
    EuclideanDistance, 
    InnerProduct, 
    Conversation, 
    Message, 
    User
)
from ..utils.document_utils import (
    get_embedding_for_query,
    process_document_and_embed_chunks_semantic
)
from ..services.groq_service import generate_groq_response

def insert_document_chunks(
    db: Session,
    document_id: int,
    text: str,
) -> List[DocumentChunk]:
    """
    Divide el texto de un documento en semanticos, genera embeddings para cada uno
    y los inserta en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento al que pertenecen los chunks
        text: Texto completo del documento
        chunk_size: Ya no se usa (el divisor semántico determina el tamaño)
        overlap: Ya no se usa (el divisor semántico maneja la superposición)
        
    Returns:
        Lista de objetos DocumentChunk creados
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"No existe un documento con ID {document_id}")
    
    created_chunks = process_document_and_embed_chunks_semantic(
        document_id=document_id,
        text=text,
        db=db
    )
    db.commit()
    db.refresh(document)
    print(f"Se insertaron {len(created_chunks)} chunks semánticos para el documento ID {document_id}")
    
    return created_chunks

def search_similar_chunks(db: Session,
                          query_embedding: List[float],
                          document_id: Optional[int] = None,
                          limit: int = 3,
                          similarity_metric: str = "cosine") -> List[Tuple[DocumentChunk, float]]:
    """
    Busca chunks similares a un embedding de consulta usando pgvector
    """
    embedding_str = f"CAST(ARRAY[{', '.join(map(str, query_embedding))}] AS vector)"

    if similarity_metric == "cosine":
        distance_expression = CosineDistance(DocumentChunk.embedding, literal_column(embedding_str))
        convert_score = lambda x: 1.0 - x
    elif similarity_metric == "l2":
        distance_expression = EuclideanDistance(DocumentChunk.embedding, literal_column(embedding_str))
        convert_score = lambda x: 1.0 / (1.0 + x)
    else:
        distance_expression = InnerProduct(DocumentChunk.embedding, literal_column(embedding_str))
        convert_score = lambda x: -x

    query = select(
        DocumentChunk,
        distance_expression.label("distance")
    ).filter(DocumentChunk.document_id == document_id if document_id else True).\
        order_by("distance").\
        limit(limit)

    results = db.execute(query).all()

    return [(row.DocumentChunk, convert_score(row.distance)) for row in results]

def create_conversation(
    db: Session,
    document_id: int,
    user_id: int,
    user_type: str,  # "teacher" o "student"
    subject_id: int
) -> Conversation:
    """
    Crea una nueva conversación.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    user = db.query(User).filter(
        and_(User.id == user_id, User.role == user_type)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    new_conversation = Conversation(
        user_id=user_id,
        user_role=user_type,
        document_id=document_id,
        subject_id=subject_id
    )

    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation

def generate_conversation(
    db: Session,
    document_id: int,
    user_id: int,
    user_type: str,
    subject_id: int ,
    initial_message_text: str = None,
) -> Tuple[str, Conversation]:
    """
    Crea una nueva conversación y genera una respuesta inicial si se proporciona un mensaje.
    """
    new_conversation = create_conversation(
        db=db,
        document_id=document_id,
        user_id=user_id,
        user_type=user_type,
        subject_id=subject_id 
    )

    bot_msg = None
    if initial_message_text:
        question_embedding = get_embedding_for_query(initial_message_text)
        user_msg = Message(
            text=initial_message_text,
            is_bot=False,
            conversation_id=new_conversation.id,
            embedding=question_embedding
        )
        db.add(user_msg)
        db.flush()

        similar_chunks = search_similar_chunks(
            db=db, 
            query_embedding=question_embedding,
            document_id=document_id
        )
        context = " ".join([chunk.content for chunk, _ in similar_chunks])
        bot_response = generate_groq_response(initial_message_text, context, "")

        bot_msg = Message(
            text=bot_response,
            is_bot=True,
            conversation_id=new_conversation.id,
            embedding=get_embedding_for_query(bot_response)
        )
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)

        return bot_msg.text, new_conversation
    
    return "", new_conversation

def add_message_and_generate_response(
    db: Session,
    conversation_id: int,
    user_id: int,
    user_type: str,
    message_text: str,
) -> Tuple[Message, Message]:
    """
    Añade un mensaje del usuario a una conversación existente y genera una respuesta.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # Verificar usuario y crear su mensaje
    question_embedding = get_embedding_for_query(message_text)
    user = db.query(User).filter(
        and_(User.id == user_id, User.role == user_type)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if user_type == "student" and conversation.student_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta conversación")
    elif user_type == "teacher" and conversation.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta conversación")

    user_msg_obj = Message(
        text=message_text,
        is_bot=False,
        conversation_id=conversation_id,
        embedding=question_embedding
    )

    db.add(user_msg_obj)
    db.flush()
    db.refresh(user_msg_obj)

    # Buscar chunks similares y generar respuesta
    similar_chunks = search_similar_chunks(
        db=db,
        query_embedding=question_embedding,
        document_id=conversation.document_id
    )
    context = " ".join([chunk.content for chunk, _ in similar_chunks])
    
    # Obtener historial de la conversación
    message_history = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(6).all()
    message_history.reverse()
    conversation_history = "\n".join(
        [f"{'Usuario' if not msg.is_bot else 'Bot'}: {msg.text}" for msg in message_history]
    )

    try:
        response_text = generate_groq_response(message_text, context, conversation_history)
    except Exception as e:
        print(f"Error generating Groq response: {e}")
        response_text = "Lo siento, hubo un error al generar la respuesta."

    bot_msg_obj = Message(
        text=response_text,
        is_bot=True,
        conversation_id=conversation_id,
        embedding=get_embedding_for_query(response_text)
    )

    db.add(bot_msg_obj)
    db.commit()
    db.refresh(bot_msg_obj)

    return user_msg_obj, bot_msg_obj

def get_context(
    db: Session,
    document_id: int,
    message_text: str,
    limit: int = 5,
    similarity_metric: str = "cosine"
) -> List[Tuple[DocumentChunk, float]]:
    """
    Obtiene el contexto de un documento específico.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento
        message_text: Texto del mensaje del usuario
        limit: Número máximo de chunks a devolver
        similarity_metric: Métrica de similitud a usar ("cosine", "l2", "inner_product")
        
    Returns:
        Lista de tuplas (DocumentChunk, score)
    """
    
    query_embedding = get_embedding_for_query(message_text)
    
    
    similar_chunks = search_similar_chunks(db, query_embedding, document_id, limit, similarity_metric)
    
    return similar_chunks