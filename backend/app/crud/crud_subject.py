from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Subject, User, Document

def get_all_subjects(db: Session) -> List[Subject]:
    """
    Obtiene todas las asignaturas de la BD.
    """
    return db.query(Subject).all()

def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    """
    Obtiene una asignatura por su ID desde la BD.
    """
    return db.query(Subject).filter(Subject.id == subject_id).first()

def get_subject_by_code(db: Session, code: str) -> Optional[Subject]:
    """
    Obtiene una asignatura por su código desde la BD.
    """
    return db.query(Subject).filter(Subject.code == code).first()

def create_subject(db: Session, name: str, code: str, description: str = None) -> Subject:
    """
    Crea una nueva asignatura en la BD.
    """
    db_subject = Subject(
        name=name,
        code=code,
        description=description
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def update_subject(db: Session, subject_id: int, name: str, code: str, description: str = None) -> Optional[Subject]:
    """
    Actualiza una asignatura en la BD.
    """
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return None
    
    db_subject.name = name
    db_subject.code = code
    db_subject.description = description
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

def delete_subject(db: Session, subject_id: int) -> bool:
    """
    Elimina una asignatura de la BD.
    """
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return False
    
    db.delete(db_subject)
    db.commit()
    return True

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su ID desde la BD.
    """
    return db.query(User).filter(User.id == user_id).first()

def add_user_to_subject(db: Session, subject: Subject, user: User) -> bool:
    """
    Agrega un usuario a una asignatura en la BD.
    """
    try:
        if user not in subject.users:
            subject.users.append(user)
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        return False

def remove_user_from_subject(db: Session, subject: Subject, user: User) -> bool:
    """
    Elimina un usuario de una asignatura en la BD.
    """
    try:
        if user in subject.users:
            subject.users.remove(user)
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        return False

def get_documents_by_subject_id(db: Session, subject_id: int) -> List[Document]:
    """
    Obtiene todos los documentos de una asignatura desde la BD.
    """
    return db.query(Document).filter(Document.subject_id == subject_id).all()

def count_documents_by_subject_id(db: Session, subject_id: int) -> int:
    """
    Cuenta los documentos de una asignatura desde la BD.
    """
    return db.query(Document).filter(Document.subject_id == subject_id).count()

def is_user_assigned_to_subject(db: Session, user_id: int, subject_id: int) -> bool:
    """
    Verifica si un usuario está asignado a una asignatura.
    """
    from .crud_user import get_user_by_id
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    return any(subject.id == subject_id for subject in user.subjects)
