from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.document_service import save_document, list_documents
from ..models.schemas import DocumentOut, DocumentCreate
from typing import List

documents_routes = APIRouter()

@documents_routes.post("/upload")
async def upload_document(
    title: str = Form(...),  
    description: str = Form(None),
    teacher_id: int = Form(...),
    pdf_file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Sube un documento PDF, guarda los metadatos en PostgreSQL y almacena el embedding en Pinecone.
    """
    
    document_data = DocumentCreate(title=title, description=description, teacher_id=teacher_id)
    document = save_document(db, pdf_file, document_data)
    return {"message": "Documento subido exitosamente", "document_id": document.id}

@documents_routes.get("/{teacher_id}",response_model=List[DocumentOut])
def get_documents( teacher_id: int,db: Session = Depends(get_db)):
    """
    Obtiene los documentos de un profesor.
    """
    return list_documents(db, teacher_id)