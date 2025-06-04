"""
Servicio de Chat - Capa superior
Este servicio maneja la lógica de chat y puede usar todos los servicios de capas inferiores.
"""
from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
import logging

from ..services.image_service import get_image_by_id, prepare_image_for_google_ai

# Configuración de logging
logger = logging.getLogger(__name__)

from app.models.models import Conversation, Message, User, Subject
from app.services.api_service import generate_google_ai_response
from app.services.vector_service import ( 
    get_conversation_context,
    get_conversation_history,
    add_user_message,
    add_bot_message
)


def create_conversation(
    db: Session,
    user_id: int,
    subject_id: int
) -> Conversation:
    """
    Crea una nueva conversación en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        user_id: ID del usuario creador
        user_type: Rol del usuario ('student', 'teacher', etc.)
        subject_id: ID de la asignatura asociada (opcional)
        
    Returns:
        Objeto de la conversación creada
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
    Obtiene todas las conversaciones asociadas a un usuario según su rol.
    """
    query = db.query(Conversation)
    
    if role == "student":
        query = query.filter(
            Conversation.user_id == user_id
        )
    elif role == "teacher":
        # Los profesores pueden ver sus propias conversaciones y las de sus asignaturas
        teacher = db.query(User).filter(
            and_(User.id == user_id, User.role == "teacher")
        ).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Profesor no encontrado")
            
        subject_ids = [subject.id for subject in teacher.subjects]
        query = query.filter(
            or_(
                Conversation.user_id == user_id,
                Conversation.subject_id.in_(subject_ids)
            )
        )
    elif role == "admin":
        # Los administradores pueden ver todas las conversaciones
        pass
    else:
        raise HTTPException(status_code=400, detail="Rol de usuario inválido")
        
    return query.all()

def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    """
    Obtiene una conversación específica por su ID.
    """
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def delete_conversation(db: Session, conversation_id: int) -> None:
    """
    Elimina una conversación y todos sus mensajes asociados.
    """
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    db.delete(conversation)  # Esto eliminará también los mensajes por la relación cascade
    db.commit()

def get_current_user_conversations(db: Session, user_id: int, role: str, subject_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Obtiene todas las conversaciones del usuario actualmente autenticado y las formatea como diccionarios.
    Si se proporciona subject_id, filtra las conversaciones por esa asignatura.
    """
    conversations = get_conversations_by_user_role(db, user_id, role)
    
    # Filtrar por asignatura si se proporciona subject_id
    if subject_id is not None:
        conversations = [conv for conv in conversations if conv.subject_id == subject_id]
    
    result = []
    for conv in conversations:
        # Obtener el último mensaje de la conversación si existe
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).first()
        
        # Construir el objeto de respuesta
        conv_dict = {
            "id": conv.id,
            "user_id": conv.user_id,
            "subject_id": conv.subject_id,
            "created_at": conv.created_at,
            "last_message": {
                "text": last_message.text if last_message else "",
                "is_bot": last_message.is_bot if last_message else False,
                "created_at": last_message.created_at if last_message else None
            } if last_message else None
        }
        result.append(conv_dict)
    
    return result

def get_conversation_messages(db: Session, conversation_id: int) -> List[Message]:
    """
    Obtiene todos los mensajes de una conversación específica, ordenados por fecha de creación.
    """
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return messages



def add_message_and_generate_response(db: Session, conversation_id: int, user_id: int, message_text: str = None, image_id: int = None) -> Tuple[Message, Message]:
    """
    Añade un mensaje del usuario a una conversación existente y genera una respuesta.
    Se puede incluir texto, imagen o ambos en el mensaje.
    """

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")


    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta conversación")


    user_msg = add_user_message(db, conversation_id, message_text, image_id)

    image_base64: Optional[str] = None
    image_mime_type: Optional[str] = None

    if image_id:
         image = get_image_by_id(image_id,db)
         if image:
             image_base64, image_mime_type = prepare_image_for_google_ai(image)


    context = ""
    subject_info = None
    try:
        if conversation.subject_id:
            # Obtener información completa de la asignatura incluyendo el resumen
            subject = db.query(Subject).filter(Subject.id == conversation.subject_id).first()
            if subject:
                subject_info = {
                    "id": subject.id,
                    "name": subject.name,
                    "code": subject.code,
                    "description": subject.description,
                    "summary": subject.summary
                }
            
            context = get_conversation_context(
                db=db,
                message_text=message_text,
                subject_id=conversation.subject_id
            )

        
        conversation_history = get_conversation_history(db, conversation_id)
        
        bot_response = generate_google_ai_response(
            user_question=message_text,
            context=context,
            conversation_history=conversation_history,
            image_base64=image_base64,
            image_mime_type=image_mime_type,
            asignatura=subject_info,
            user_id=str(user_id),
            conversation_id=conversation_id
        )
    except Exception as e:
        print(f"Error generating AI response: {e}")
        bot_response = "Lo siento, hubo un error al generar la respuesta."

    
    bot_msg = add_bot_message(db, conversation_id, bot_response)
    
    return user_msg, bot_msg