from sentence_transformers import SentenceTransformer

# Inicializa el modelo Hugging Face
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generar_embedding(texto: str):
    """
    Genera un embedding a partir de texto usando Sentence Transformers.
    """
    return model.encode(texto).tolist()
