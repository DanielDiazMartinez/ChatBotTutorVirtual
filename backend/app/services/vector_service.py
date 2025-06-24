"""
Servicio de Vector - Capa intermedia
Este servicio maneja las operaciones con vectores y búsqueda semántica.
Solo puede depender de servicios de la capa base (embedding_service, document_service).
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
import logging

from app.crud import crud_vector
from app.services.embedding_service import get_embedding_for_query

def search_similar_chunks(db: Session,
                          query_embedding: List[float],
                          subject_id: Optional[int] = None,
                          limit: int = 10,
                          similarity_metric: str = "cosine") -> List[Tuple]:
    """
    Busca chunks similares a un embedding de consulta usando pgvector
    
    Args:
        db: Sesión de SQLAlchemy
        query_embedding: Vector de embedding de la consulta
        subject_id: ID de la asignatura (opcional)
        limit: Número máximo de chunks a devolver
        similarity_metric: Métrica de similitud a usar ("cosine", "l2", "inner_product")
        
    Returns:
        Lista de tuplas (chunk, score) ordenadas por similitud
    """
    logger = logging.getLogger(__name__)
    
    # Log para depuración
    logger.info(f"Buscando chunks similares, subject_id={subject_id}, limit={limit}")
    
    if not query_embedding or len(query_embedding) == 0:
        logger.error("query_embedding es None o vacío en search_similar_chunks")
        return []
        
    # Log de dimensiones del embedding
    logger.info(f"Dimensión del embedding de consulta: {len(query_embedding)}")
    
    # Si se proporciona subject_id, hacer logs de diagnóstico
    if subject_id:
        # Log para verificar documentos de asignatura
        doc_count = crud_vector.count_documents_by_subject_id(db, subject_id)
        logger.info(f"Documentos encontrados para subject_id={subject_id}: {doc_count}")
        
        # Verificar si los documentos tienen chunks
        documents = crud_vector.get_documents_by_subject_id(db, subject_id)
        for doc in documents:
            chunk_count = crud_vector.count_chunks_by_document_id(db, doc.id)
            logger.info(f"Documento id={doc.id}, título='{doc.title}' tiene {chunk_count} chunks")
            
            # Verificar si los chunks tienen embeddings válidos
            if chunk_count > 0:
                sample_chunk = crud_vector.get_sample_chunk_by_document_id(db, doc.id)
                if sample_chunk and sample_chunk.embedding:
                    embedding_dim = len(sample_chunk.embedding)
                    logger.info(f"Un chunk del documento {doc.id} tiene un embedding de dimensión {embedding_dim}")
                else:
                    logger.warning(f"Los chunks del documento {doc.id} no tienen embeddings válidos")
    
    # Usar función CRUD para buscar chunks similares
    results = crud_vector.search_similar_chunks_db(
        db=db,
        query_embedding=query_embedding,
        subject_id=subject_id,
        limit=limit,
        similarity_metric=similarity_metric
    )
    
    # Log del número de resultados encontrados
    logger.info(f"Resultados encontrados: {len(results)}")
    
    # Si no hay resultados, hacer log para depuración
    if len(results) == 0:
        logger.warning("No se encontraron chunks similares")
        
        # Verificar si hay chunks en la base de datos
        chunk_count = crud_vector.count_total_chunks(db)
        logger.info(f"Total de chunks en la base de datos: {chunk_count}")
        
        # Si hay subject_id, verificar que hay chunks relacionados
        if subject_id:
            related_chunks = crud_vector.count_chunks_by_subject_id(db, subject_id)
            logger.info(f"Chunks relacionados con subject_id={subject_id}: {related_chunks}")

    return results



def add_user_message(
    db: Session,
    conversation_id: int,
    message_text: str = None,
    image_id: int = None
):
    """
    Añade un mensaje del usuario a una conversación existente.
    Se puede proporcionar texto, imagen o ambos.
    """
    # Verificar que la conversación existe usando CRUD
    conversation = crud_vector.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Crear embedding para el mensaje si hay texto
    question_embedding = get_embedding_for_query(message_text) if message_text else None
    
    # Crear el mensaje del usuario usando CRUD
    user_msg = crud_vector.create_user_message(
        db=db,
        conversation_id=conversation_id,
        message_text=message_text,
        image_id=image_id,
        embedding=question_embedding
    )
    
    return user_msg

def add_bot_message(
    db: Session,
    conversation_id: int,
    message_text: str
):
    """
    Añade un mensaje del bot a una conversación existente.
    """
    # Verificar que la conversación existe usando CRUD
    conversation = crud_vector.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Crear embedding para el mensaje
    bot_embedding = get_embedding_for_query(message_text)
    
    # Crear el mensaje del bot usando CRUD
    bot_msg = crud_vector.create_bot_message(
        db=db,
        conversation_id=conversation_id,
        message_text=message_text,
        embedding=bot_embedding
    )
    
    return bot_msg

def get_conversation_context(
    db: Session,
    message_text: str = None,
    subject_id: int = None,
    limit: int = 10,
    similarity_metric: str = "cosine"
) -> str:
    """
    Obtiene el contexto de todos los documentos de una asignatura
    basado en la similitud con el mensaje.
    
    Args:
        db: Sesión de SQLAlchemy
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
        
    # Es opcional tener subject_id
    if subject_id is None:
        logger.warning("get_conversation_context llamado sin subject_id")
        return ""
    
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
            # Obtener el título del documento usando CRUD
            title_str = crud_vector.get_document_title_by_id(db, chunk.document_id)
            if not title_str:
                title_str = "Documento desconocido"
            
            # Log de la puntuación de similitud
            logger.info(f"Chunk {i+1}: score={score:.4f}, documento='{title_str}', longitud={len(chunk.content)}")
            
            # Formatear el chunk con información del documento
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
    # Obtener mensajes usando CRUD
    message_history = crud_vector.get_messages_by_conversation_id(db, conversation_id, limit)
    
    message_history.reverse()
    
    conversation_history = "\n".join(
        [f"{'Usuario' if not msg.is_bot else 'Bot'}: {msg.text}" for msg in message_history]
    )
    
    return conversation_history