import pinecone
import os

import os
from pinecone import Pinecone, ServerlessSpec

def init_pinecone():
    
    api_key = os.environ.get("PINECONE_API_KEY")
    environment = os.environ.get("PINECONE_ENVIRONMENT")  

    
    pc = Pinecone(api_key=api_key)

    # Configura tu índice, si no existe
    index_name = "bbddvector" # TODO: Meter esto en .env

    if index_name not in pc.list_indexes().names():
        print(f"[WARNING] El índice '{index_name}' no existe en Pinecone. Verifica la configuración o crea el índice manualmente.")
        return None  

       

    return pc.Index(index_name)
