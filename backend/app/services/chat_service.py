"""
Servicio de Chat - Capa superior
Este servicio maneja la lógica de chat y puede usar todos los servicios de capas inferiores.
"""
from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.models import Conversation, Message, User
from app.services.api_service import generate_ai_response
from app.services.vector_service import (
    create_conversation as create_conversation_in_vector, 
    get_conversation_context,
    get_conversation_history,
    add_user_message,
    add_bot_message
)

def process_message(db: Session, conversation_id: int, message_text: str) -> str:
    """
    Procesa un mensaje del usuario y genera una respuesta con AI.
    """
    # Obtener la conversación
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Añadir mensaje del usuario
    add_user_message(db, conversation_id, message_text)
    
    # Obtener contexto de documento
    context = get_conversation_context(db, conversation.document_id, message_text)
    
    # Obtener historial de conversación
    conversation_history = get_conversation_history(db, conversation_id)
    
    # Generar respuesta con AI
    bot_response = generate_ai_response(message_text, context, conversation_history)
    
    # Añadir mensaje del bot
    add_bot_message(db, conversation_id, bot_response)
    
    return bot_response

def get_conversations_by_user_role(db: Session, user_id: int, role: str) -> List[Conversation]:
    """
    Obtiene todas las conversaciones asociadas a un usuario según su rol.
    """
    query = db.query(Conversation)
    
    if role == "student":
        query = query.filter(
            and_(Conversation.user_id == user_id, Conversation.user_role == "student")
        )
    elif role == "teacher":
        # Los profesores pueden ver sus propias conversaciones y las de sus asignaturas
        teacher = db.query(User).filter(
            and_(User.id == user_id, User.role == "teacher")
        ).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Profesor no encontrado")
            
        subject_ids = [subject.id for subject in teacher.teaching_subjects]
        query = query.filter(
            or_(
                and_(Conversation.user_id == user_id, Conversation.user_role == "teacher"),
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
            "document_id": conv.document_id,
            "user_id": conv.user_id,
            "user_role": conv.user_role,
            "subject_id": conv.subject_id,
            "created_at": conv.created_at,
            "document_title": conv.document.title if conv.document else None,
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

def create_conversation(db: Session, document_id: int, user_id: int, user_type: str, subject_id: int) -> Conversation:
    """
    Crea una nueva conversación utilizando el servicio vector.
    """
    return create_conversation_in_vector(db, document_id, user_id, user_type, subject_id)

def generate_conversation(db: Session, document_id: int, user_id: int, user_type: str, subject_id: int, initial_message_text: str = None) -> Tuple[str, Conversation]:
    """
    Crea una nueva conversación y genera una respuesta inicial si se proporciona un mensaje.
    """
    # Crear la conversación
    new_conversation = create_conversation(db, document_id, user_id, user_type, subject_id)
    
    # Si no hay mensaje inicial, devolver conversación vacía
    if not initial_message_text:
        return "", new_conversation
    
    # Procesar mensaje y generar respuesta
    bot_response = process_message(db, new_conversation.id, initial_message_text)
    
    return bot_response, new_conversation

def add_message_and_generate_response(db: Session, conversation_id: int, user_id: int, user_type: str, message_text: str) -> Tuple[Message, Message]:
    """
    Añade un mensaje del usuario a una conversación existente y genera una respuesta.
    """
    # Verificar que la conversación existe
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Verificar que el usuario tiene permisos para esta conversación
    if conversation.user_id != user_id or conversation.user_role != user_type:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta conversación")
    
    # Añadir mensaje del usuario
    user_msg = add_user_message(db, conversation_id, message_text)
    
    # Obtener contexto de documento
    context = get_conversation_context(db, conversation.document_id, message_text)
    
    # Obtener historial de conversación
    conversation_history = get_conversation_history(db, conversation_id)
    
    try:
        # Generar respuesta con AI
        bot_response = generate_ai_response(message_text, context, conversation_history)
    except Exception as e:
        print(f"Error generating AI response: {e}")
        bot_response = "Lo siento, hubo un error al generar la respuesta."
    
    # Añadir mensaje del bot
    bot_msg = add_bot_message(db, conversation_id, bot_response)
    
    return user_msg, bot_msg