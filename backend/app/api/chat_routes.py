from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Tuple
from sqlalchemy.orm import Session

from ..models.models import DocumentChunk, User
from ..services.chat_service import delete_conversation, get_conversation_by_id, get_conversations_by_user_role, get_current_user_conversations
from ..core.database import get_db
from ..core.auth import require_role, get_current_user
from ..services.vector_service import (
    add_message_and_generate_response, 
    generate_conversation, 
    get_context, 
    search_similar_chunks
)
from ..models.schemas import (
    APIResponse,
    ConversationCreate, 
    ConversationOut, 
    ConversationWithResponse, 
    DocumentChunkOut, 
    MessageCreate, 
    MessageOut, 
    MessagePairOut
)

chat_routes = APIRouter()

@chat_routes.post("/conversation", response_model=APIResponse)
async def create_conversation(
    conversation_data: ConversationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una nueva conversación"""
    bot_response_str, conversation_obj = generate_conversation(
        db=db,
        document_id=conversation_data.document_id,
        user_id=current_user.id,
        user_type=current_user.role,
        initial_message_text=conversation_data.text
    )

    return {
        "data": {
            "conversation": conversation_obj,
            "bot_response": bot_response_str
        },
        "message": "Conversación creada correctamente",
        "status": 200 
    }

@chat_routes.get("/me/conversations", response_model=APIResponse)
async def get_my_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todas las conversaciones del usuario actualmente autenticado"""
    conversations = get_current_user_conversations(current_user.id, current_user.role, db)
    
    return {
        "data": conversations,
        "message": "Conversaciones obtenidas correctamente",
        "status": 200
    }

@chat_routes.get("/conversations/{user_id}", response_model=APIResponse)
async def get_user_conversations(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener conversaciones de un usuario"""
    # Verificar que el usuario actual puede acceder a estas conversaciones
    if current_user.id != user_id and current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para ver las conversaciones de este usuario"
        )
        
    conversations = get_conversations_by_user_role(user_id, current_user.role, db)
    if not conversations:
        return {
            "data": [],
            "message": "No se encontraron conversaciones para este usuario",
            "status": 200
        }
    return {
        "data": conversations,
        "message": "Conversaciones obtenidas correctamente",
        "status": 200
    }

@chat_routes.get("/conversation/{conversation_id}", response_model=APIResponse)
async def get_conversation(
    conversation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener una conversación específica"""
    conversation = get_conversation_by_id(conversation_id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    # Verificar que el usuario actual puede acceder a esta conversación
    if current_user.role == "student" and conversation.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta conversación")
    elif current_user.role == "teacher":
        # Los profesores pueden ver las conversaciones de las asignaturas que imparten
        if not (conversation.teacher_id == current_user.id or 
                (conversation.subject_id and conversation.subject_id in 
                 [s.id for s in current_user.teaching_subjects])):
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta conversación")
        
    return {
        "data": conversation,
        "message": "Conversación obtenida correctamente",
        "status": 200
    }

@chat_routes.delete("/conversation/{conversation_id}", response_model=APIResponse)
async def delete_conv(
    conversation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar una conversación"""
    conversation = get_conversation_by_id(conversation_id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    # Verificar que el usuario actual puede eliminar esta conversación
    if current_user.role == "student":
        if conversation.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta conversación")
    elif current_user.role == "teacher":
        if conversation.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta conversación")
            
    delete_conversation(conversation_id, db)
    return {
        "data": None,
        "message": "Conversación eliminada correctamente",
        "status": 200
    }

@chat_routes.post("/c/{conversation_id}", response_model=APIResponse)
async def add_message_to_conversation(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Añadir mensaje a una conversación"""
    try:
        user_msg_obj, bot_msg_obj = add_message_and_generate_response(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            user_type=current_user.role,
            message_text=message_data.text
        )
        return {
            "data": {
                "user_message": user_msg_obj,
                "bot_message": bot_msg_obj
            },
            "message": "Mensaje añadido correctamente",
            "status": 200
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error procesando el mensaje")

@chat_routes.post("/context/{document_id}", response_model=APIResponse)
async def get_context_for_question(
    document_id: int, 
    db: Session = Depends(get_db), 
    message_data: MessageCreate = None,
    current_user: User = Depends(get_current_user)
):
    """Obtener contexto para una pregunta"""
    if message_data is None or message_data.text is None:
        raise HTTPException(status_code=400, detail="Message text is required")

    similar_chunks: List[Tuple[DocumentChunk, float]] = get_context(
        db=db,
        document_id=document_id,
        message_text=message_data.text
    )

    context_out = [
        DocumentChunkOut.model_validate(chunk) for chunk, _ in similar_chunks
    ]

    return {
        "data": context_out,
        "message": "Contexto obtenido correctamente",
        "status": 200
    }
