from sqlalchemy.orm import Session
from app.models.models import User, Document
from fastapi import HTTPException
from typing import List, Dict, Any

def get_current_user_subjects(user_id: int, db: Session):
    """
    Obtiene las asignaturas asociadas al usuario actual.
    
    Args:
        user_id: ID del usuario actual
        db: Sesión de base de datos
        
    Returns:
        Lista de asignaturas asociadas al usuario
    """
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    # Para todos los roles, obtenemos las asignaturas asociadas
    if user_db.role == 'admin':
        # Para administradores, mostramos todas las asignaturas
        from app.models.models import Subject
        subjects = db.query(Subject).all()
    else:
        # Para profesores y estudiantes, mostramos sus asignaturas específicas
        subjects = user_db.subjects
    
    # Si no hay asignaturas, devolvemos lista vacía en lugar de error
    if not subjects:
        return []
        
    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "created_at": subject.created_at
        }
        for subject in subjects
    ]

def get_current_user_documents(user_id: int, db: Session):
    """
    Obtiene los documentos asociados al usuario actual.
    
    Args:
        user_id: ID del usuario actual
        db: Sesión de base de datos
        is_admin: Indica si el usuario es administrador
        
    Returns:
        Lista de documentos asociados al usuario
    """
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    # Dependiendo del rol, filtramos los documentos
    query = db.query(Document)
    
    if user_db.role == 'teacher':
        # Profesores ven sus propios documentos
        query = query.filter(Document.user_id == user_id)
    elif user_db.role == 'student':
        # Estudiantes ven documentos de las asignaturas en las que están matriculados
        from sqlalchemy import or_
        subject_ids = [subject.id for subject in user_db.subjects]
        query = query.filter(Document.subject_id.in_(subject_ids))
    # Administradores ven todos los documentos (no necesita filtro)
    
    documents = query.all()
    
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "file_path": doc.file_path,
            "user_id": doc.user_id,
            "subject_id": doc.subject_id,
            "topic_id": doc.topic_id,
            "created_at": doc.created_at
        }
        for doc in documents
    ]
