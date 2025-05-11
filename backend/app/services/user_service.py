from sqlalchemy.orm import Session
from app.models.models import User
from app.models.schemas import UserCreate, UserUpdate
from fastapi import HTTPException 
from app.core.security import get_password_hash
from typing import List

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
    return user_db

def get_user_by_id(user_id: int, role: str | None, db: Session):
    """
    Obtiene un usuario por su ID y opcionalmente por su rol.
    """
    query = db.query(User).filter(User.id == user_id)
    if role:
        query = query.filter(User.role == role)
    return query.first()

def get_users_by_role(role: str, db: Session) -> List[User]:
    """
    Obtiene todos los usuarios de un rol específico.
    """
    return db.query(User).filter(User.role == role).all()

def update_user(user_id: int, user_update: UserUpdate, db: Session):
    """
    Actualiza un usuario existente.
    """
    user_db = get_user_by_id(user_id, None, db)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
    for field, value in update_data.items():
        setattr(user_db, field, value)
    
    db.commit()
    db.refresh(user_db)
    return user_db

def delete_user(user_id: int, db: Session):
    """
    Elimina un usuario por su ID.
    """
    user = get_user_by_id(user_id, None, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    db.delete(user)
    db.commit()
    return user

def get_user_by_email(email: str, db: Session):
    """
    Obtiene un usuario por su email.
    """
    return db.query(User).filter(User.email == email).first()
