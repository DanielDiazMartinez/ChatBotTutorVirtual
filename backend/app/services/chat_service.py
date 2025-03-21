
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.pinecone_service import retrieve_context
from app.models.models import Conversation, Message
from app.services.groq_service import generate_groq_response


def process_student_question( conversation_id: int, document_id: int, question_text: str,db: Session):
    """
    Maneja la pregunta del estudiante, busca contexto en Pinecone y genera una respuesta con Groq.
    """

    context = retrieve_context(conversation_id, document_id, question_text)


    bot_response = generate_groq_response(question_text, context)

 
    question = Message(conversation_id=conversation_id, text=question_text, is_bot=False)
    response = Message(conversation_id=conversation_id, text=bot_response, is_bot=True)

    db.add_all([question, response])
    db.commit()

    return bot_response

def get_conversations_by_student(student_id: int, db: Session):
    """
    Obtiene todas las conversaciones asociadas a un estudiante.
    """
    return db.query(Conversation).filter(Conversation.student_id == student_id).all()

def get_all_conversations(db: Session):
    """
    Obtiene todas las conversaciones en la base de datos.
    """
    return db.query(Conversation).all()

def delete_conversation(conversation_id: int, db: Session):
    """
    Elimina una conversación específica de la base de datos.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    db.delete(conversation)
    db.commit()
    return {"message": "Conversación eliminada correctamente"}