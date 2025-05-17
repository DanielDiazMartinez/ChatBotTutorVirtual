from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_role
from app.services.user_service import (
    create_user,
    get_all_users,
    get_subjects_by_user_id,
    get_user_by_id,
    get_users_by_role,
    update_user,
    delete_user,
    get_current_user
)
from app.models.schemas import APIResponse, SubjectOut, UserCreate, UserUpdate, UserOut
from app.services.current_user_service import get_current_user_subjects

users_routes = APIRouter()

@users_routes.post("/register", response_model=APIResponse, status_code=201)
def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    """Registrar un nuevo usuario (solo administradores)"""
    user_created = create_user(user, db)
    return {
        "data": user_created,
        "message": "Usuario registrado correctamente",
        "status": 201
    }

@users_routes.get("/list/{role}", response_model=APIResponse)
def list_users_by_role(
    role: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Listar todos los usuarios de un rol específico (profesores y administradores)"""
    if role not in ["admin", "teacher", "student"]:
        raise HTTPException(status_code=400, detail="Rol inválido")
        
    users = get_users_by_role(role, db)
    if not users:
        return {
            "data": [],
            "message": f"No hay usuarios registrados con el rol {role}",
            "status": 200
        }
    return {
        "data": users,
        "message": f"Usuarios con rol {role} obtenidos correctamente",
        "status": 200
    }

@users_routes.get("/list", response_model=APIResponse)
def list_user_all(
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):      
    users = get_all_users(db)
    if not users:
        return {
            "data": [],
            "message": f"No hay usuarios registrados",
            "status": 200
        }
    
    return {
        "data": users,
        "message": f"Usuarios obtenidos correctamente",
        "status": 200
    }

@users_routes.get("/me", response_model=APIResponse)
def get_me(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["admin", "teacher", "student"]))
):
    """Obtener información del usuario actual basado en el token de autenticación"""
    user_id = current_user.id
    user = get_current_user(user_id, db)
    return {
        "data": user,
        "message": "Información del usuario actual obtenida correctamente",
        "status": 200
    }

@users_routes.get("/me/subjects", response_model=APIResponse)
def list_current_user_subjects(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["admin", "teacher", "student"]))
):
    """Obtener las materias del usuario actual"""

    user_id = current_user.id
    subjects = get_current_user_subjects(user_id, db)
    return {
        "data": subjects,
        "message": "Materias obtenidas correctamente",
        "status": 200
    }

@users_routes.get("/{user_id}", response_model=APIResponse)
def get_user(
    user_id: int,
    role: str | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Obtener información de un usuario (profesores, estudiantes y administradores)"""
    user = get_user_by_id(user_id, role, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "data": user,
        "message": "Usuario obtenido correctamente",
        "status": 200
    }

@users_routes.put("/{user_id}", response_model=APIResponse)
def update_user_route(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Actualizar información de un usuario (solo administradores)"""
    user_updated = update_user(user_id, user_update, db)
    return {
        "data": user_updated,
        "message": "Usuario actualizado correctamente",
        "status": 200
    }

@users_routes.delete("/{user_id}", response_model=APIResponse)
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Eliminar un usuario (solo administradores)"""
    user_deleted = delete_user(user_id, db)
    return {
        "data": user_deleted,
        "message": "Usuario eliminado correctamente",
        "status": 200
    }

@users_routes.get("/{user_id}/subjects", response_model=APIResponse)
def list_subjects_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Obtener las materias de un usuario (profesores, estudiantes y administradores)"""
    subjects = get_subjects_by_user_id(user_id, db)
    if not subjects:
        return {
            "data": [],
            "message": "No hay materias registradas para este usuario",
            "status": 200
        }
    return {
        "data": subjects,
        "message": "Materias obtenidas correctamente",
        "status": 200
    }