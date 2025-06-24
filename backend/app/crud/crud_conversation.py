from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.models import Conversation, Message, Subject, User

def create_conversation(db: Session, user_id: int, subject_id: int) -> Conversation:
    """
    Crea una nueva conversación en la base de datos.
    """
    conversation = Conversation(
        user_id=user_id,
        subject_id=subject_id
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversations_by_user_role(db: Session, user_id: int, role: str) -> List[Conversation]:
    """
    Obtiene todas las conversaciones asociadas a un usuario según su rol desde la BD.
    """
    query = db.query(Conversation)
    
    if role == "student":
        query = query.filter(Conversation.user_id == user_id)
    elif role == "teacher":
        # Los profesores solo pueden ver sus propias conversaciones
        query = query.filter(Conversation.user_id == user_id)
    elif role == "admin":
        # Los administradores pueden ver todas las conversaciones
        pass
    else:
        # La validación del rol debe ocurrir en la capa de servicio
        return []
        
    return query.all()

def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    """
    Obtiene una conversación específica por su ID desde la BD.
    """
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def delete_conversation(db: Session, conversation: Conversation) -> None:
    """
    Elimina una conversación de la BD.
    """
    db.delete(conversation)
    db.commit()

def get_last_message_for_conversation(db: Session, conversation_id: int) -> Optional[Message]:
    """
    Obtiene el último mensaje de una conversación.
    """
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).first()

def get_messages_by_conversation_id(db: Session, conversation_id: int) -> List[Message]:
    """
    Obtiene todos los mensajes de una conversación, ordenados por fecha.
    """
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    """
    Obtiene una asignatura por su ID.
    """
    return db.query(Subject).filter(Subject.id == subject_id).first()
