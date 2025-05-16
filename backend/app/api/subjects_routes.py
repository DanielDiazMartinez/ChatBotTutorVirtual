from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import require_role
from ..models.schemas import APIResponse, SubjectCreate, SubjectOut
from ..models.models import User
from ..services.subject_service import (
    add_user_to_subject,
    create_subject,
    get_subject_by_id,
    get_all_subjects,
    update_subject,
    delete_subject,
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
    # Buscar al usuario para determinar su rol
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not add_user_to_subject(db=db, subject_id=subject_id, user_id=user_id, role=user.role):
        raise HTTPException(status_code=400, detail="No se pudo agregar el usuario a la asignatura")
    
    return {
        "data": None,
        "message": "Usuario agregado a la asignatura correctamente",
        "status": 200
    }
