from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from app.models.models import Message, Conversation, User, Subject, Topic, Document

def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    """
    Obtiene una asignatura por su ID desde la BD.
    """
    return db.query(Subject).filter(Subject.id == subject_id).first()

def get_student_messages_by_subject(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = None,
    limit: Optional[int] = None
) -> List[Message]:
    """
    Obtiene mensajes de estudiantes por asignatura desde la BD.
    """
    query = db.query(Message).filter(
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    )
    
    # Joins necesarios
    query = query.join(Conversation, Message.conversation_id == Conversation.id)
    query = query.join(User, Conversation.user_id == User.id)
    
    # Filtrar por asignatura y rol de estudiante
    query = query.filter(
        Conversation.subject_id == subject_id,
        User.role == "student"
    )
    
    # Filtrar por fecha si se especifica
    if days_limit:
        date_threshold = datetime.utcnow() - timedelta(days=days_limit)
        query = query.filter(Message.created_at >= date_threshold)
    
    # Ordenar por fecha descendente y aplicar límite
    query = query.order_by(Message.created_at.desc())
    if limit:
        query = query.limit(limit)
    
    return query.all()

def count_student_messages_by_subject(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = None
) -> int:
    """
    Cuenta mensajes de estudiantes por asignatura desde la BD.
    """
    query = db.query(Message).filter(
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    )
    
    query = query.join(Conversation, Message.conversation_id == Conversation.id)
    query = query.join(User, Conversation.user_id == User.id)
    query = query.filter(
        Conversation.subject_id == subject_id,
        User.role == "student"
    )
    
    if days_limit:
        date_threshold = datetime.utcnow() - timedelta(days=days_limit)
        query = query.filter(Message.created_at >= date_threshold)
    
    return query.count()

def count_unique_students_by_subject(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = None
) -> int:
    """
    Cuenta estudiantes únicos que han participado en una asignatura desde la BD.
    """
    query = db.query(Message).filter(
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    )
    
    query = query.join(Conversation, Message.conversation_id == Conversation.id)
    query = query.join(User, Conversation.user_id == User.id)
    query = query.filter(
        Conversation.subject_id == subject_id,
        User.role == "student"
    )
    
    if days_limit:
        date_threshold = datetime.utcnow() - timedelta(days=days_limit)
        query = query.filter(Message.created_at >= date_threshold)
    
    return query.with_entities(distinct(User.id)).count()

def count_total_students_in_subject(db: Session, subject_id: int) -> int:
    """
    Cuenta el total de estudiantes matriculados en una asignatura desde la BD.
    """
    return db.query(User).join(
        User.subjects
    ).filter(
        Subject.id == subject_id,
        User.role == "student"
    ).count()

def get_documents_by_subject_limited(db: Session, subject_id: int, limit: int = 10) -> List[Document]:
    """
    Obtiene documentos de una asignatura limitados desde la BD.
    """
    return db.query(Document).filter(
        Document.subject_id == subject_id
    ).limit(limit).all()

def get_topics_by_subject_limited(db: Session, subject_id: int, limit: int = 8) -> List[Topic]:
    """
    Obtiene temas de una asignatura limitados desde la BD.
    """
    return db.query(Topic).filter(
        Topic.subject_id == subject_id
    ).limit(limit).all()

def get_most_active_students_by_subject(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = None,
    limit: int = 10
) -> List[Tuple[int, str, str, int]]:
    """
    Obtiene los estudiantes más activos en una asignatura desde la BD.
    
    Returns:
        Lista de tuplas (user_id, full_name, email, message_count)
    """
    query = db.query(
        User.id,
        User.full_name,
        User.email,
        func.count(Message.id).label('message_count')
    ).select_from(User)
    
    query = query.join(Conversation, User.id == Conversation.user_id)
    query = query.join(Message, Conversation.id == Message.conversation_id)
    
    query = query.filter(
        Conversation.subject_id == subject_id,
        User.role == "student",
        Message.is_bot == False,
        Message.text.isnot(None),
        Message.text != ""
    )
    
    # Filtrar por fecha si se especifica
    if days_limit:
        date_threshold = datetime.utcnow() - timedelta(days=days_limit)
        query = query.filter(Message.created_at >= date_threshold)
    
    # Agrupar y ordenar
    query = query.group_by(User.id, User.full_name, User.email)
    query = query.order_by(func.count(Message.id).desc())
    query = query.limit(limit)
    
    return query.all()
