import os
from sqlalchemy.orm import Session
from app.models.models import  Document
from app.models.schemas import   DocumentCreate
from fastapi import  HTTPException, UploadFile, logger
from app.core.config import settings

from app.services.vector_service import insert_document_chunks
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
    
    file_path = os.path.join(subfolder_path, pdf_file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(pdf_file.file.read())
    
    # Si topic_id es 0, establecerlo como None para evitar violación de clave foránea
    topic_id = None if document.topic_id == 0 else document.topic_id
    
    new_document = Document(
        title=document.title,
        file_path=file_path,
        description=document.description,
        teacher_id=document.user_id,
        subject_id=document.subject_id,  # Campo obligatorio
        topic_id=topic_id  # Campo opcional
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    content = extract_text_from_pdf(pdf_file)

    if not content:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")
    
    insert_document_chunks(db, new_document.id, content)
        
    return new_document

def list_documents(db: Session, document_id: int):
    """
    Obtiene los documentos de un profesor.
    """
    return db.query(Document).filter(Document.id == document_id).all()

def list_all_documents(db: Session, user_id: int = None, is_admin: bool = False):
    """
    Lista todos los documentos.
    Si el usuario no es administrador y se proporciona user_id, sólo devuelve sus documentos.
    """
    query = db.query(Document)
    
    if user_id is not None and not is_admin:
        query = query.filter(Document.teacher_id == user_id)
    
    documents = query.all()
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "file_path": doc.file_path,
            "teacher_id": doc.teacher_id,
            "subject_id": doc.subject_id,
            "topic_id": doc.topic_id,
            "created_at": doc.created_at
        }
        for doc in documents
    ]

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
        if document.teacher_id != user_id:
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


