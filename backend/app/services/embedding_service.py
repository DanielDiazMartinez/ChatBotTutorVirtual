from typing import List
from sentence_transformers import SentenceTransformer
import torch
import logging
from llama_index.core.node_parser import SentenceSplitter  # Importamos SentenceSplitter
from llama_index.core import Document
from sqlalchemy.orm import Session
from ..models.models import DocumentChunk
import nltk  # Importamos nltk
import numpy as np

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Instancia global del modelo (singleton)
sentence_transformer_model_instance = None
#EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'  # Modelo más eficiente

EMBEDDING_MODEL_NAME = 'all-distilroberta-v1'  # Modelo más potente
def load_sentence_transformer_model_singleton(model_name: str = EMBEDDING_MODEL_NAME):
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

def semantic_split_text(
    text: str,
    model: SentenceTransformer,
    similarity_threshold: float = 0.7,
    max_chunk_length: int = 512,
) -> List[str]:
    """
    Divide semánticamente un texto en chunks más pequeños usando similitud de embeddings.
    """
    if not text or len(text.strip()) == 0:
        return []

    try:
        nltk.data.find("tokenizers/punkt")
        nltk.data.find("tokenizers/punkt_tab/english/")
    except LookupError:
        nltk.download("punkt")
        nltk.download("punkt_tab")

    sentences = nltk.tokenize.sent_tokenize(text)  # Usamos nltk para dividir en oraciones
    embeddings = model.encode(sentences)

    chunks = []
    current_chunk = ""
    current_chunk_len = 0

    for i, sentence in enumerate(sentences):
        if current_chunk_len + len(sentence) <= max_chunk_length:
            if current_chunk:
                similarity = np.dot(embeddings[i - 1], embeddings[i]) / (
                    np.linalg.norm(embeddings[i - 1]) * np.linalg.norm(embeddings[i])
                )
                if similarity >= similarity_threshold:
                    current_chunk += " " + sentence
                    current_chunk_len += len(sentence)
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence
                    current_chunk_len = len(sentence)
            else:
                current_chunk = sentence
                current_chunk_len = len(sentence)
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
            current_chunk_len = len(sentence)

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

    # Cargar el modelo *una vez* al inicio (o usar el singleton)
    model = load_sentence_transformer_model_singleton()

    # Dividir el texto en chunks semánticos
    chunks = semantic_split_text(text, model)

    if not chunks:
        logger.warning(f"No se pudieron crear chunks para el documento {document_id}")
        return []

  
    embeddings = model.encode(chunks)  
    print(f"Chunks: {embeddings}")
    db_chunks = []
    for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        chunk = DocumentChunk(
            document_id=document_id,
            content=chunk_text,
            embedding=embedding.tolist(),
            chunk_number=i,
        )
        db_chunks.append(chunk)

    # Guardar en la base de datos
    db.add_all(db_chunks)
    db.flush()
    db.commit()
    logger.info(f"Guardados {len(db_chunks)} chunks para el documento {document_id}")
    return db_chunks