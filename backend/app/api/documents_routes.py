from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from ..models.models import Teacher
from ..core.auth import get_current_active_teacher
from ..core.database import get_db
from ..services.document_service import save_document, list_documents
from ..models.schemas import DocumentOut, DocumentCreate
from typing import List

documents_routes = APIRouter()

@documents_routes.post("/upload")
async def upload_document(
    title: str = Form(...),  
    description: str = Form(None),
    pdf_file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_active_teacher)
):
    """
    Sube un documento PDF, guarda los metadatos en PostgreSQL y almacena el embedding en Pinecone.
    """
    
    document_data = DocumentCreate(title=title, description=description, teacher_id=current_teacher.id)
    document = save_document(db, pdf_file, document_data)
    return {"message": "Documento subido exitosamente", "document_id": document.id}

@documents_routes.get("/{teacher_id}", response_model=List[DocumentOut])
def get_documents(
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_active_teacher)
):
    """
    Obtiene los documentos de un profesor.
    """

    return list_documents(db, current_teacher.teacher_id)

