import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.schemas import DocumentCreate
from fastapi import HTTPException, UploadFile
import logging

from app.crud import crud_document, crud_user, crud_topic, crud_subject
from app.core.config import settings
from app.services.embedding_service import create_document_chunks
from app.services.summary_service import update_document_summary
from ..utils.document_utils import extract_text_from_pdf

logger = logging.getLogger(__name__)


def save_document(db: Session, pdf_file: UploadFile, document: DocumentCreate):
    """
    Guarda el documento en PostgreSQL.
    """
    if not pdf_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    subfolder_path = os.path.join(settings.UPLOAD_FOLDER, str(document.user_id))
    os.makedirs(subfolder_path, exist_ok=True)
    
    # Generamos un nombre único para el archivo
    file_name, file_ext = os.path.splitext(pdf_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    unique_file_name = f"{file_name}_{timestamp}_{unique_id}{file_ext}"
    
    file_path = os.path.join(subfolder_path, unique_file_name)
    
    with open(file_path, "wb") as buffer:
        buffer.write(pdf_file.file.read())
    
    # Crear documento en la BD usando CRUD
    new_document = crud_document.create_document(db, document, file_path)
    
    content = extract_text_from_pdf(pdf_file)
    if not content:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")
    
    create_document_chunks(db, new_document.id, content)
    
    # Generar resumen del documento después de procesar los chunks
    try:
        import asyncio
        asyncio.create_task(update_document_summary(new_document.id, db))
        logger.info(f"Resumen generado para el documento {new_document.id}")
    except Exception as e:
        logger.warning(f"Error al generar resumen para documento {new_document.id}: {e}")
        
    return new_document

def list_documents(db: Session, document_id: int):
    """
    Obtiene los documentos de un profesor.
    """
    return crud_document.get_document_by_id(db, document_id)

def list_all_documents(db: Session, user_id: int = None, is_admin: bool = False):
    """
    Lista todos los documentos según el rol del usuario:
    - Administradores: Ven todos los documentos
    - Profesores: Ven documentos de las asignaturas a las que están asignados
    - Estudiantes: Ven documentos de las asignaturas en las que están matriculados
    """
    if is_admin:
        documents = crud_document.get_all_documents(db)
    elif user_id is not None:
        # Obtener el usuario actual para verificar su rol
        user = crud_user.get_user_by_id(db, user_id)
        if not user:
            return []
        
        if user.role == "teacher":
            # Los profesores ven documentos de las asignaturas a las que están asignados
            subject_ids = crud_document.get_user_subject_ids(db, user_id)
            documents = crud_document.get_documents_by_subject_ids(db, subject_ids)
        elif user.role == "student":
            # Los estudiantes ven documentos de las asignaturas en las que están matriculados
            subject_ids = crud_document.get_user_subject_ids(db, user_id)
            documents = crud_document.get_documents_by_subject_ids(db, subject_ids)
        else:
            # Para otros roles que no sean admin, mostrar solo sus documentos
            documents = crud_document.get_documents_by_user(db, user_id)
    else:
        documents = crud_document.get_all_documents(db)
    
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

def document_exists(db: Session, document_id: int) -> bool:
    """
    Verifica si existe un documento con el ID especificado.
    """
    return crud_document.document_exists(db, document_id)

def delete_document(db: Session, document_id: int, user_id: int = None, is_admin: bool = False):
    """
    Elimina un documento, sus chunks asociados y el archivo físico.
    Si se proporciona user_id y no es admin, se verifica que sea el propietario del documento.
    """
    # Buscar el documento
    document = crud_document.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    
    # Verificar propiedad si no es administrador
    if user_id is not None and not is_admin:
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este documento.")
    
    # Eliminar el archivo físico si existe
    if document.file_path and os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except OSError as e:
            # Continuar con la eliminación de la BD aunque falle la eliminación del archivo
            logger.error(f"Error al eliminar el archivo: {e}")
    
    # Eliminar el documento de la base de datos usando CRUD
    crud_document.delete_document_db(db, document)
    
    return {"id": document_id}

def get_document_by_id(db: Session, document_id: int):
    """
    Obtiene un documento específico por su ID.
    """
    return crud_document.get_document_by_id(db, document_id)

def get_documents_by_topic_id(db: Session, topic_id: int, current_user):
    """
    Obtiene todos los documentos asociados a un tema específico.
    Los administradores pueden ver todos los documentos.
    Los profesores y estudiantes solo pueden ver documentos de asignaturas a las que tienen acceso.
    """
    # Verificar que el tema existe
    topic = crud_topic.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    
    # Verificar acceso a la asignatura del tema
    subject = crud_subject.get_subject_by_id(db, topic.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    # Los administradores tienen acceso completo
    if current_user.role == "admin":
        documents = crud_document.get_documents_by_topic_id(db, topic_id)
    else:
        # Para profesores y estudiantes, verificar acceso a la asignatura
        is_assigned = crud_subject.is_user_assigned_to_subject(db, current_user.id, topic.subject_id)
        if not is_assigned:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para acceder a los documentos de este tema"
            )
        
        documents = crud_document.get_documents_by_topic_id(db, topic_id)
    
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "file_path": doc.file_path,
            "user_id": doc.user_id,
            "subject_id": doc.subject_id,
            "topic_id": doc.topic_id,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        }
        for doc in documents
    ]


