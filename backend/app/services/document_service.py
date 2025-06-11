import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Document
from app.models.schemas import DocumentCreate
from fastapi import HTTPException, UploadFile
import logging

logger = logging.getLogger(__name__)
from app.core.config import settings

from app.services.embedding_service import create_document_chunks
from app.services.summary_service import update_document_summary
from ..utils.document_utils import extract_text_from_pdf



def save_document(db: Session,pdf_file: UploadFile,document: DocumentCreate):
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
    
    
    topic_id = None if document.topic_id == 0 else document.topic_id
    
    new_document = Document(
        title=document.title,
        file_path=file_path,
        description=document.description,
        user_id=document.user_id,
        subject_id=document.subject_id,  # Campo obligatorio
        topic_id=topic_id  # Campo opcional
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
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
    return db.query(Document).filter(Document.id == document_id).all()

def list_all_documents(db: Session, user_id: int = None, is_admin: bool = False):
    """
    Lista todos los documentos según el rol del usuario:
    - Administradores: Ven todos los documentos
    - Profesores: Ven documentos de las asignaturas a las que están asignados
    - Estudiantes: Ven documentos de las asignaturas en las que están matriculados
    """
    from app.models.models import User, user_subject
    
    query = db.query(Document)
    
    if user_id is not None and not is_admin:
        # Obtener el usuario actual para verificar su rol
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        if user.role == "teacher":
            # Los profesores ven documentos de las asignaturas a las que están asignados
            user_subjects = db.query(user_subject.c.subject_id).filter(
                user_subject.c.user_id == user_id
            ).subquery()
            
            query = query.filter(Document.subject_id.in_(
                db.query(user_subjects.c.subject_id)
            ))
            
        elif user.role == "student":
            # Los estudiantes ven documentos de las asignaturas en las que están matriculados
            user_subjects = db.query(user_subject.c.subject_id).filter(
                user_subject.c.user_id == user_id
            ).subquery()
            
            query = query.filter(Document.subject_id.in_(
                db.query(user_subjects.c.subject_id)
            ))
        else:
            # Para otros roles que no sean admin, mostrar solo sus documentos
            query = query.filter(Document.user_id == user_id)
    
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

def document_exists(db: Session, document_id: int) -> bool:
    """
    Verifica si existe un documento con el ID especificado.
    """
    return db.query(db.query(Document).filter(Document.id == document_id).exists()).scalar()

def delete_document(db: Session, document_id: int, user_id: int = None, is_admin: bool = False):
    """
    Elimina un documento, sus chunks asociados y el archivo físico.
    Si se proporciona user_id y no es admin, se verifica que sea el propietario del documento.
    """
    # Buscar el documento
    document = db.query(Document).filter(Document.id == document_id).first()
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
    
    # Eliminar el documento de la base de datos (los chunks se eliminarán automáticamente por cascade)
    db.delete(document)
    db.commit()
    
    return {"id": document_id}

def get_document_by_id(db: Session, document_id: int):
    """
    Obtiene un documento específico por su ID.
    """
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents_by_topic_id(db: Session, topic_id: int, current_user):
    """
    Obtiene todos los documentos asociados a un tema específico.
    Los administradores pueden ver todos los documentos.
    Los profesores y estudiantes solo pueden ver documentos de asignaturas a las que tienen acceso.
    """
    from app.models.models import Topic, Subject
    
    # Verificar que el tema existe
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    
    # Verificar acceso a la asignatura del tema
    subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    # Los administradores tienen acceso completo
    if current_user.role == "admin":
        documents = db.query(Document).filter(Document.topic_id == topic_id).all()
    else:
        # Para profesores y estudiantes, verificar acceso a la asignatura
        is_assigned = any(user.id == current_user.id for user in subject.users)
        if not is_assigned:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para acceder a los documentos de este tema"
            )
        
        documents = db.query(Document).filter(Document.topic_id == topic_id).all()
    
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


