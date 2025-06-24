from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, distinct
from app.models.models import Message, Conversation, User, Subject, Topic

def get_user_messages_filtered(
    db: Session,
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: Optional[int] = None
) -> List[Message]:
    """
    Obtiene mensajes de usuarios filtrados desde la BD.
    """
    query = db.query(Message).filter(
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    )
    
    # Hacer joins con las tablas relacionadas
    query = query.join(Conversation, Message.conversation_id == Conversation.id)
    query = query.join(User, Conversation.user_id == User.id)
    query = query.outerjoin(Subject, Conversation.subject_id == Subject.id)
    
    # Aplicar filtros si se proporcionan
    if subject_id:
        query = query.filter(Conversation.subject_id == subject_id)
        
    if user_id:
        query = query.filter(Conversation.user_id == user_id)
    
    # Para el filtro de tema, necesitamos hacer un join adicional
    if topic_id:
        query = query.join(Topic, Subject.id == Topic.subject_id)
        query = query.filter(Topic.id == topic_id)
    
    # Ordenar por fecha de creación descendente
    query = query.order_by(desc(Message.created_at))
    
    # Aplicar límite si se especifica
    if limit:
        query = query.limit(limit)
    
    return query.all()

def count_user_messages_filtered(
    db: Session,
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None
) -> int:
    """
    Cuenta mensajes de usuarios filtrados desde la BD.
    """
    query = db.query(Message).filter(
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    )
    
    query = query.join(Conversation, Message.conversation_id == Conversation.id)
    query = query.outerjoin(Subject, Conversation.subject_id == Subject.id)
    
    if subject_id:
        query = query.filter(Conversation.subject_id == subject_id)
        
    if topic_id:
        query = query.join(Topic, Subject.id == Topic.subject_id)
        query = query.filter(Topic.id == topic_id)
    
    return query.count()

def count_unique_users_filtered(
    db: Session,
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None
) -> int:
    """
    Cuenta usuarios únicos que han enviado mensajes filtrados desde la BD.
    """
    query = db.query(Message).filter(
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    ).join(Conversation, Message.conversation_id == Conversation.id)
    
    if subject_id:
        query = query.filter(Conversation.subject_id == subject_id)
        
    if topic_id:
        query = query.join(Subject, Conversation.subject_id == Subject.id)
        query = query.join(Topic, Subject.id == Topic.subject_id)
        query = query.filter(Topic.id == topic_id)
    
    return query.distinct(Conversation.user_id).count()

def get_messages_by_subject_counts(db: Session) -> List[Tuple[str, int]]:
    """
    Obtiene el conteo de mensajes agrupados por asignatura desde la BD.
    """
    return db.query(Subject.name, func.count(Message.id)).join(
        Conversation, Subject.id == Conversation.subject_id
    ).join(
        Message, Conversation.id == Message.conversation_id
    ).filter(
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    ).group_by(Subject.name).all()

def get_message_by_id(db: Session, message_id: int) -> Optional[Message]:
    """
    Obtiene un mensaje específico por su ID desde la BD.
    """
    return db.query(Message).filter(
        Message.id == message_id,
        Message.is_bot == False,
        Message.text.isnot(None)
    ).first()

def get_topic_by_subject_id(db: Session, subject_id: int) -> Optional[Topic]:
    """
    Obtiene el primer tema de una asignatura desde la BD.
    """
    return db.query(Topic).filter(Topic.subject_id == subject_id).first()

def get_topic_by_id_and_subject(db: Session, topic_id: int, subject_id: int) -> Optional[Topic]:
    """
    Obtiene un tema específico de una asignatura desde la BD.
    """
    return db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.subject_id == subject_id
    ).first()
