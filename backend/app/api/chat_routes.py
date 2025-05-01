from typing import  List 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from ..models.models import Student, Teacher
from ..models.schemas import (
    ConversationCreateRequest, 
    ConversationOut,
    MessageCreate,
    MessagePairOut
)

from ..services.chat_service import (
    delete_conversation,
    get_conversation_by_id,
    get_conversations_by_student
)
from ..core.database import get_db
from ..services.chat_service import (
    add_message_and_generate_response,
    create_conversation 
)


chat_routes = APIRouter()


@chat_routes.post("/conversation", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_new_conversation(
    conversation_data: ConversationCreateRequest, # Usar el nuevo schema
    db: Session = Depends(get_db)
):
    """
    Crea una nueva conversación asociada a un documento y un usuario.
    """
    # TODO: Reemplazar con lógica de autenticación real para obtener user_id y user_type
    user_id = 1
    user_type = "student"

    if user_type == "student":
        user = db.get(Student, user_id)
        if not user:
             raise HTTPException(status_code=404, detail=f"Estudiante con ID {user_id} no encontrado")
    elif user_type == "teacher":
         user = db.get(Teacher, user_id)
         if not user:
             raise HTTPException(status_code=404, detail=f"Profesor con ID {user_id} no encontrado")
   
    try:
      
        conversation_obj = create_conversation(
            db=db,
            document_id=conversation_data.document_id,
            user_id=user_id,
            user_type=user_type
        )
       
        return conversation_obj
    except HTTPException as e:
      
        raise e
    except Exception as e:
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al crear la conversación")


@chat_routes.post("/conversations/{conversation_id}/messages", response_model=MessagePairOut)
def add_message_to_conversation(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Añade un mensaje de usuario a una conversación existente y obtiene la respuesta del bot.
    """
    # TODO: Reemplazar con lógica de autenticación real
    user_id = 1
    user_type = "student"

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
    except ValueError as e:
        
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al procesar el mensaje")




@chat_routes.get("/conversations/student/{student_id}", response_model=List[ConversationOut])
def get_student_conversations(student_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todas las conversaciones de un alumno específico.
    """
  
    conversations = get_conversations_by_student(student_id, db)
   
    return conversations

@chat_routes.get("/conversation/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una conversación específica por su ID.
    """
    conversation = get_conversation_by_id(conversation_id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada.")
    return conversation

@chat_routes.delete("/conversation/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conv(conversation_id: int, db: Session = Depends(get_db)):
    """
    Elimina una conversación específica y sus mensajes asociados.
    Devuelve 204 No Content si tiene éxito.
    """
    
    deleted_ok = delete_conversation(conversation_id, db)
    if not deleted_ok:
         raise HTTPException(status_code=404, detail="Conversación no encontrada para eliminar.")
   
    return None 