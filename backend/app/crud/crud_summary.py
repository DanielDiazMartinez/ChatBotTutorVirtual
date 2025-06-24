from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Document, DocumentChunk, Subject

def get_document_by_id(db: Session, document_id: int) -> Optional[Document]:
    """
    Obtiene un documento por su ID desde la BD.
    """
    return db.query(Document).filter(Document.id == document_id).first()

def get_document_chunks_by_document_id(db: Session, document_id: int) -> List[DocumentChunk]:
    """
    Obtiene todos los chunks de un documento ordenados por número desde la BD.
    """
    return db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_number).all()

def update_document_summary(db: Session, document_id: int, summary: str) -> bool:
    """
    Actualiza el resumen de un documento en la BD.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        
        document.summary = summary
        db.commit()
        return True
        
    except Exception:
        db.rollback()
        return False

def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    """
    Obtiene una asignatura por su ID desde la BD.
    """
    return db.query(Subject).filter(Subject.id == subject_id).first()

def get_documents_by_subject_id(db: Session, subject_id: int) -> List[Document]:
    """
    Obtiene todos los documentos de una asignatura desde la BD.
    """
    return db.query(Document).filter(Document.subject_id == subject_id).all()

def update_subject_summary(db: Session, subject_id: int, summary: str) -> bool:
    """
    Actualiza el resumen de una asignatura en la BD.
    """
    try:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return False
        
        subject.summary = summary
        db.commit()
        return True
        
    except Exception:
        db.rollback()
        return False
