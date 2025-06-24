from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Dict, Any

from app.crud import crud_user, crud_subject, crud_document

def get_current_user_subjects(user_id: int, db: Session):
    """
    Obtiene las asignaturas asociadas al usuario actual.
    
    Args:
        user_id: ID del usuario actual
        db: Sesión de base de datos
        
    Returns:
        Lista de asignaturas asociadas al usuario
    """
    user_db = crud_user.get_user_by_id(db, user_id=user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    # Para todos los roles, obtenemos las asignaturas asociadas
    if user_db.role == 'admin':
        # Para administradores, mostramos todas las asignaturas
        subjects = crud_subject.get_all_subjects(db)
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
            "summary": subject.summary,
            "created_at": subject.created_at,
            "document_count": crud_document.count_documents_by_subject(db, subject_id=subject.id)
        }
        for subject in subjects
    ]

def get_current_user_documents(user_id: int, db: Session):
    """
    Obtiene los documentos asociados al usuario actual.
    
    Args:
        user_id: ID del usuario actual
        db: Sesión de base de datos
        
    Returns:
        Lista de documentos asociados al usuario
    """
    user_db = crud_user.get_user_by_id(db, user_id=user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    # Dependiendo del rol, filtramos los documentos
    if user_db.role == 'admin':
        documents = crud_document.get_all_documents(db)
    elif user_db.role == 'teacher':
        # Profesores ven sus propios documentos
        documents = crud_document.get_documents_by_user(db, user_id=user_id)
    elif user_db.role == 'student':
        # Estudiantes ven documentos de las asignaturas en las que están matriculados
        subject_ids = [subject.id for subject in user_db.subjects]
        if not subject_ids:
            return []
        documents = crud_document.get_documents_by_subject_ids(db, subject_ids=subject_ids)
    else:
        documents = []
    
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
