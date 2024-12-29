from sqlalchemy.orm import Session
from models.content_models import Temario
from utils.file_utils import extraer_texto_pdf, dividir_texto
from services.embedding_service import generar_embedding
from pinecone_config import init_pinecone

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
    Procesa un PDF, genera embeddings y los sube a Pinecone.
    """
    index = init_pinecone()

    # Extraer texto del PDF
    texto = extraer_texto_pdf(ruta_pdf)

    # Dividir texto en fragmentos y generar embeddings
    fragmentos = dividir_texto(texto, max_tokens=512)
    items = []
    for i, fragmento in enumerate(fragmentos):
        embedding = generar_embedding(fragmento)
        items.append({
            "id": f"{metadatos['documento_id']}-{i}",
            "values": embedding.tolist(),
            "metadata": metadatos
        })
    
    # Subir a Pinecone
    index.upsert(items)
