from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_role
from app.services.user_service import (
    create_user,
    get_user_by_id,
    get_users_by_role,
    update_user,
    delete_user
)
from app.models.schemas import UserCreate, UserUpdate, UserOut

users_routes = APIRouter()

@users_routes.post("/register", response_model=UserOut, status_code=201)
def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Registrar un nuevo usuario (solo administradores)"""
    return create_user(user, db)

@users_routes.get("/list/{role}", response_model=List[UserOut])
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
        raise HTTPException(status_code=200, detail=f"No hay usuarios registrados con el rol {role}")
    return users

@users_routes.get("/{user_id}", response_model=UserOut)
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
    return user

@users_routes.put("/{user_id}", response_model=UserOut)
def update_user_route(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Actualizar información de un usuario (solo administradores)"""
    return update_user(user_id, user_update, db)

@users_routes.delete("/{user_id}", response_model=UserOut)
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Eliminar un usuario (solo administradores)"""
    return delete_user(user_id, db)

