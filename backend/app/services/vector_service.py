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
                          subject_id: Optional[int] = None,
                          limit: int = 3,
                          similarity_metric: str = "cosine") -> List[Tuple[DocumentChunk, float]]:
    """
    Busca chunks similares a un embedding de consulta usando pgvector
    
    Args:
        db: Sesión de SQLAlchemy
        query_embedding: Vector de embedding de la consulta
        document_id: ID del documento (opcional)
        subject_id: ID de la asignatura (opcional)
        limit: Número máximo de chunks a devolver
        similarity_metric: Métrica de similitud a usar ("cosine", "l2", "inner_product")
        
    Returns:
        Lista de tuplas (chunk, score) ordenadas por similitud
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

    # Construir la consulta base
    query = select(
        DocumentChunk,
        distance_expression.label("distance")
    )
    
    # Si se proporciona document_id, filtrar por ese documento
    if document_id:
        query = query.filter(DocumentChunk.document_id == document_id)
    
    # Si se proporciona subject_id, filtrar por los documentos de esa asignatura
    if subject_id:
        query = query.join(Document, DocumentChunk.document_id == Document.id)
        query = query.filter(Document.subject_id == subject_id)
        
        # Optimización: priorizamos chunks donde la distancia es baja
        # Sin embargo, para mantener la diversidad, intentamos obtener chunks de diferentes documentos
        # si es posible mediante una subquery para obtener el mejor chunk de cada documento
        if limit > 1:
            # Obtener primero los documentos de la asignatura
            documents = db.query(Document.id).filter(Document.subject_id == subject_id).all()
            doc_ids = [doc[0] for doc in documents]
            
            if len(doc_ids) > 1:
                # Si hay varios documentos, podemos intentar obtener diversidad
                # Sin embargo, mantenemos la query original porque es más simple y general
                pass
    
    # Ordenar por distancia y limitar resultados
    query = query.order_by("distance").limit(limit)

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
    document_id: int = None,
    message_text: str = None,
    subject_id: int = None,
    limit: int = 5,
    similarity_metric: str = "cosine"
) -> str:
    """
    Obtiene el contexto de un documento específico o de todos los documentos
    de una asignatura basado en la similitud con el mensaje.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento (opcional si se proporciona subject_id)
        message_text: Texto del mensaje del usuario
        subject_id: ID de la asignatura (opcional)
        limit: Número máximo de chunks a devolver
        similarity_metric: Métrica de similitud a usar ("cosine", "l2", "inner_product")
        
    Returns:
        Contexto como string concatenado
    """
    if not message_text:
        return ""
        
    # Validar que se proporcionó al menos uno de document_id o subject_id
    if document_id is None and subject_id is None:
        raise ValueError("Se requiere proporcionar document_id o subject_id")
        
    query_embedding = get_embedding_for_query(message_text)
    similar_chunks = search_similar_chunks(
        db=db, 
        query_embedding=query_embedding,
        document_id=document_id,
        subject_id=subject_id,
        limit=limit,
        similarity_metric=similarity_metric
    )
    
    if not similar_chunks:
        return ""
    
    # Si estamos buscando por subject_id, añadimos información sobre el documento de origen
    if subject_id and not document_id:
        context_parts = []
        for chunk, score in similar_chunks:
            # Obtenemos el título del documento
            document_title = db.query(Document.title).filter(Document.id == chunk.document_id).first()
            title_str = document_title[0] if document_title else "Documento desconocido"
            
            # Formateamos el chunk con información del documento
            context_parts.append(f"[Del documento '{title_str}']: {chunk.content}")
        
        context = "\n\n".join(context_parts)
    else:
        # Comportamiento original para búsqueda en un solo documento
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