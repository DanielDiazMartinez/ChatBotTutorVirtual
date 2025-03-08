from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.chat_service import delete_conversation, get_conversations_by_student
from ..core.database import get_db
from ..services.document_service import add_message_to_conversation, generate_conversation
from ..models.schemas import ConversationCreate, ConversationOut, MessageCreate

chat_routes  = APIRouter()

@chat_routes.post("/conversation", response_model=ConversationCreate)
def create_conversation(conversaction_data: ConversationCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva pregunta y la asocia con un estudiante y un documento.
    """
    return generate_conversation(conversaction_data, db)

@chat_routes.post("/{conversation_id}/message", response_model=MessageCreate)
def post_message(conversation_id: int, message_data: MessageCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo mensaje y lo asocia con una conversación.
    """
    message_data.is_bot = False
    
    return add_message_to_conversation(conversation_id,message_data, db)

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