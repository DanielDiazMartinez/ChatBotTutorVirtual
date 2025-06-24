from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import User, Subject, Document

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su ID desde la BD.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Obtiene un usuario por su email desde la BD.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, full_name: str, role: str, hashed_password: str) -> User:
    """
    Crea un nuevo usuario en la BD.
    """
    user_db = User(
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=hashed_password
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

def get_user_by_id_and_role(db: Session, user_id: int, role: str) -> Optional[User]:
    """
    Obtiene un usuario por su ID y rol desde la BD.
    """
    return db.query(User).filter(User.id == user_id, User.role == role).first()

def get_users_by_role(db: Session, role: str) -> List[User]:
    """
    Obtiene todos los usuarios de un rol específico desde la BD.
    """
    return db.query(User).filter(User.role == role).all()

def get_all_users(db: Session) -> List[User]:
    """
    Obtiene todos los usuarios desde la BD.
    """
    return db.query(User).all()

def update_user(db: Session, user_id: int, update_data: dict) -> Optional[User]:
    """
    Actualiza un usuario en la BD.
    """
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        return None

    for field, value in update_data.items():
        setattr(user_db, field, value)
    
    db.commit()
    db.refresh(user_db)
    return user_db

def delete_user(db: Session, user_id: int) -> Optional[User]:
    """
    Elimina un usuario de la BD.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    db.delete(user)
    db.commit()
    return user

def count_documents_by_subject_id(db: Session, subject_id: int) -> int:
    """
    Cuenta los documentos de una asignatura desde la BD.
    """
    return db.query(Document).filter(Document.subject_id == subject_id).count()

def get_subjects_by_user_id(db: Session, user_id: int) -> Optional[List[Subject]]:
    """
    Obtiene las asignaturas asociadas a un usuario por su ID desde la BD.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    return user.subjects
