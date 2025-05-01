import pypdf
from sentence_transformers import SentenceTransformer
import torch
import logging
from typing import List
from transformers import AutoTokenizer
from ..models.models import DocumentChunk 

model_name = 'multi-qa-mpnet-base-dot-v1'


embedding_model = None

def load_embedding_model():
    """Carga el modelo de embedding asegurándose de usar la GPU si está disponible."""
    global embedding_model
    if embedding_model is None:
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logging.info(f"Cargando modelo de embedding: {model_name} en dispositivo: {device}")
            
            embedding_model = SentenceTransformer(model_name, device=device)
            logging.info("Modelo de embedding cargado exitosamente.")
        except Exception as e:
            logging.error(f"Error al cargar el modelo de embedding {model_name}: {e}", exc_info=True)
          
            raise 
    return embedding_model

def generate_embedding(text: str):
    """
    Genera un embedding para UN SOLO texto.
    Nota: Es más eficiente usar model.encode() con una lista de textos.
    """
    model = load_embedding_model() 
    if model:
        
        embedding = model.encode(text)
        
        return embedding.tolist()
    else:
        
        return None

def process_document_and_embed_chunks(document_id: int, text: str, db, chunk_size: int = 256):
    """
    Divide un documento en chunks, genera embeddings en batch y los guarda en la BBDD.

    Args:
        document_id: ID del documento.
        text: Contenido del documento.
        db: Sesión/conexión de la base de datos.
        chunk_size: Tamaño de chunk para la función de chunking.
    """
    global embedding_model 

    load_embedding_model()
    if embedding_model is None:
        logging.error("No se puede procesar el documento porque el modelo de embedding no está cargado.")
        return []


    logging.info(f"Chunking documento ID: {document_id}...")
    chunks_content_list: List[str] = chunk_text_by_tokens_hf(text, chunk_size=chunk_size)
    logging.info(f"Documento ID: {document_id} dividido en {len(chunks_content_list)} chunks.")

    if not chunks_content_list:
        logging.warning(f"No se generaron chunks para el documento ID: {document_id}.")
        return []

    
    logging.info(f"Generando embeddings en batch para {len(chunks_content_list)} chunks...")
    
    all_embeddings = embedding_model.encode(
        chunks_content_list,
        batch_size=32, 
        show_progress_bar=True, 
        convert_to_numpy=True 
    )
    logging.info("Embeddings generados.")

 
    created_chunks = []
    logging.info("Guardando chunks y embeddings en la base de datos...")
    
    for i, (chunk_content, embedding_np) in enumerate(zip(chunks_content_list, all_embeddings)):
        
        embedding_list = embedding_np.tolist()

        chunk = DocumentChunk(
            document_id=document_id,
            content=chunk_content,
            embedding=embedding_list,
            chunk_number=i
        )

        db.add(chunk)
        created_chunks.append(chunk) 

    logging.info(f"Proceso completado para documento ID: {document_id}. {len(created_chunks)} chunks añadidos a la sesión.")
    return created_chunks 

TOKENIZER_FOR_EMBEDDING_MODEL = 'sentence-transformers/multi-qa-mpnet-base-dot-v1'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def chunk_text_by_tokens_hf(
    text: str,
    tokenizer_name: str = TOKENIZER_FOR_EMBEDDING_MODEL, 
    chunk_size: int = 256, # Tamaño objetivo en TOKENS 
    chunk_overlap: int = 32 # Solapamiento en TOKENS 
) -> List[str]:
    """
    Divide texto en chunks basados en tokens usando el tokenizador ESPECÍFICO
    del modelo sentence-transformer 'multi-qa-mpnet-base-dot-v1', con solapamiento.

    Args:
        text: El texto a dividir.
        tokenizer_name: Identificador del tokenizador en Hugging Face Hub.
                        Por defecto, usa el de multi-qa-mpnet-base-dot-v1.
        chunk_size: Tamaño objetivo de cada chunk (en tokens de este tokenizador).
        chunk_overlap: Número de tokens de solapamiento entre chunks.

    Returns:
        Lista de fragmentos de texto (chunks). O lista vacía si hay error.
    """
    try:
        # Cargar el tokenizador específico
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        logger.info(f"Tokenizador '{tokenizer_name}' cargado para chunking.")

    except Exception as e:
        logger.error(f"Error al cargar el tokenizador '{tokenizer_name}' para chunking: {e}", exc_info=True)
        return [] # Retorna lista vacía en caso de error

    # Tokenizar el texto completo sin añadir tokens especiales (BOS/EOS)
    # para un conteo limpio al dividir.
    try:
        tokens = tokenizer.encode(text, add_special_tokens=False)
    except Exception as e:
        logger.error(f"Error al tokenizar el texto con '{tokenizer_name}': {e}", exc_info=True)
        return []

    num_tokens = len(tokens)

    if num_tokens == 0:
        logger.warning("El texto de entrada no produjo tokens con este tokenizador.")
        return []

    chunks = []
    current_pos = 0

    while current_pos < num_tokens:
        # Define el final del chunk actual
        end_pos = min(current_pos + chunk_size, num_tokens)

        # Obtiene los tokens para este chunk
        chunk_tokens = tokens[current_pos:end_pos]

        # Decodifica los tokens de vuelta a texto
        try:
            chunk_text = tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True # Ajusta espacios
            )
        except Exception as e:
            logger.error(f"Error al decodificar tokens: {chunk_tokens}. Error: {e}", exc_info=True)
            # Decide si continuar o parar; aquí continuamos al siguiente chunk
            chunk_text = "" # Asigna texto vacío para este chunk problemático

        # Añadir el chunk solo si contiene texto útil
        if chunk_text and not chunk_text.isspace():
             chunks.append(chunk_text)

        # Calcula la posición de inicio del siguiente chunk
        next_start_pos = current_pos + chunk_size - chunk_overlap

        # Medida de seguridad: Asegurar avance para evitar bucles infinitos
        if next_start_pos <= current_pos:
             current_pos += 1
        else:
             current_pos = next_start_pos

    logger.info(f"Chunking completado. Generados {len(chunks)} chunks.")
    return chunks

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrae el texto de un archivo PDF.
    """
    pdf_reader = pypdf.PdfReader(pdf_file.file)
    text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text.strip()
