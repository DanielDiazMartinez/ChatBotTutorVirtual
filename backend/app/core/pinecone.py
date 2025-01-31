import pinecone
from .config import settings

def init_pinecone():
    pinecone.init(
        api_key=settings.PINECONE_API_KEY,
        environment=settings.PINECONE_ENVIRONMENT
    )
    return pinecone.Index(settings.PINECONE_INDEX)
