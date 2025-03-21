import pypdf
from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer
from typing import List
from textwrap import wrap
# Inicializar el modelo de embeddings (se carga solo una vez)
embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
def generate_embedding(text: str):
    """
    Genera un embedding a partir del contenido del texto.
    """
    return embedding_model.encode(text).tolist()

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrae el texto de un archivo PDF.
    """
    pdf_reader = pypdf.PdfReader(pdf_file.file)
    text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text.strip()



def chunk_text(text: str, chunk_size: int = 300) -> List[str]:
    """
    Divide un texto largo en fragmentos más pequeños (chunks).
    Cada chunk tiene un tamaño máximo definido por chunk_size.
    """
    return wrap(text, width=chunk_size, break_long_words=False)


