from pinecone_config import init_pinecone
from services.embedding_service import generar_embedding

def consultar_pinecone(pregunta: str):
    """
    Genera un embedding para la pregunta y consulta Pinecone.
    """
    index = init_pinecone()

    # Generar embedding de la pregunta
    embedding = generar_embedding(pregunta)

    # Realizar consulta a Pinecone
    resultados = index.query ( 
        vector=embedding,  # Tu vector de consulta (debe ser una lista o array)
        top_k=3,                   # Número de resultados más cercanos que quieres
        include_metadata=True,      # Para incluir metadatos en los resultados
    )
  # Procesar resultados en un formato JSON serializable
    processed_resultados = [
        {
            "id": match.id,  # Extraer el ID
            "score": match.score,  # Extraer el score
            "metadata": match.metadata  # Extraer los metadatos
        }
        for match in resultados["matches"]
    ]

    return {"matches": processed_resultados}