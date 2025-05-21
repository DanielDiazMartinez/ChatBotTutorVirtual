"""
Servicio de Vector - Capa intermedia
Este servicio maneja las operaciones con vectores y búsqueda semántica.
Solo puede depender de servicios de la capa base (embedding_service, document_service).
"""
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
from app.services.embedding_service import get_embedding_for_query

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
    user_type: str,
    subject_id: int
) -> Conversation:
    """
    Crea una nueva conversación.
    """
    from ..services.document_service import document_exists
    
    if not document_exists(db, document_id):
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

def add_user_message(
    db: Session,
    conversation_id: int,
    message_text: str
) -> Message:
    """
    Añade un mensaje del usuario a una conversación existente.
    """
    # Verificar que la conversación existe
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Crear embedding para el mensaje
    question_embedding = get_embedding_for_query(message_text)
    
    # Crear el mensaje del usuario
    user_msg = Message(
        text=message_text,
        is_bot=False,
        conversation_id=conversation_id,
        embedding=question_embedding
    )
    
    db.add(user_msg)
    db.flush()
    db.refresh(user_msg)
    
    return user_msg

def add_bot_message(
    db: Session,
    conversation_id: int,
    message_text: str
) -> Message:
    """
    Añade un mensaje del bot a una conversación existente.
    """
    # Verificar que la conversación existe
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Crear embedding para el mensaje
    bot_embedding = get_embedding_for_query(message_text)
    
    # Crear el mensaje del bot
    bot_msg = Message(
        text=message_text,
        is_bot=True,
        conversation_id=conversation_id,
        embedding=bot_embedding
    )
    
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)
    
    return bot_msg

def get_conversation_context(
    db: Session,
    document_id: int,
    message_text: str,
    limit: int = 5,
    similarity_metric: str = "cosine"
) -> str:
    """
    Obtiene el contexto de un documento específico basado en la similitud con el mensaje.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento
        message_text: Texto del mensaje del usuario
        limit: Número máximo de chunks a devolver
        similarity_metric: Métrica de similitud a usar ("cosine", "l2", "inner_product")
        
    Returns:
        Contexto como string concatenado
    """
    query_embedding = get_embedding_for_query(message_text)
    similar_chunks = search_similar_chunks(
        db=db, 
        query_embedding=query_embedding,
        document_id=document_id,
        limit=limit,
        similarity_metric=similarity_metric
    )
    
    context = " ".join([chunk.content for chunk, _ in similar_chunks])
    return context

def get_conversation_history(
    db: Session,
    conversation_id: int,
    limit: int = 6
) -> str:
    """
    Obtiene el historial de conversación formateado como string.
    
    Args:
        db: Sesión de SQLAlchemy
        conversation_id: ID de la conversación
        limit: Número máximo de mensajes a recuperar
        
    Returns:
        Historial de conversación formateado
    """
    message_history = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    message_history.reverse()
    
    conversation_history = "\n".join(
        [f"{'Usuario' if not msg.is_bot else 'Bot'}: {msg.text}" for msg in message_history]
    )
    
    return conversation_history