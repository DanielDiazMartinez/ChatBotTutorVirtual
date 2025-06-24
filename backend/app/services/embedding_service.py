from typing import List
from sentence_transformers import SentenceTransformer
import torch
import logging
from llama_index.core.node_parser import SentenceSplitter  # Importamos SentenceSplitter
from llama_index.core import Document
from sqlalchemy.orm import Session
from app.crud import crud_document_chunk
from app.models.models import DocumentChunk
import nltk  # Importamos nltk
import numpy as np

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Instancia global del modelo (singleton)
sentence_transformer_model_instance = None
# Modelos por dimensiones:
# all-MiniLM-L6-v2: 384 dimensiones (eficiente, más rápido)
# all-mpnet-base-v2: 768 dimensiones (balance)
# all-distilroberta-v1: ~768 dimensiones (potente, más preciso)
# text-embedding-ada-002: 1536 dimensiones (alta precisión)
# e5-large-v2: 1024 dimensiones (reciente, alta precisión)

EMBEDDING_MODEL_NAME = 'all-mpnet-base-v2'  # Usar modelo de mejor calidad
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
    if not text or text.strip() == "":
        logger.warning("Se solicitó embedding para texto vacío")
        return []
    
    try:
        model = load_sentence_transformer_model_singleton()
        logger.info(f"Generando embedding para consulta: '{text[:50]}...' (longitud: {len(text)})")
        
        # Procesar el texto para mejorar resultados
        processed_text = text.strip()
        
        # Generar embedding
        embedding = model.encode(processed_text)
        
        # Verificar dimensiones del embedding
        embedding_list = embedding.tolist()
        embedding_dim = len(embedding_list)
        logger.info(f"Embedding generado correctamente: dimensión={embedding_dim}")
        
        return embedding_list
    except Exception as e:
        logger.error(f"Error al generar embedding para consulta: {e}")
        return []

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

    # Generar embeddings para todos los chunks
    embeddings = model.encode(chunks)  
    print(f"Chunks: {embeddings}")
    
    # Preparar datos para la capa CRUD
    chunks_data = []
    for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_data = {
            'document_id': document_id,
            'content': chunk_text,
            'embedding': embedding.tolist(),
            'chunk_number': i
        }
        chunks_data.append(chunk_data)

    # Guardar en la base de datos usando CRUD
    db_chunks = crud_document_chunk.create_document_chunks(db, chunks_data)
    logger.info(f"Guardados {len(db_chunks)} chunks para el documento {document_id}")
    return db_chunks