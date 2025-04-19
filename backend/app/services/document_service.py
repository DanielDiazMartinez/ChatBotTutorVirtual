
import os
from sqlalchemy.orm import Session
from app.models.models import Conversation, Document, Message, Student
from app.models.schemas import  ConversationCreate, DocumentCreate, MessageCreate
from fastapi import  HTTPException, UploadFile
from app.utils.document_utils import extract_text_from_pdf
from app.core.config import settings
from app.services.groq_service import generate_groq_response
from app.services.vector_service import insert_document_chunks



def save_document(db: Session,pdf_file: UploadFile,document: DocumentCreate):
    """
    Guarda el documento en PostgreSQL.
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
    
    insert_document_chunks(db, new_document.id, content)
        
    return new_document

def list_documents(db: Session, teacher_id: int):
    """
    Obtiene los documentos de un profesor.
    """
    return db.query(Document).filter(Document.teacher_id == teacher_id).all()
