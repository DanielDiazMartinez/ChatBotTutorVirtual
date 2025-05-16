from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.models import Subject, User, teacher_subject, student_subject
from ..models.schemas import SubjectCreate

def create_subject(db: Session, subject: SubjectCreate) -> Subject:
    """Crea una nueva asignatura"""
    db_subject = Subject(
        name=subject.name,
        code=subject.code,
        description=subject.description
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def get_subject_by_id(db: Session, subject_id: int) -> Subject:
    """Obtiene una asignatura por su ID"""
    return db.query(Subject).filter(Subject.id == subject_id).first()

def get_all_subjects(db: Session) -> list[Subject]:
    """Obtiene todas las asignaturas"""
    return db.query(Subject).all()

def update_subject(db: Session, subject_id: int, subject: SubjectCreate) -> Subject:
    """Actualiza una asignatura existente"""
    db_subject = get_subject_by_id(db, subject_id)
    if not db_subject:
        return None
    
    db_subject.name = subject.name
    db_subject.code = subject.code
    db_subject.description = subject.description
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

def delete_subject(db: Session, subject_id: int) -> bool:
    """Elimina una asignatura"""
    db_subject = get_subject_by_id(db, subject_id)
    if not db_subject:
        return False
    
    db.delete(db_subject)
    db.commit()
    return True

def add_user_to_subject(db: Session, subject_id: int, user_id: int, role: str) -> bool:
    """Agrega un usuario a una asignatura"""
    db_subject = get_subject_by_id(db, subject_id)
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_subject or not db_user:
        return False
    
    # Verificar que el usuario tiene el rol correcto (profesor o estudiante)
    if not (db_user.role == "teacher" or db_user.role == "student"):
        return False
        
    try:
        if db_user.role == "teacher":
            # Verificar si ya existe la relación
            if db_user not in db_subject.teachers:
                db_subject.teachers.append(db_user)
                
        elif db_user.role == "student":
            # Verificar si ya existe la relación
            if db_user not in db_subject.students:
                db_subject.students.append(db_user)
        else:
            return False
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
