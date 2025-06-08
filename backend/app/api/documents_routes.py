from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.models.models import User, Subject
from ..core.database import get_db
from ..core.auth import get_current_user, require_role
from ..services.document_service import save_document, list_documents, list_all_documents, delete_document, get_documents_by_topic_id, get_document_by_id
from ..services.summary_service import generate_document_summary_by_id, generate_subject_summary, update_subject_summary
from ..models.schemas import APIResponse, DocumentOut, DocumentCreate

documents_routes = APIRouter()

def validate_subject_access(current_user: User, subject_id: int, db: Session):
    """Valida que el usuario tenga acceso a la asignatura"""
    # Los administradores tienen acceso a todas las asignaturas
    if current_user.role == "admin":
        return True
    
    # Para profesores, verificar que estén asignados a la asignatura
    if current_user.role == "teacher":
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Asignatura no encontrada")
        
        # Verificar si el profesor está asignado a esta asignatura
        is_assigned = any(user.id == current_user.id for user in subject.users)
        if not is_assigned:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para acceder a esta asignatura"
            )
    
    return True

@documents_routes.post("/upload", response_model=APIResponse)
async def upload_document(
    title: str = Form(...),  
    description: str = Form(None),
    subject_id: int = Form(...),  # Ahora es obligatorio
    topic_id: int = Form(None),  # Opcional
    pdf_file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Sube un documento PDF, guarda los metadatos en PostgreSQL.
    Accesible para profesores y administradores.
    Requiere subject_id (obligatorio) y opcionalmente topic_id.
    """
    document_data = DocumentCreate(
        title=title, 
        description=description, 
        user_id=current_user.id, 
        subject_id=subject_id,  
        topic_id=topic_id  
    )
    document = save_document(db, pdf_file, document_data)
    return {
        "data": {"document_id": document.id},
        "message": "Documento subido exitosamente",
        "status": 200
    }

@documents_routes.get("/list", response_model=APIResponse)
def list_all_documents_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """
    Lista todos los documentos.
    Para profesores: muestra solo sus propios documentos.
    Para administradores: muestra todos los documentos.
    Para estudiantes: muestra solo los documentos a los que tienen acceso.
    """
    is_admin = current_user.role == "admin"
    documents = list_all_documents(db, current_user.id, is_admin)
    return {
        "data": documents,
        "message": "Documentos listados correctamente",
        "status": 200
    }

@documents_routes.get("/me", response_model=APIResponse)
def list_current_user_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener todos los documentos del usuario actual.
    Para profesores: devuelve los documentos que ha subido.
    Para estudiantes: devuelve los documentos a los que tiene acceso.
    """
    from app.services.current_user_service import get_current_user_documents
    user_id = current_user.id
    documents = get_current_user_documents(user_id, db)
    
    return {
        "data": documents,
        "message": "Documentos del usuario obtenidos correctamente",
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

@documents_routes.delete("/{document_id}", response_model=APIResponse)
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Elimina un documento, sus chunks asociados y el archivo físico.
    Accesible para profesores (solo sus propios documentos) y administradores (cualquier documento).
    """
    is_admin = current_user.role == "admin"
    result = delete_document(db, document_id, current_user.id, is_admin)
    return {
        "data": result,
        "message": "Documento y archivos asociados eliminados correctamente",
        "status": 200
    }

@documents_routes.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """
    Descarga un documento PDF por su ID.
    Accesible para profesores, estudiantes y administradores.
    Los estudiantes solo pueden descargar documentos a los que tienen acceso a través de sus asignaturas.
    Los profesores pueden descargar sus propios documentos.
    Los administradores pueden descargar cualquier documento.
    """
    # Obtener el documento
    document = get_document_by_id(db, document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Verificar permisos de acceso
    if current_user.role == "admin":
        # Los administradores pueden acceder a cualquier documento
        pass
    elif current_user.role == "teacher":
        # Los profesores solo pueden acceder a sus propios documentos
        if document.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este documento")
    elif current_user.role == "student":
        # Los estudiantes solo pueden acceder a documentos de asignaturas en las que están inscritos
        if document.subject_id:
            user_subjects = [subject.id for subject in current_user.subjects]
            if document.subject_id not in user_subjects:
                raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este documento")
        else:
            raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este documento")
    
    # Verificar que el archivo existe
    if not document.file_path or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")
    
    # Obtener el nombre del archivo original para la descarga
    original_filename = f"{document.title}.pdf"
    
    return FileResponse(
        path=document.file_path,
        filename=original_filename,
        media_type='application/pdf'
    )

# Endpoints para gestión de resúmenes
@documents_routes.post("/{document_id}/summary", response_model=APIResponse)
async def generate_document_summary_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Genera un resumen para un documento específico.
    Accesible para profesores y administradores.
    """
    try:
        summary = await generate_document_summary_by_id(db, document_id)
        return {
            "data": {"summary": summary},
            "message": "Resumen generado exitosamente",
            "status": 200
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@documents_routes.post("/subjects/{subject_id}/summary", response_model=APIResponse)
async def generate_subject_summary_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Genera un resumen de todos los documentos de una asignatura.
    Accesible para profesores y administradores.
    """
    # Validar que el usuario tenga acceso a la asignatura
    validate_subject_access(current_user, subject_id, db)
    
    try:
        summary = await generate_subject_summary(subject_id, db)
        return {
            "data": {"summary": summary},
            "message": "Resumen de asignatura generado exitosamente",
            "status": 200
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@documents_routes.put("/subjects/{subject_id}/summary", response_model=APIResponse)
def update_subject_summary_endpoint(
    subject_id: int,
    new_summary: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Actualiza el resumen de una asignatura con un nuevo texto proporcionado.
    Accesible para profesores y administradores.
    """
    # Validar que el usuario tenga acceso a la asignatura
    validate_subject_access(current_user, subject_id, db)
    
    try:
        success = update_subject_summary(subject_id, db, new_summary)
        if success:
            return {
                "data": {"updated": True},
                "message": "Resumen de asignatura actualizado exitosamente",
                "status": 200
            }
        else:
            raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@documents_routes.get("/topic/{topic_id}", response_model=APIResponse)
def get_documents_by_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """
    Obtiene todos los documentos asociados a un tema específico.
    Accesible para profesores, estudiantes y administradores.
    """
    try:
        documents = get_documents_by_topic_id(db, topic_id, current_user)
        return {
            "data": documents,
            "message": f"Documentos del tema {topic_id} obtenidos exitosamente",
            "status": 200
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

