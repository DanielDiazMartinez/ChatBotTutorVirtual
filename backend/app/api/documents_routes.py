from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.auth import require_role
from ..services.document_service import save_document, list_documents
from ..models.schemas import DocumentOut, DocumentCreate

documents_routes = APIRouter()

@documents_routes.post("/upload")
async def upload_document(
    title: str = Form(...),  
    description: str = Form(None),
    pdf_file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Sube un documento PDF, guarda los metadatos en PostgreSQL.
    Accesible para profesores y administradores.
    """
    document_data = DocumentCreate(title=title, description=description)
    document = save_document(db, pdf_file, document_data)
    return {"message": "Documento subido exitosamente", "document_id": document.id}

@documents_routes.get("/{document_id}", response_model=List[DocumentOut])
def get_documents(
    document_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """
    Obtiene los documentos.
    Accesible para profesores, estudiantes y administradores.
    """
    return list_documents(db, document_id)

