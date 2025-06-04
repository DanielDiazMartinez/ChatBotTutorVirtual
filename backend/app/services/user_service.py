from sqlalchemy.orm import Session
from app.models.models import User
from app.models.schemas import UserCreate, UserUpdate
from fastapi import HTTPException 
from app.core.security import get_password_hash
from typing import List, Dict, Any

def create_user(user: UserCreate, db: Session):
    """
    Crea un nuevo usuario en la base de datos.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user.model_dump()
    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    
    user_db = User(**user_data)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
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
    query = db.query(User).filter(User.id == user_id)
    if role:
        query = query.filter(User.role == role)
    user_db = query.first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {
    "id": user_db.id,
    "email": user_db.email,
    "full_name": user_db.full_name,
    "role": user_db.role,
    "created_at": user_db.created_at
}
    

def get_users_by_role(role: str, db: Session) -> List[User]:
    """
    Obtiene todos los usuarios de un rol específico.
    """
    users = db.query(User).filter(User.role == role).all()

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
    users = db.query(User).all()
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
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
    for field, value in update_data.items():
        setattr(user_db, field, value)
    
    db.commit()
    db.refresh(user_db)
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
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    db.delete(user)
    db.commit()

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
    return db.query(User).filter(User.email == email).first()

def get_subjects_by_user_id(user_id: int, db: Session):
    """
    Obtiene las asignaturas asociadas a un usuario por su ID.
    """
    # Obtenemos el objeto User directamente de la base de datos
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    subjects = user_db.subjects
    if not subjects:
        raise HTTPException(status_code=404, detail="No hay materias asociadas al usuario.")
    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "summary": subject.summary,
            "created_at": subject.created_at
        }
        
        for subject in subjects
    ]

def get_current_user(current_user_id: int, db: Session) -> Dict[str, Any]:
    """
    Obtiene la información del usuario actualmente autenticado.
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "created_at": user.created_at
    }