"""
Servicio de Mensajes - Capa de lógica de negocio
Este servicio maneja toda la lógica relacionada con los mensajes de usuarios.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.crud import crud_message

# Configuración de logging
logger = logging.getLogger(__name__)


def get_user_messages_with_filters(
    db: Session,
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene todos los mensajes (mensajes de usuarios) con información del usuario,
    asignatura y tema, aplicando los filtros especificados.
    
    Args:
        db: Sesión de SQLAlchemy
        subject_id: ID de la asignatura para filtrar (opcional)
        topic_id: ID del tema para filtrar (opcional)
        user_id: ID del usuario para filtrar (opcional)
        limit: Número máximo de resultados (opcional)
        
    Returns:
        Lista de diccionarios con la información de los mensajes
    """
    try:
        # Obtener mensajes usando CRUD
        messages = crud_message.get_user_messages_filtered(
            db, subject_id, topic_id, user_id, limit
        )
        
        # Transformar los resultados al formato esperado
        messages_data = []
        for message in messages:
            conversation = message.conversation
            user = conversation.user
            subject = conversation.subject
            
            # Obtener el tema si existe
            topic = None
            if subject:
                if topic_id:
                    # Si se especificó un topic_id, buscar ese tema específico
                    topic = crud_message.get_topic_by_id_and_subject(db, topic_id, subject.id)
                else:
                    # Si no se especificó topic_id, obtener el primer tema de la asignatura
                    topic = crud_message.get_topic_by_subject_id(db, subject.id)
            
            message_data = {
                "id": str(message.id),
                "text": message.text,
                "subject": subject.name if subject else "Sin asignatura",
                "topic": topic.name if topic else "Sin tema",
                "userId": str(user.id),
                "userName": user.full_name or "Usuario sin nombre",
                "userEmail": user.email,
                "createdAt": message.created_at.isoformat() if message.created_at else None
            }
            messages_data.append(message_data)
        
        logger.info(f"Se obtuvieron {len(messages_data)} mensajes con filtros: subject_id={subject_id}, topic_id={topic_id}, user_id={user_id}")
        return messages_data
        
    except Exception as e:
        logger.error(f"Error al obtener mensajes: {str(e)}")
        raise e


def get_messages_statistics(
    db: Session,
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre los mensajes de usuarios.
    
    Args:
        db: Sesión de SQLAlchemy
        subject_id: ID de la asignatura para filtrar (opcional)
        topic_id: ID del tema para filtrar (opcional)
        
    Returns:
        Diccionario con estadísticas de los mensajes
    """
    try:
        # Contar total de mensajes usando CRUD
        total_messages = crud_message.count_user_messages_filtered(db, subject_id, topic_id)
        
        # Contar usuarios únicos usando CRUD
        unique_users = crud_message.count_unique_users_filtered(db, subject_id, topic_id)
        
        # Contar mensajes por asignatura (si no se está filtrando por asignatura)
        messages_by_subject = {}
        if not subject_id:
            subject_counts = crud_message.get_messages_by_subject_counts(db)
            messages_by_subject = {name: count for name, count in subject_counts}
        
        statistics = {
            "total_messages": total_messages,
            "unique_users": unique_users,
            "messages_by_subject": messages_by_subject
        }
        
        logger.info(f"Estadísticas calculadas: {statistics}")
        return statistics
        
    except Exception as e:
        logger.error(f"Error al calcular estadísticas: {str(e)}")
        raise e


def get_message_by_id(db: Session, message_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un mensaje específico por su ID con información del tema.
    
    Args:
        db: Sesión de SQLAlchemy
        message_id: ID del mensaje
        
    Returns:
        Diccionario con la información del mensaje o None si no existe
    """
    try:
        # Obtener mensaje usando CRUD
        message = crud_message.get_message_by_id(db, message_id)
        
        if not message:
            return None
        
        conversation = message.conversation
        user = conversation.user
        subject = conversation.subject
        
        # Obtener el primer tema de la asignatura como referencia
        topic = None
        if subject:
            topic = crud_message.get_topic_by_subject_id(db, subject.id)
        
        # Crear un objeto similar a lo que espera el servicio de IA
        message_data = type('Message', (), {
            'id': message.id,
            'content': message.text,
            'subject_id': subject.id if subject else None,
            'topic_id': topic.id if topic else None,
            'user_id': user.id,
            'created_at': message.created_at
        })()
        
        logger.info(f"Mensaje obtenido para análisis: {message_id}")
        return message_data
        
    except Exception as e:
        logger.error(f"Error al obtener mensaje {message_id}: {str(e)}")
        raise e


def get_detailed_message_by_id(db: Session, message_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un mensaje específico por su ID con información detallada para la UI.
    
    Args:
        db: Sesión de SQLAlchemy
        message_id: ID del mensaje
        
    Returns:
        Diccionario con la información detallada del mensaje o None si no existe
    """
    try:
        # Obtener mensaje usando CRUD
        message = crud_message.get_message_by_id(db, message_id)
        
        if not message:
            return None
        
        conversation = message.conversation
        user = conversation.user
        subject = conversation.subject
        
        # Obtener el tema si existe
        topic = None
        if subject:
            topic = crud_message.get_topic_by_subject_id(db, subject.id)
        
        message_data = {
            "id": str(message.id),
            "text": message.text,
            "subject": subject.name if subject else "Sin asignatura",
            "topic": topic.name if topic else "Sin tema",
            "userId": str(user.id),
            "userName": user.full_name or "Usuario sin nombre",
            "userEmail": user.email,
            "createdAt": message.created_at.isoformat() if message.created_at else None
        }
        
        logger.info(f"Mensaje detallado obtenido: {message_id}")
        return message_data
        
    except Exception as e:
        logger.error(f"Error al obtener mensaje detallado {message_id}: {str(e)}")
        raise e


def get_recent_messages(
    db: Session,
    limit: int = 10,
    subject_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene los mensajes más recientes.
    
    Args:
        db: Sesión de SQLAlchemy
        limit: Número máximo de mensajes a retornar
        subject_id: ID de la asignatura para filtrar (opcional)
        
    Returns:
        Lista de diccionarios con los mensajes más recientes
    """
    return get_user_messages_with_filters(
        db=db,
        subject_id=subject_id,
        limit=limit
    )
