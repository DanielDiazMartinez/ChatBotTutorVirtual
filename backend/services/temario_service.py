from sqlalchemy.orm import Session
from models.content_models import Temario
from utils.file_utils import extraer_texto_pdf, dividir_texto
from services.embedding_service import generar_embedding
from pinecone_config import init_pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter

def registrar_temario(db: Session, titulo: str, descripcion: str, archivo: str, profesor_id: int):
    """
    Registra un nuevo temario en la base de datos.
    """
    nuevo_temario = Temario(titulo=titulo, descripcion=descripcion, archivo=archivo, profesor_id=profesor_id)
    db.add(nuevo_temario)
    db.commit()
    db.refresh(nuevo_temario)
    return nuevo_temario

def procesar_pdf_y_subir(ruta_pdf, metadatos):
    """
    Procesa un PDF, genera embeddings y los sube a Pinecone con los fragmentos de texto como metadatos.
    """
    index = init_pinecone()

    # Extraer texto del PDF
    texto = extraer_texto_pdf(ruta_pdf)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len
        )
    
    fragmentos = text_splitter.split_text(texto)

    items = []
    for i, fragmento in enumerate(fragmentos):
        # Evitar fragmentos vacíos
        if not fragmento.strip():
            continue

        embedding = generar_embedding(fragmento)

        items.append({
            "id": f"{metadatos['documento_id']}-{i}",
            "values": embedding,
            "metadata": {
                "titulo": metadatos["titulo"],
                "documento_id": metadatos["documento_id"],
                "contenido": fragmento
            }
        })
    
    # Subir a Pinecone
    index.upsert(items)

    return f"Se han subido {len(items)} fragmentos del documento '{metadatos['titulo']}' a Pinecone."