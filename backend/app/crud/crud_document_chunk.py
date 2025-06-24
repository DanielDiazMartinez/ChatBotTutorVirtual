from typing import List
from sqlalchemy.orm import Session
from app.models.models import DocumentChunk

def create_document_chunks(db: Session, chunks_data: List[dict]) -> List[DocumentChunk]:
    """
    Crea múltiples chunks de documento en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        chunks_data: Lista de diccionarios con datos de chunks
        
    Returns:
        Lista de objetos DocumentChunk creados
    """
    db_chunks = []
    for chunk_data in chunks_data:
        chunk = DocumentChunk(
            document_id=chunk_data['document_id'],
            content=chunk_data['content'],
            embedding=chunk_data['embedding'],
            chunk_number=chunk_data['chunk_number']
        )
        db_chunks.append(chunk)
    
    db.add_all(db_chunks)
    db.flush()
    db.commit()
    return db_chunks

def get_chunks_by_document_id(db: Session, document_id: int) -> List[DocumentChunk]:
    """
    Obtiene todos los chunks de un documento específico.
    """
    return db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
