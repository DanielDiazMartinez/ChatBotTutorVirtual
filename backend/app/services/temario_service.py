from sqlalchemy.orm import Session
from models.content_models import Temario
from models.chunk_models import Chunk
from utils.file_utils import extraer_texto_pdf
from services.embedding_service import generar_embedding
from pinecone_config import init_pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
import asyncio

def registrar_temario(db: Session, titulo: str, descripcion: str, archivo: str, profesor_id: int):
    """
    Registra un nuevo temario en la base de datos.
    """
    nuevo_temario = Temario(titulo=titulo, descripcion=descripcion, archivo=archivo, profesor_id=profesor_id)
    db.add(nuevo_temario)
    db.commit()
    db.refresh(nuevo_temario)
    return nuevo_temario

async def procesar_pdf_y_subir(db: Session, ruta_pdf: str, metadatos: dict):
    """
    Procesa un PDF, genera embeddings y los sube a Pinecone con los fragmentos de texto como metadatos.
    También guarda los chunks en la base de datos SQL para mantener la trazabilidad.
    """
    index = init_pinecone()

    # Extraer texto del PDF (bloqueante convertido a asíncrono)
    texto = await asyncio.to_thread(extraer_texto_pdf, ruta_pdf)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len
    )
    fragmentos = text_splitter.split_text(texto)

    items = []

    for i, fragmento in enumerate(fragmentos):
        if not fragmento.strip():
            continue

        # Generar embedding
        embedding = await asyncio.to_thread(generar_embedding, fragmento)

        pinecone_id = f"{metadatos['documento_id']}-{i}"
        
        # Crear el chunk en la base de datos
        chunk = Chunk(
            pinecone_id=pinecone_id,
            temario_id=metadatos['documento_id'],
            contenido=fragmento,
            orden=i
        )
        db.add(chunk)
        
        items.append({
            "id": pinecone_id,
            "values": embedding,
            "metadata": {
                "titulo": metadatos["titulo"],
                "documento_id": metadatos["documento_id"],
                "contenido": fragmento
            }
        })
    
    try:
        # Primero intentamos guardar en la base de datos SQL
        await asyncio.to_thread(db.commit)
        
        try:
            # Si el guardado en SQL fue exitoso, subimos a Pinecone
            await asyncio.to_thread(index.upsert, items)
        except Exception as e:
            # Si falla la subida a Pinecone, hacemos rollback de la base de datos
            await asyncio.to_thread(db.rollback)
            raise Exception(f"Error al subir a Pinecone: {str(e)}. Se ha revertido la transacción de la base de datos.")
            
    except Exception as e:
        # Si falla el guardado en SQL, no llegamos a subir a Pinecone
        await asyncio.to_thread(db.rollback)
        raise Exception(f"Error al guardar en la base de datos: {str(e)}")

    return f"Se han subido {len(items)} fragmentos del documento '{metadatos['titulo']}' a Pinecone y la base de datos."

async def eliminar_temario(db: Session, temario_id: int):
    """
    Elimina un temario de la base de datos y sus embeddings de Pinecone.
    """
    from pinecone_config import init_pinecone
    import os
    from models import Temario

    # Obtener el temario de la base de datos
    temario = db.query(Temario).filter(Temario.id == temario_id).first()
    if not temario:
        return None

    # Eliminar el archivo físico si existe
    if os.path.exists(temario.archivo):
        os.remove(temario.archivo)

    # Eliminar los embeddings de Pinecone
    index = init_pinecone()
    if index:
        # Eliminar todos los vectores asociados con este documento
        index.delete(filter={"documento_id": temario_id})

    # Eliminar el registro de la base de datos
    db.delete(temario)
    db.commit()

    return temario