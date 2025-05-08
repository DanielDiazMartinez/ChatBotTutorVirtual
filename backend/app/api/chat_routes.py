from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Tuple
from sqlalchemy.orm import Session

from ..models.models import DocumentChunk, Student, Teacher
from ..services.chat_service import delete_conversation, get_conversation_by_id, get_conversations_by_student
from ..core.database import get_db
from ..core.auth import get_current_active_student, get_current_active_teacher, require_role
from ..services.vector_service import add_message_and_generate_response, generate_conversation, get_context, search_similar_chunks
from ..models.schemas import ConversationCreate, ConversationOut, ConversationWithResponse, DocumentChunkOut, MessageCreate, MessageOut, MessagePairOut

chat_routes = APIRouter()

@chat_routes.post("/conversation", response_model=ConversationWithResponse)
async def create_conversation(
    conversation_data: ConversationCreate, 
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher] = Depends(require_role(["student", "teacher"]))
):
    user_id = current_user.id
    user_type = current_user.role

    student = db.query(Student).filter(Student.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Estudiante con ID {user_id} no encontrado")
    
    bot_response_str, conversation_obj = generate_conversation(
        db=db,
        document_id=conversation_data.document_id,
        user_id=user_id,
        user_type=user_type,
        initial_message_text=conversation_data.text
    )

    return {
        "conversation": conversation_obj,
        "bot_response": bot_response_str 
    }


@chat_routes.get("/conversations/student/{student_id}", response_model=list[ConversationOut])
async def get_student_conversations(
    student_id: int, 
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_active_student)
):
    """
    Obtiene todas las conversaciones de un alumno específico.
    """
    conversations = get_conversations_by_student(student_id, db)
    if not conversations:
        raise HTTPException(status_code=404, detail="No se encontraron conversaciones para este estudiante.")
    return conversations

@chat_routes.get("/conversation/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: int, 
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher] = Depends(require_role(["student", "teacher"]))
):
    """
    Obtiene una conversación específica.
    """
    conversation = get_conversation_by_id(conversation_id, db)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada.")
    
    return conversation

@chat_routes.delete("/conversation/{conversation_id}")
async def delete_conv(
    conversation_id: int, 
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher] = Depends(require_role(["student", "teacher"]))
):
    """
    Elimina una conversación específica.
    """
    return delete_conversation(conversation_id, db)

@chat_routes.post("/c/{conversation_id}", response_model=MessagePairOut)
async def add_message_to_conversation(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher] = Depends(require_role(["student", "teacher"]))
):
    user_id = current_user.id
    user_type = current_user.role

    try:
        user_msg_obj, bot_msg_obj = add_message_and_generate_response(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
            user_type=user_type,
            message_text=message_data.text
        )
        return {
            "user_message": user_msg_obj,
            "bot_message": bot_msg_obj
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error procesando el mensaje")

@chat_routes.post("/context/{document_id}", response_model=List[DocumentChunkOut])
async def get_context_for_question(
    document_id: int, 
    db: Session = Depends(get_db), 
    message_data: MessageCreate = None,
    current_user: Union[Student, Teacher] = Depends(require_role(["student", "teacher"]))
):
    """
    Obtiene el contexto de un documento específico.
    Devuelve una lista de DocumentChunkOut objetos.
    """

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

    return context_out
