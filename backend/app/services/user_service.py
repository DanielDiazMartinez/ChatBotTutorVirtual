from sqlalchemy.orm import Session
from app.crud import crud_user
from app.models.schemas import UserCreate, UserUpdate
from fastapi import HTTPException 
from app.core.security import get_password_hash
from typing import List, Dict, Any

def create_user(user: UserCreate, db: Session):
    """
    Crea un nuevo usuario en la base de datos.
    """
    existing_user = crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user.model_dump()
    hashed_password = get_password_hash(user_data.pop("password"))
    
    user_db = crud_user.create_user(
        db=db,
        email=user_data["email"],
        full_name=user_data["full_name"],
        role=user_data["role"],
        hashed_password=hashed_password
    )
    
    return {
        "id": user_db.id,
        "email": user_db.email,
        "full_name": user_db.full_name,
        "role": user_db.role,
        "created_at": user_db.created_at
    }

def get_user_by_id(user_id: int, role: str | None, db: Session):
    """
    Obtiene un usuario por su ID y opcionalmente por su rol.
    """
    if role:
        user_db = crud_user.get_user_by_id_and_role(db, user_id, role)
    else:
        user_db = crud_user.get_user_by_id(db, user_id)
        
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {
        "id": user_db.id,
        "email": user_db.email,
        "full_name": user_db.full_name,
        "role": user_db.role,
        "created_at": user_db.created_at
    }
    

def get_users_by_role(role: str, db: Session) -> List[dict]:
    """
    Obtiene todos los usuarios de un rol específico.
    """
    users = crud_user.get_users_by_role(db, role)

    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "created_at": user.created_at
        }
        for user in users
    ]

def get_all_users(db: Session) -> List[dict]:
    """
    Obtiene todos los usuarios de la base de datos y los convierte en diccionarios.
    """
    users = crud_user.get_all_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No hay usuarios registrados.")
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "created_at": user.created_at
        }
        for user in users
    ]

def update_user(user_id: int, user_update: UserUpdate, db: Session):
    """
    Actualiza un usuario existente.
    """
    user_db = crud_user.get_user_by_id(db, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    user_db = crud_user.update_user(db, user_id, update_data)
    
    return {
        "id": user_db.id,
        "email": user_db.email,
        "full_name": user_db.full_name,
        "role": user_db.role,
        "created_at": user_db.created_at
    }

def delete_user(user_id: int, db: Session):
    """
    Elimina un usuario por su ID.
    """
    user = crud_user.delete_user(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "created_at": user.created_at
    }

def get_user_by_email(email: str, db: Session):
    """
    Obtiene un usuario por su email.
    """
    return crud_user.get_user_by_email(db, email)

def get_subjects_by_user_id(user_id: int, db: Session):
    """
    Obtiene las asignaturas asociadas a un usuario por su ID.
    """
    # Obtenemos las asignaturas del usuario usando CRUD
    subjects = crud_user.get_subjects_by_user_id(db, user_id)
    if subjects is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not subjects:
        raise HTTPException(status_code=404, detail="No hay materias asociadas al usuario.")
    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "summary": subject.summary,
            "created_at": subject.created_at,
            "document_count": crud_user.count_documents_by_subject_id(db, subject.id)
        }
        
        for subject in subjects
    ]

def get_current_user(current_user_id: int, db: Session) -> Dict[str, Any]:
    """
    Obtiene la información del usuario actualmente autenticado.
    """
    user = crud_user.get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "created_at": user.created_at
    }