from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.models import Student, Teacher
from ..services.chat_service import delete_conversation, get_conversation_by_id, get_conversations_by_student
from ..core.database import get_db
from ..services.vector_service import add_message_and_generate_response, generate_conversation
from ..models.schemas import ConversationCreate, ConversationOut, ConversationWithResponse, MessageCreate, MessageOut, MessagePairOut

chat_routes  = APIRouter()

@chat_routes.post("/conversation", response_model=ConversationWithResponse)
def create_conversation(
    conversation_data: ConversationCreate, 
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

@chat_routes.get("/conversation/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una conversación específica.
    """

    conversation = get_conversation_by_id(conversation_id, db)

    if not conversation:

        raise HTTPException(status_code=404, detail="Conversación no encontrada.")
    
    return conversation

@chat_routes.delete("/conversation/{conversation_id}")
def delete_conv(conversation_id: int, db: Session = Depends(get_db)):
    """
    Elimina una conversación específica.
    """
    return delete_conversation(conversation_id, db)

@chat_routes.post("/c/{conversation_id}", response_model=MessagePairOut) # Usa el nuevo response_model
def add_message_to_conversation(
    conversation_id: int, # ID de la conversación
    document_id: int, # ID del documento
    message_data: MessageCreate,    # El cuerpo de la petición es el nuevo mensaje
    db: Session = Depends(get_db)
):
    user_id = 1 # TODO: Cambiar por el ID del estudiante autenticado
    user_type = "student" # TODO: Cambiar por el tipo de usuario autenticado

    try:
       
        user_msg_obj, bot_msg_obj = add_message_and_generate_response(
            db=db,
            conversation_id=conversation_id,
            document_id=document_id, 
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

