import logging
from typing import List, Tuple, Optional

from fastapi import HTTPException
from sqlalchemy import select, literal_column
from sqlalchemy.orm import Session

from app.models.models import (
    Document,
    DocumentChunk,
    CosineDistance,
    EuclideanDistance,
    InnerProduct,
    Conversation,
    Message,
    Student,
    Teacher
)
from app.services.document_service import search_similar_chunks
from app.services.groq_service import generate_groq_response
from app.utils.document_utils import chunk_text, generate_embedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_student_question( conversation_id: int, document_id: int, question_text: str,db: Session):
    """
    Maneja la pregunta del estudiante, busca contexto y genera una respuesta con Groq.
    """
    
    context = any
    

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
    return db.query(Conversation).filter(Conversation.student_id == student_id).all()#TODO: Mover a otro servicio

def get_conversation_by_id(conversation_id: int, db: Session):
    """
    Obtiene una conversación específica por su ID.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    return conversation

def get_all_conversations(db: Session):
    """
    Obtiene todas las conversaciones en la base de datos.
    """
    return db.query(Conversation).all()#TODO: Mover a otro servicio

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

def create_conversation(
    db: Session,
    document_id: int,
    user_id: int,
    user_type: str
) -> Conversation:
    """
    Crea y guarda una nueva conversación asociada a un documento y un usuario.

    Args:
        db: Sesión de base de datos SQLAlchemy.
        document_id: ID del documento relacionado.
        user_id: ID del usuario que inicia la conversación.
        user_type: Tipo de usuario ('teacher' o 'student').

    Returns:
        El objeto Conversation recién creado.

    Raises:
        HTTPException: Si el documento o el usuario no se encuentran,
                       o si el tipo de usuario es inválido.
    """
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    conversation_data = {"document_id": document_id}
    if user_type == "student":
        student = db.get(Student, user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        conversation_data["student_id"] = user_id
    elif user_type == "teacher":
        teacher = db.get(Teacher, user_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Profesor no encontrado")
        conversation_data["teacher_id"] = user_id
    else:
        raise HTTPException(status_code=400, detail="Tipo de usuario inválido. Debe ser 'teacher' o 'student'")

    new_conversation = Conversation(**conversation_data)

    try:
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        logger.info(f"Conversación {new_conversation.id} creada para {user_type} {user_id}.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear conversación para {user_type} {user_id} y doc {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al crear la conversación.") from e

    return new_conversation


def add_message_and_generate_response(
    db: Session,
    conversation_id: int,
    user_id: int,
    user_type: str,
    message_text: str
) -> Tuple[Message, Message]:
    """
    Añade un mensaje de usuario a una conversación existente, busca contexto,
    genera una respuesta del bot y guarda ambos mensajes.

    Args:
        db: Sesión de base de datos SQLAlchemy.
        conversation_id: ID de la conversación existente.
        user_id: ID del usuario que envía el mensaje.
        user_type: Tipo de usuario ('teacher' o 'student').
        message_text: Texto del mensaje del usuario.

    Returns:
        Una tupla conteniendo el objeto Message del usuario y el objeto Message del bot.

    Raises:
        HTTPException: Si la conversación o el usuario no se encuentran,
                       si el usuario no pertenece a la conversación, o si el tipo
                       de usuario es inválido.
        ValueError: Si no se puede generar el embedding para el mensaje.
    """
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    if not conversation.document_id:
         raise HTTPException(status_code=500, detail="La conversación no está asociada a ningún documento.")

    if user_type == "student":
        if not conversation.student_id == user_id:
             raise HTTPException(status_code=403, detail="El estudiante no pertenece a esta conversación")
    elif user_type == "teacher":
         if not conversation.teacher_id == user_id:
             raise HTTPException(status_code=403, detail="El profesor no pertenece a esta conversación")
    else:
        raise HTTPException(status_code=400, detail="Tipo de usuario inválido.")

    user_message: Optional[Message] = None
    bot_message: Optional[Message] = None

    try:
        question_embedding = generate_embedding(message_text)
        if question_embedding is None:
            raise ValueError("No se pudo generar embedding para el mensaje del usuario.")

        user_message = Message(
            text=message_text,
            is_bot=False,
            conversation_id=conversation_id,
            embedding=question_embedding
        )
        db.add(user_message)
        db.flush()
        db.refresh(user_message)

        similar_chunks = search_similar_chunks(
            db,
            question_embedding,
            conversation.document_id
        )
        similarity_threshold = 0.4
        context = " ".join([
            chunk.content for chunk, score in similar_chunks
            if score > similarity_threshold
        ])

        try:
            response_text = generate_groq_response(message_text, context)
            logger.info(f"Respuesta generada por Groq para conversación {conversation_id}")
        except Exception as e:
            logger.error(f"Error al llamar a generate_groq_response: {e}")
            response_text = "Lo siento, ha ocurrido un problema al generar la respuesta."

        response_embedding = generate_embedding(response_text)
        if response_embedding is None:
             logger.warning(f"No se pudo generar embedding para la respuesta del bot en conversación {conversation_id}")

        bot_message = Message(
            text=response_text,
            is_bot=True,
            conversation_id=conversation_id,
            embedding=response_embedding
        )
        db.add(bot_message)
        db.commit()
        db.refresh(bot_message)

        logger.info(f"Mensaje añadido y respuesta generada para conversación {conversation_id}.")

        if not user_message or not bot_message:
             raise RuntimeError("Error inesperado: Faltan objetos de mensaje después del commit.")

        return user_message, bot_message

    except Exception as e:
        db.rollback()
        logger.error(f"Error al añadir mensaje o generar respuesta para conv {conversation_id}: {e}")
        if isinstance(e, HTTPException):
            raise e
        if isinstance(e, ValueError): # Relanzar ValueError específico del embedding
             raise HTTPException(status_code=400, detail=str(e)) from e
        raise HTTPException(status_code=500, detail="Error interno al procesar el mensaje.") from e