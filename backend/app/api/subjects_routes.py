from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import require_role
from ..models.schemas import APIResponse, SubjectCreate, SubjectOut, UserIdsRequest, DocumentOut
from ..models.models import User, Document
from ..services.subject_service import (
    add_user_to_subject,
    add_multiple_users_to_subject,
    remove_multiple_users_from_subject,
    create_subject,
    get_subject_by_id,
    get_all_subjects,
    update_subject,
    delete_subject,
    get_subject_documents,
)

subjects_routes = APIRouter()

@subjects_routes.post("/", response_model=APIResponse, status_code=201)
def create_new_subject(
    subject: SubjectCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Crea una nueva asignatura (solo administradores)"""
    subject_created = create_subject(db=db, subject=subject)
    
    # Verificar si hay error en la respuesta
    if "error" in subject_created:
        raise HTTPException(
            status_code=subject_created["status"], 
            detail=subject_created["error"]
        )
        
    return {
        "data": subject_created,
        "message": "Asignatura creada correctamente",
        "status": 201
    }

@subjects_routes.get("/{subject_id}", response_model=APIResponse)
def get_subject(
    subject_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["student", "teacher", "admin"]))
):
    """Obtiene una asignatura por su ID"""
    subject = get_subject_by_id(db=db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return {
        "data": subject,
        "message": "Asignatura obtenida correctamente",
        "status": 200
    }

@subjects_routes.get("/", response_model=APIResponse)
def list_subjects(
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["student", "teacher", "admin"]))
):
    """Lista todas las asignaturas"""
    subjects = get_all_subjects(db=db)
    return {
        "data": subjects,
        "message": "Asignaturas obtenidas correctamente",
        "status": 200
    }

@subjects_routes.put("/{subject_id}", response_model=APIResponse)
def update_subject_route(
    subject_id: int, 
    subject: SubjectCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Actualiza una asignatura (solo administradores)"""
    updated_subject = update_subject(db=db, subject_id=subject_id, subject=subject)
    if not updated_subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return {
        "data": updated_subject,
        "message": "Asignatura actualizada correctamente",
        "status": 200
    }

@subjects_routes.delete("/{subject_id}", response_model=APIResponse)
def delete_subject_route(
    subject_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Elimina una asignatura (solo administradores)"""
    if not delete_subject(db=db, subject_id=subject_id):
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return {
        "data": None,
        "message": "Asignatura eliminada correctamente",
        "status": 200
    }

@subjects_routes.post("/{subject_id}/user/{user_id}", response_model=APIResponse)
def add_user_to_subject_route(
    subject_id: int, 
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Agrega un profesor o estudiante a una asignatura (solo administradores)"""

    if not add_user_to_subject(db=db, subject_id=subject_id, user_id=user_id):
        raise HTTPException(status_code=400, detail="No se pudo agregar el usuario a la asignatura")
    
    return {
        "data": None,
        "message": "Usuario agregado a la asignatura correctamente",
        "status": 200
    }

@subjects_routes.post("/{subject_id}/users", response_model=APIResponse)
def add_multiple_users_to_subject_route(
    subject_id: int,
    users_request: UserIdsRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Agrega múltiples usuarios (profesores o estudiantes) a una asignatura (solo administradores)"""
    
    result = add_multiple_users_to_subject(
        db=db, 
        subject_id=subject_id, 
        user_ids=users_request.user_ids
    )
    
    if not result["success"]:
        status_code = 404 if result.get("error") == "Asignatura no encontrada" else 400
        raise HTTPException(status_code=status_code, detail=result.get("error", "Error al agregar usuarios"))
    
    return {
        "data": {
            "added": result["added"],
            "failed": result["failed"]
        },
        "message": f"Se añadieron {len(result['added'])} usuarios a la asignatura. {len(result['failed'])} fallaron.",
        "status": 200
    }

@subjects_routes.get("/{subject_id}/documents", response_model=APIResponse)
def get_subject_documents_route(
    subject_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["student", "teacher", "admin"]))
):
    """Obtiene todos los documentos asociados a una asignatura"""
    documents = get_subject_documents(db=db, subject_id=subject_id)
    if documents is None:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    # Convertir los documentos al esquema DocumentOut para serialización
    document_outs = [DocumentOut.model_validate(doc) for doc in documents]
    return {
        "data": document_outs,
        "message": "Documentos de la asignatura obtenidos correctamente",
        "status": 200
    }

@subjects_routes.delete("/{subject_id}/users", response_model=APIResponse)
def remove_multiple_users_from_subject_route(
    subject_id: int,
    users_request: UserIdsRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Elimina múltiples usuarios (profesores o estudiantes) de una asignatura (solo administradores)"""
    
    result = remove_multiple_users_from_subject(
        db=db, 
        subject_id=subject_id, 
        user_ids=users_request.user_ids
    )
    
    if not result["success"]:
        status_code = 404 if result.get("error") == "Asignatura no encontrada" else 400
        raise HTTPException(status_code=status_code, detail=result.get("error", "Error al eliminar usuarios"))
    
    return {
        "data": {
            "removed": result["removed"],
            "failed": result["failed"]
        },
        "message": f"Se eliminaron {len(result['removed'])} usuarios de la asignatura. {len(result['failed'])} fallaron.",
        "status": 200
    }
