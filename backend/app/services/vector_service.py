from sqlalchemy.orm import Session
from app.models.models import Document, DocumentChunk,CosineDistance, EuclideanDistance, InnerProduct
from app.utils.document_utils import  chunk_text,generate_embedding
from typing import List, Tuple, Optional

def insert_document_chunks(
    db: Session,
    document_id: int,
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[DocumentChunk]:
    """
    Divide el texto de un documento en chunks, genera embeddings para cada uno
    y los inserta en la base de datos usando pgvector.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento al que pertenecen los chunks
        text: Texto completo del documento
        chunk_size: Tamaño de cada chunk en caracteres
        overlap: Cantidad de caracteres de superposición entre chunks
        
    Returns:
        Lista de objetos DocumentChunk creados
    """
    # Recuperar el documento para asegurarse de que existe
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"No existe un documento con ID {document_id}")
    
    # Dividir el texto en chunks
    chunks = chunk_text(text, chunk_size=chunk_size)
    
    created_chunks = []
    
    
    for i, chunk_content in enumerate(chunks):
        
        embedding = generate_embedding(chunk_content)
        
        
        chunk = DocumentChunk(
            document_id=document_id,
            content=chunk_content,
            embedding=embedding,
            chunk_number=i
        )
        
        # Añadirlo a la sesión
        db.add(chunk)
        created_chunks.append(chunk)
    
    # Guardar todos los chunks en la base de datos
    db.commit()
    
    print(f"Se insertaron {len(created_chunks)} chunks para el documento ID {document_id}")
    
    return created_chunks

def search_similar_chunks(db: Session, 
                          query_embedding: List[float], 
                          document_id: Optional[int] = None, 
                          limit: int = 5,
                          similarity_metric: str = "cosine") -> List[Tuple[DocumentChunk, float]]:
    """
    Busca chunks similares a un embedding de consulta usando pgvector
    
    Args:
        db: Sesión de SQLAlchemy
        query_embedding: Vector de embedding de la consulta
        document_id: ID del documento para filtrar (opcional)
        limit: Número máximo de resultados
        similarity_metric: Métrica de similitud ("cosine", "l2", o "dot")
        
    Returns:
        Lista de tuplas (chunk, score de similitud)
    """
    from sqlalchemy import select
    
    # Seleccionar la función de distancia
    if similarity_metric == "cosine":
        distance_func = CosineDistance
        # Para coseno, menor distancia = mayor similitud
        convert_score = lambda x: 1.0 - x  # Convertir distancia a similitud
    elif similarity_metric == "l2":
        distance_func = EuclideanDistance
        # Para L2, menor distancia = mayor similitud, pero no tiene límite superior
        convert_score = lambda x: 1.0 / (1.0 + x)
    else:  # dot product
        distance_func = InnerProduct
        # Para producto escalar, mayor valor = mayor similitud
        convert_score = lambda x: -x
    
    # Construir la consulta
    query = select(
        DocumentChunk,
        distance_func(DocumentChunk.embedding, query_embedding).label("distance")
    )
    
    # Filtrar por documento si se especifica
    if document_id:
        query = query.filter(DocumentChunk.document_id == document_id)
    
    # Ordenar por similitud
    query = query.order_by(distance_func(DocumentChunk.embedding, query_embedding))
    
    # Limitar resultados
    query = query.limit(limit)
    
    # Ejecutar la consulta
    results = db.execute(query).all()
    
    # Convertir resultados
    return [(chunk, convert_score(distance)) for chunk, distance in results]