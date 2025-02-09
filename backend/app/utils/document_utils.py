import datetime
import pypdf
from sentence_transformers import SentenceTransformer
from app.core.pinecone import get_pinecone_index
from sentence_transformers import SentenceTransformer
from typing import List
from textwrap import wrap
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
    pdf_reader = pypdf.PdfReader(pdf_file.file)
    text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text.strip()



def chunk_text(text: str, chunk_size: int = 300) -> List[str]:
    """
    Divide un texto largo en fragmentos más pequeños (chunks).
    Cada chunk tiene un tamaño máximo definido por chunk_size.
    """
    return wrap(text, width=chunk_size, break_long_words=False)


def insert_document_embeddings(document_id: int, teacher_id: int, title: str, description: str, text: str, batch_size: int = 100):
    """
    Divide el texto en fragmentos, genera embeddings y los inserta en Pinecone con metadatos.
    """
    index = get_pinecone_index()

    chunks = chunk_text(text)
    total_chunks = len(chunks)
    print(f"📌 Documento {document_id} dividido en {total_chunks} fragmentos.")

    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = embedding_model.encode(chunk).tolist()
        chunk_id = f"{document_id}_{i}"  

        vectors.append((chunk_id, embedding, {
        "document_id": document_id,
        "teacher_id": teacher_id,
        "title": title,
        "description": description,
        "chunk_index": i,
        "total_chunks": total_chunks,
        "created_at": str(datetime.datetime.now())  
    }))


    
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        print(f"📌 Subiendo batch {i // batch_size + 1}/{(len(vectors) // batch_size) + 1} a Pinecone...")
        index.upsert(vectors=batch, namespace="documents")


    print(f"✅ Documento {document_id} almacenado correctamente en Pinecone con metadatos.")
