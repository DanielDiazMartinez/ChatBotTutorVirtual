
import os
from sqlalchemy.orm import Session
from app.models.models import Document
from app.models.schemas import  DocumentBase
from fastapi import HTTPException, UploadFile
from app.core.pinecone import get_pinecone_index
from app.utils.document_utils import extract_text_from_pdf, generate_embedding, insert_document_embeddings
from app.core.config import settings


def save_document(db: Session,pdf_file: UploadFile,document: DocumentBase):
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