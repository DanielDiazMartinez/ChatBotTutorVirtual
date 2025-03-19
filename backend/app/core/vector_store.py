from sqlalchemy.orm import Session
from app.models.models import DocumentChunk
from app.core.vector_types import CosineDistance, EuclideanDistance, InnerProduct
from typing import List, Tuple, Optional

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