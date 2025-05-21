from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.models import Conversation, Message, User
from app.services.groq_service import generate_groq_response
from app.utils.document_utils import get_embedding_for_query
from app.services.document_service import document_exists
def process_message(conversation_id: int, message_text: str, user: User, db: Session) -> str:
    """
    Procesa un mensaje del usuario y genera una respuesta con Groq.
    """
    from app.services.vector_service import search_similar_chunks
    
    message_embedding = get_embedding_for_query(message_text)
    context = search_similar_chunks(message_embedding, conversation_id, db) 
    
    bot_response = generate_groq_response(message_text, context)
    
    # Crear los mensajes del usuario y del bot
    user_message = Message(
        conversation_id=conversation_id, 
        text=message_text, 
        is_bot=False,
        embedding=message_embedding
    )
    bot_message = Message(
        conversation_id=conversation_id, 
        text=bot_response, 
        is_bot=True,
        embedding=get_embedding_for_query(bot_response)
    )
    
    db.add_all([user_message, bot_message])
    db.commit()

    return bot_response

def get_conversations_by_user_role(user_id: int, role: str, db: Session) -> List[Conversation]:
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

def get_conversation_by_id(conversation_id: int, db: Session) -> Optional[Conversation]:
    """
    Obtiene una conversación específica por su ID.
    """
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def delete_conversation(conversation_id: int, db: Session) -> None:
    """
    Elimina una conversación y todos sus mensajes asociados.
    """
    conversation = get_conversation_by_id(conversation_id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    db.delete(conversation)  # Esto eliminará también los mensajes por la relación cascade
    db.commit()

def get_current_user_conversations(user_id: int, role: str, db: Session, subject_id: Optional[int] = None) -> List[dict]:
    """
    Obtiene todas las conversaciones del usuario actualmente autenticado y las formatea como diccionarios.
    Si se proporciona subject_id, filtra las conversaciones por esa asignatura.
    """
    conversations = get_conversations_by_user_role(user_id, role, db)
    
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

def get_conversation_messages(conversation_id: int, db: Session) -> List[Message]:
    """
    Obtiene todos los mensajes de una conversación específica, ordenados por fecha de creación.
    """
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return messages

def create_conversation(
    db: Session,
    document_id: int,
    user_id: int,
    user_type: str,  # "teacher" o "student"
    subject_id: int
) -> Conversation:
    """
    Crea una nueva conversación.
    """

    
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