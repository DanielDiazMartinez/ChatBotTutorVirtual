"""
Servicio de embeddings - Capa base de infraestructura
Este servicio maneja la generación de embeddings y operaciones vectoriales básicas.
No debe depender de ningún otro servicio.
"""
from typing import List
from sentence_transformers import SentenceTransformer
import torch
import logging
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core import Document
from sqlalchemy.orm import Session
from ..models.models import DocumentChunk

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Instancia global del modelo (singleton)
sentence_transformer_model_instance = None

def load_sentence_transformer_model_singleton(model_name: str = 'multi-qa-mpnet-base-dot-v1'):
    """
    Carga el modelo SentenceTransformer como un singleton para evitar 
    múltiples cargas del mismo modelo.
    """
    global sentence_transformer_model_instance
    if sentence_transformer_model_instance is None:
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Cargando modelo SentenceTransformer: {model_name} en dispositivo: {device} para codificación de chunks.")
            sentence_transformer_model_instance = SentenceTransformer(model_name, device=device)
            logger.info("Modelo SentenceTransformer cargado exitosamente para codificación.")
        except Exception as e:
            logger.error(f"Error al cargar el modelo SentenceTransformer {model_name}: {e}", exc_info=True)
            raise
    return sentence_transformer_model_instance

def get_embedding_for_query(text: str) -> List[float]:
    """
    Genera un embedding para un texto dado utilizando el modelo SentenceTransformer.
    """
    model = load_sentence_transformer_model_singleton()
    if not text:
        return []
    
    embedding = model.encode(text)
    return embedding.tolist()

def semantic_split_text(text: str) -> List[str]:
    """
    Divide semánticamente un texto en chunks más pequeños.
    """
    if not text or len(text.strip()) == 0:
        return []
    
    try:
        # Usando el parser semántico de LlamaIndex
        semantic_splitter = SemanticSplitterNodeParser.from_defaults()
        nodes = semantic_splitter.get_nodes_from_documents([Document(text=text)])
        return [node.get_content() for node in nodes]
    except Exception as e:
        logger.error(f"Error al dividir semánticamente el texto: {e}", exc_info=True)
        # Fallback a una división simple si falla el parser semántico
        sentences = text.split(". ")
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= 1024:
                current_chunk += sentence + ". "
            else:
                chunks.append(current_chunk)
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

def create_document_chunks(db: Session, document_id: int, text: str) -> List[DocumentChunk]:
    """
    Divide el texto de un documento en chunks semánticos, genera embeddings para cada uno
    y los almacena en la base de datos.
    """
    if not text:
        return []
    
    # Dividir el texto en chunks semánticos
    chunks = semantic_split_text(text)
    
    if not chunks:
        logger.warning(f"No se pudieron crear chunks para el documento {document_id}")
        return []
    
    # Obtener embeddings para todos los chunks
    model = load_sentence_transformer_model_singleton()
    embeddings = model.encode(chunks)
    
    # Crear objetos DocumentChunk
    db_chunks = []
    for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        chunk = DocumentChunk(
            document_id=document_id,
            content=chunk_text,
            embedding=embedding.tolist(),
            chunk_number=i
        )
        db_chunks.append(chunk)
    
    # Guardar en la base de datos
    db.add_all(db_chunks)
    db.flush()
    
    return db_chunks
