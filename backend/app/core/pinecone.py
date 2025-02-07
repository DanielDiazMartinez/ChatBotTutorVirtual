
from pinecone import Pinecone, ServerlessSpec
from .config import settings


pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT) 

def get_pinecone_index():
    """
    Obtiene o crea el índice de Pinecone correctamente.
    """
    index_name = "bbddvector"

    print(pc.list_indexes().names())
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536, 
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-west-2") 
        )

    return pc.Index(index_name) 