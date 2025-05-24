"""
Servicio de Vector - Capa intermedia
Este servicio maneja las operaciones con vectores y búsqueda semántica.
Solo puede depender de servicios de la capa base (embedding_service, document_service).
"""
from fastapi import HTTPException
from sqlalchemy import and_, select, literal_column
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
import logging

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
                          subject_id: Optional[int] = None,
                          limit: int = 10,
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
    import logging
    logger = logging.getLogger(__name__)
    
    # Log para depuración
    logger.info(f"Buscando chunks similares, subject_id={subject_id}, limit={limit}")
    
    if not query_embedding or len(query_embedding) == 0:
        logger.error("query_embedding es None o vacío en search_similar_chunks")
        return []
        
    # Log de dimensiones del embedding
    logger.info(f"Dimensión del embedding de consulta: {len(query_embedding)}")
        
    embedding_str = f"CAST(ARRAY[{', '.join(map(str, query_embedding))}] AS vector)"

    try:
        if similarity_metric == "cosine":
            # Usamos directamente la sintaxis SQL de pgvector para la distancia coseno
            distance_expression = literal_column(f"({DocumentChunk.embedding.key} <=> {embedding_str})")
            convert_score = lambda x: 1.0 - x
        elif similarity_metric == "l2":
            # Usamos directamente la sintaxis SQL de pgvector para la distancia euclidiana
            distance_expression = literal_column(f"({DocumentChunk.embedding.key} <-> {embedding_str})")
            convert_score = lambda x: 1.0 / (1.0 + x)
        else:
            # Inner product negativo (más alto = más similar)
            distance_expression = literal_column(f"({DocumentChunk.embedding.key} <#> {embedding_str})")
            convert_score = lambda x: -x
        
        logger.info(f"Expresión de distancia creada correctamente: {distance_expression}")
    except Exception as e:
        logger.error(f"Error al crear la expresión de distancia: {str(e)}")
        raise

    # Construir la consulta base
    query = select(
        DocumentChunk,
        distance_expression.label("distance")
    )
    
    
    # Si se proporciona subject_id, filtrar por los documentos de esa asignatura
    if subject_id:
        query = query.join(Document, DocumentChunk.document_id == Document.id)
        query = query.filter(Document.subject_id == subject_id)
        
        # Log para verificar documentos de asignatura
        doc_count = db.query(Document).filter(Document.subject_id == subject_id).count()
        logger.info(f"Documentos encontrados para subject_id={subject_id}: {doc_count}")
        
        # Verificar si los documentos tienen chunks
        for doc in db.query(Document).filter(Document.subject_id == subject_id).all():
            chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            logger.info(f"Documento id={doc.id}, título='{doc.title}' tiene {chunk_count} chunks")
            
            # Verificar si los chunks tienen embeddings válidos
            if chunk_count > 0:
                sample_chunk = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first()
                if sample_chunk and sample_chunk.embedding:
                    embedding_dim = len(sample_chunk.embedding)
                    logger.info(f"Un chunk del documento {doc.id} tiene un embedding de dimensión {embedding_dim}")
                else:
                    logger.warning(f"Los chunks del documento {doc.id} no tienen embeddings válidos")
        
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
    
    # Log del número de resultados encontrados
    logger.info(f"Resultados encontrados: {len(results)}")
    
    # Si no hay resultados, hacer log del query SQL para depuración
    if len(results) == 0:
        logger.warning(f"No se encontraron chunks similares. Query SQL: {query}")
        
        # Verificar si hay chunks en la base de datos
        chunk_count = db.query(DocumentChunk).count()
        logger.info(f"Total de chunks en la base de datos: {chunk_count}")
        
        # Si hay subject_id, verificar que hay chunks relacionados
        if subject_id:
            related_chunks = db.query(DocumentChunk).\
                join(Document, DocumentChunk.document_id == Document.id).\
                filter(Document.subject_id == subject_id).count()
            logger.info(f"Chunks relacionados con subject_id={subject_id}: {related_chunks}")

    return [(row.DocumentChunk, convert_score(row.distance)) for row in results]

def create_conversation(
    db: Session,
    user_id: int,
    user_type: str,
    subject_id: int
) -> Conversation:
    """
    Crea una nueva conversación.
    """
    from ..services.document_service import document_exists
    

    user = db.query(User).filter(
        and_(User.id == user_id, User.role == user_type)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Buscar un documento asociado a la asignatura
    document = db.query(Document).filter(Document.subject_id == subject_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="No se encontraron documentos para la asignatura")
        
    # Crear la conversación con el ID del documento y la asignatura
    new_conversation = Conversation(
        user_id=user_id,
        user_role=user_type,
        subject_id=subject_id,
        document_id=document.id
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
    message_text: str = None,
    subject_id: int = None,
    limit: int = 10,
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
    logger = logging.getLogger(__name__)
    
    if not message_text:
        logger.warning("get_conversation_context llamado con message_text vacío")
        return ""
        
    # Validar que se proporcionó al menos uno de document_id o subject_id
    if subject_id is None:
        logger.error("get_conversation_context llamado sin document_id ni subject_id")
        raise ValueError("Se requiere proporcionar document_id o subject_id")
    
    logger.info(f"Generando contexto para pregunta: '{message_text[:50]}...', subject_id={subject_id}]")
        
    query_embedding = get_embedding_for_query(message_text)
    logger.debug(f"Embedding generado con tamaño: {len(query_embedding)}")
    
    similar_chunks = search_similar_chunks(
        db=db, 
        query_embedding=query_embedding,
        subject_id=subject_id,
        limit=limit,
        similarity_metric=similarity_metric
    )
    
    logger.info(f"Búsqueda de chunks similares completada. Encontrados: {len(similar_chunks)} chunks")
    if not similar_chunks:
        logger.warning(f"No se encontraron chunks similares para la pregunta: '{message_text[:50]}...'")
        return ""
    
    # Si estamos buscando por subject_id, añadimos información sobre el documento de origen
    if subject_id:
        context_parts = []
        logger.info(f"Procesando {len(similar_chunks)} chunks para generar contexto")
        
        for i, (chunk, score) in enumerate(similar_chunks):
            # Obtenemos el título del documento
            document_title = db.query(Document.title).filter(Document.id == chunk.document_id).first()
            title_str = document_title[0] if document_title else "Documento desconocido"
            
            # Log de la puntuación de similitud
            logger.info(f"Chunk {i+1}: score={score:.4f}, documento='{title_str}', longitud={len(chunk.content)}")
            
            # Formateamos el chunk con información del documento
            context_parts.append(f"[Del documento '{title_str}']: {chunk.content}")
        
        context = "\n\n".join(context_parts)
        logger.info(f"Contexto generado con {len(context_parts)} chunks, longitud total: {len(context)} caracteres")
    return context

def get_conversation_history(
    db: Session,
    conversation_id: int,
    limit: int = 10
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