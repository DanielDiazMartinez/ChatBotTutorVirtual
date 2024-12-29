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
    resultados = index.query(embedding, top_k=3, include_metadata=True)
    return resultados
