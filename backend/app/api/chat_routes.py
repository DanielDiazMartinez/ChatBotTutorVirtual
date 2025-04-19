from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.models import Student, Teacher
from ..services.chat_service import delete_conversation, get_conversations_by_student
from ..core.database import get_db
from ..services.vector_service import generate_conversation
from ..models.schemas import ConversationCreate, ConversationOut, ConversationWithResponse, MessageCreate

chat_routes  = APIRouter()

@chat_routes.post("/conversation", response_model=ConversationWithResponse)
def create_conversation(
    conversation_data: ConversationCreate, # Asumiendo que tienes este schema Pydantic para la entrada
    db: Session = Depends(get_db)
):
    
    user_id = 1 #TODO: Cambiar por el ID del estudiante autenticado
    user_type = "student"  
    

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
def get_student_conversations(student_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todas las conversaciones de un alumno específico.
    """
    conversations = get_conversations_by_student(student_id, db)
    if not conversations:
        raise HTTPException(status_code=404, detail="No se encontraron conversaciones para este estudiante.")
    return conversations

@chat_routes.delete("/conversation/{conversation_id}")
def delete_conv(conversation_id: int, db: Session = Depends(get_db)):
    """
    Elimina una conversación específica.
    """
    return delete_conversation(conversation_id, db)