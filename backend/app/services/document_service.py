import os
import logging
from typing import List, Tuple, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, literal_column
from sqlalchemy.orm import Session

from ..models.models import (
    Document, 
    DocumentChunk,
    CosineDistance, 
    EuclideanDistance, 
    InnerProduct
)
from ..models.schemas import DocumentCreate
from ..utils.document_utils import (
    extract_text_from_pdf,
    chunk_text, 
    generate_embedding
)
from ..core.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_document(db: Session,pdf_file: UploadFile,document: DocumentCreate):
    """
    Guarda el documento en PostgreSQL.
    """
   
    if not pdf_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    subfolder_path = os.path.join(settings.UPLOAD_FOLDER, str(document.teacher_id))

    os.makedirs(subfolder_path, exist_ok=True)
    
    file_path = os.path.join(subfolder_path, pdf_file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(pdf_file.file.read())
    
    new_document = Document(
        title=document.title,
        file_path=file_path,
        description=document.description,
        teacher_id=document.teacher_id
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    content = extract_text_from_pdf(pdf_file)

    if not content:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")
    
    insert_document_chunks(db, new_document.id, content)
        
    return new_document

def list_documents(db: Session, teacher_id: int):
    """
    Obtiene los documentos de un profesor.
    """
    return db.query(Document).filter(Document.teacher_id == teacher_id).all()

def insert_document_chunks(
    db: Session,
    document_id: int,
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[DocumentChunk]:
    """
    Divide el texto de un documento en fragmentos (chunks), genera embeddings
    vectoriales para cada uno y los inserta en la base de datos.

    Args:
        db: Sesión de base de datos SQLAlchemy.
        document_id: ID del documento al que pertenecen los chunks.
        text: Texto completo del documento.
        chunk_size: Tamaño deseado para cada chunk en caracteres.
        overlap: Superposición deseada entre chunks (actualmente no implementado en `chunk_text` usado).

    Returns:
        Lista de los objetos DocumentChunk creados y guardados.

    Raises:
        HTTPException: Si el documento con el ID proporcionado no existe.
        ValueError: Si ocurre un error al generar embeddings.
        Exception: Para otros errores de base de datos.
    """
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail=f"Documento con ID {document_id} no encontrado.")

    chunks_content = chunk_text(text, chunk_size=chunk_size)
    created_chunks = []

    try:
        for i, content in enumerate(chunks_content):
            embedding = generate_embedding(content)
            if embedding is None:
                logger.warning(f"No se pudo generar embedding para el chunk {i} del documento {document_id}. Omitiendo chunk.")
                continue

            chunk = DocumentChunk(
                document_id=document_id,
                content=content,
                embedding=embedding,
                chunk_number=i
            )
            db.add(chunk)
            created_chunks.append(chunk)

        if not created_chunks:
             logger.warning(f"No se crearon chunks válidos para el documento {document_id}.")
             return []

        db.commit()
        for chunk in created_chunks:
             db.refresh(chunk)

        logger.info(f"Se insertaron {len(created_chunks)} chunks para el documento ID {document_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error al insertar chunks para documento {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar los chunks del documento.") from e

    return created_chunks


def search_similar_chunks(
    db: Session,
    query_embedding: List[float],
    document_id: Optional[int] = None,
    limit: int = 10,
    similarity_metric: str = "cosine"
) -> List[Tuple[DocumentChunk, float]]:
    """
    Busca en la base de datos los chunks de documento más similares a un
    embedding de consulta, utilizando métricas de distancia vectorial (pgvector).

    Args:
        db: Sesión de base de datos SQLAlchemy.
        query_embedding: El vector de embedding de la consulta.
        document_id: ID opcional para limitar la búsqueda a un documento específico.
        limit: Número máximo de chunks similares a devolver.
        similarity_metric: Métrica de similitud a usar ('cosine', 'l2', 'inner_product').

    Returns:
        Lista de tuplas, donde cada tupla contiene un objeto DocumentChunk
        y su puntuación de similitud calculada (mayor es mejor).

    Raises:
        ValueError: Si se proporciona una `similarity_metric` no válida o query_embedding vacío.
        Exception: Para errores durante la consulta a la base de datos.
    """
    if not query_embedding:
        raise ValueError("El embedding de consulta no puede estar vacío.")

    embedding_str = f"CAST(ARRAY[{','.join(map(str, query_embedding))}] AS vector)"
    embedding_literal = literal_column(embedding_str)

    if similarity_metric == "cosine":
        distance_expression = CosineDistance(DocumentChunk.embedding, embedding_literal)
        convert_score = lambda dist: 1.0 - dist if dist is not None else 0.0
        order_direction = "asc"
    elif similarity_metric == "l2":
        distance_expression = EuclideanDistance(DocumentChunk.embedding, embedding_literal)
        convert_score = lambda dist: 1.0 / (1.0 + dist) if dist is not None else 0.0
        order_direction = "asc"
    elif similarity_metric == "inner_product":
        distance_expression = InnerProduct(DocumentChunk.embedding, embedding_literal)
        convert_score = lambda dist: -dist if dist is not None else 0.0
        order_direction = "asc"
    else:
        raise ValueError(f"Métrica de similitud no soportada: {similarity_metric}. Usar 'cosine', 'l2' o 'inner_product'.")

    query = select(
        DocumentChunk,
        distance_expression.label("distance")
    ).select_from(DocumentChunk)

    if document_id is not None:
        query = query.filter(DocumentChunk.document_id == document_id)

    if order_direction == "asc":
      query = query.order_by(distance_expression.asc())
    else:
      query = query.order_by(distance_expression.desc())

    query = query.limit(limit)

    try:
        results = db.execute(query).all()
    except Exception as e:
        logger.error(f"Error en la búsqueda de similitud: {e}")
        raise

    similar_chunks = [
        (row.DocumentChunk, convert_score(row.distance))
        for row in results
    ]

    return similar_chunks