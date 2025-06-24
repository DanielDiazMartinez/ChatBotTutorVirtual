from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Document, User, user_subject
from app.models.schemas import DocumentCreate

def create_document(db: Session, document: DocumentCreate, file_path: str) -> Document:
    """Crea un nuevo documento en la base de datos."""
    topic_id = None if document.topic_id == 0 else document.topic_id
    new_document = Document(
        title=document.title,
        file_path=file_path,
        description=document.description,
        user_id=document.user_id,
        subject_id=document.subject_id,
        topic_id=topic_id
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document

def get_document_by_id(db: Session, document_id: int) -> Optional[Document]:
    """Obtiene un documento por su ID."""
    return db.query(Document).filter(Document.id == document_id).first()

def get_all_documents(db: Session) -> List[Document]:
    """Obtiene todos los documentos."""
    return db.query(Document).all()

def get_documents_by_user(db: Session, user_id: int) -> List[Document]:
    """Obtiene todos los documentos de un usuario específico."""
    return db.query(Document).filter(Document.user_id == user_id).all()

def get_documents_by_subject_ids(db: Session, subject_ids: List[int]) -> List[Document]:
    """Obtiene documentos que pertenecen a una lista de IDs de asignaturas."""
    return db.query(Document).filter(Document.subject_id.in_(subject_ids)).all()

def count_documents_by_subject(db: Session, subject_id: int) -> int:
    """Cuenta el número de documentos para una asignatura específica."""
    return db.query(Document).filter(Document.subject_id == subject_id).count()

def document_exists(db: Session, document_id: int) -> bool:
    """Verifica si existe un documento con el ID especificado."""
    return db.query(db.query(Document).filter(Document.id == document_id).exists()).scalar()

def delete_document_db(db: Session, document: Document):
    """Elimina un documento de la base de datos."""
    db.delete(document)
    db.commit()

def get_documents_by_topic_id(db: Session, topic_id: int) -> List[Document]:
    """Obtiene todos los documentos asociados a un tema específico."""
    return db.query(Document).filter(Document.topic_id == topic_id).all()

def get_user_subject_ids(db: Session, user_id: int) -> List[int]:
    """Obtiene los IDs de las asignaturas asociadas a un usuario."""
    return [subject_id for subject_id, in db.query(user_subject.c.subject_id).filter(user_subject.c.user_id == user_id).all()]
