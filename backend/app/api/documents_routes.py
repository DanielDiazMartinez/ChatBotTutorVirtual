from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.models import User
from ..core.database import get_db
from ..core.auth import get_current_user, require_role
from ..services.document_service import save_document, list_documents
from ..models.schemas import APIResponse, DocumentOut, DocumentCreate

documents_routes = APIRouter()

@documents_routes.post("/upload", response_model=APIResponse)
async def upload_document(
    title: str = Form(...),  
    description: str = Form(None),
    pdf_file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Sube un documento PDF, guarda los metadatos en PostgreSQL.
    Accesible para profesores y administradores.
    """
    document_data = DocumentCreate(title=title, description=description, user_id=current_user.id)
    document = save_document(db, pdf_file, document_data)
    return {
        "data": {"document_id": document.id},
        "message": "Documento subido exitosamente",
        "status": 200
    }

@documents_routes.get("/{document_id}", response_model=APIResponse)
def get_documents(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """
    Obtiene los documentos.
    Accesible para profesores, estudiantes y administradores.
    """
    documents = list_documents(db, document_id)
    return {
        "data": documents,
        "message": "Documentos obtenidos correctamente",
        "status": 200
    }

