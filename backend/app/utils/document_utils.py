import pypdf
from sentence_transformers import SentenceTransformer

# Inicializar el modelo de embeddings (se carga solo una vez)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str):
    """
    Genera un embedding a partir del contenido del texto.
    """
    return embedding_model.encode(text).tolist()

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrae el texto de un archivo PDF.
    """
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text.strip()
