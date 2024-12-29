import pinecone
import os

def init_pinecone():
    """
    Inicializa la conexión con Pinecone y asegura que el índice está configurado.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    pinecone.init(api_key=api_key, environment=environment)

    index_name = os.getenv("PINECONE_INDEX", "temarios-index")
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=384)  # Dimensión típica de embeddings
    return pinecone.Index(index_name)
