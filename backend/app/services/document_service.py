
import os
from sqlalchemy.orm import Session
from app.models.models import Conversation, Document, Message, Student
from app.models.schemas import  ConversationCreate, DocumentCreate, MessageCreate
from fastapi import Depends, HTTPException, UploadFile
from app.utils.document_utils import extract_text_from_pdf, insert_document_embeddings
from app.core.config import settings


def save_document(db: Session,pdf_file: UploadFile,document: DocumentCreate):
    """
    Guarda el documento en PostgreSQL y envía su embedding a Pinecone.
    """
   
    if not pdf_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    subfolder_path = os.path.join(settings.UPLOAD_FOLDER, str(document.teacher_id))

    os.makedirs(subfolder_path, exist_ok=True)
    
    file_path = os.path.join(subfolder_path, pdf_file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(pdf_file.file.read())
    
    new_document = Document(
        title=document.title,
        file_path=file_path,
        description=document.description,
        teacher_id=document.teacher_id
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    content = extract_text_from_pdf(pdf_file)

    if not content:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")
   
    insert_document_embeddings(new_document.id, new_document.teacher_id, new_document.title, new_document.description, content)

    return new_document

def list_documents(db: Session, teacher_id: int):
    """
    Obtiene los documentos de un profesor.
    """
    return db.query(Document).filter(Document.teacher_id == teacher_id).all()

def generate_conversation(conversation_data: ConversationCreate, db: Session):
    """
    Crea una nueva conversación y la asocia con un estudiante.
    """
    student = db.query(Student).filter(Student.id == conversation_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    document = db.query(Document).filter(Document.id == conversation_data.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    new_conversation = Conversation(student_id=conversation_data.student_id, document_id=conversation_data.document_id)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return new_conversation

def add_message_to_conversation(conversation_id: int, message_data: MessageCreate, db: Session ):
    """
    Añade un mensaje (pregunta o respuesta) a una conversación.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    new_message = Message(
        text=message_data.text,
        is_bot=message_data.is_bot,
        conversation_id=conversation_id
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message
