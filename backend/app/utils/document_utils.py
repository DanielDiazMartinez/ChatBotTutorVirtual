import pypdf
from sentence_transformers import SentenceTransformer
import torch
import logging
from typing import List
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core import Document

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.services.embedding_service import load_sentence_transformer_model_singleton as load_embedding_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_sentence_transformer_model_singleton(model_name: str = 'multi-qa-mpnet-base-dot-v1'):
    """
    Usa el modelo singleton del servicio de embedding para mantener consistencia.
    Esta función se mantiene para compatibilidad con el código existente.
    """
    return load_embedding_model(model_name)

def extract_text_from_pdf(pdf_file) -> str:
    try:
        pdf_reader = pypdf.PdfReader(pdf_file.file)
        text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        return text.strip()
    except Exception as e:
        logger.error(f"Error al extraer texto del PDF: {e}", exc_info=True)
        return ""

def process_document_and_embed_chunks_semantic(document_id: int, text: str, db, model_name_for_embedding: str = 'multi-qa-mpnet-base-dot-v1'):
    st_encoder_model = load_sentence_transformer_model_singleton(model_name=model_name_for_embedding)
    if st_encoder_model is None:
        logger.error("No se puede procesar el documento porque el modelo SentenceTransformer para codificación no está cargado.")
        return []

    logger.info(f"Iniciando chunking semántico para el documento ID: {document_id}...")

    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        llama_index_embed_model = HuggingFaceEmbedding(
            model_name=model_name_for_embedding,
            device=device,
        )
        logger.info(f"Modelo de embedding LlamaIndex ({model_name_for_embedding}) preparado para SemanticSplitterNodeParser en dispositivo: {device}.")
    except Exception as e:
        logger.error(f"Error al inicializar LlamaIndex HuggingFaceEmbedding para SemanticSplitter: {e}", exc_info=True)
        return []

    try:
        semantic_splitter = SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=llama_index_embed_model,
        )
    except Exception as e:
        logger.error(f"Error al inicializar SemanticSplitterNodeParser: {e}", exc_info=True)
        return []

    llama_document = Document(text=text, doc_id=str(document_id))
    try:
        nodes = semantic_splitter.get_nodes_from_documents([llama_document])
    except Exception as e:
        logger.error(f"Error durante la división semántica con get_nodes_from_documents: {e}", exc_info=True)
        return []
        
    raw_chunks_content_list = [node.get_content() for node in nodes]

    chunks_content_list = []
    for chunk_text in raw_chunks_content_list:
        cleaned_text = chunk_text.strip()
        if cleaned_text and len(cleaned_text.split()) > 5:
            chunks_content_list.append(cleaned_text)
        else:
            logger.info(f"Chunk semántico descartado para doc {document_id} por ser demasiado corto o vacío tras strip: '{cleaned_text[:50]}...'")

    logger.info(f"Documento ID: {document_id} dividido en {len(chunks_content_list)} chunks semánticos válidos.")

    if not chunks_content_list:
        logger.warning(f"No se generaron chunks válidos para el documento ID: {document_id} después del filtrado.")
        return []

    logger.info(f"Generando embeddings en batch para {len(chunks_content_list)} chunks del documento ID: {document_id}...")
    try:
        all_embeddings_np = st_encoder_model.encode(
            chunks_content_list,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        logger.info(f"Embeddings generados para el documento ID: {document_id}.")
    except Exception as e:
        logger.error(f"Error al generar embeddings con SentenceTransformer: {e}", exc_info=True)
        return []

    from app.models.models import DocumentChunk

    created_chunks_in_db = []
    logger.info(f"Guardando {len(chunks_content_list)} chunks y embeddings en la base de datos para el documento ID: {document_id}...")

    for i, (chunk_content, embedding_np) in enumerate(zip(chunks_content_list, all_embeddings_np)):
        embedding_list = embedding_np.tolist()

        db_chunk_entry = DocumentChunk(
            document_id=document_id,
            content=chunk_content,
            embedding=embedding_list,
            chunk_number=i
        )
        db.add(db_chunk_entry)
        created_chunks_in_db.append(db_chunk_entry)
    
    logger.info(f"Proceso completado para documento ID: {document_id}. {len(created_chunks_in_db)} chunks preparados para añadir a la sesión de BBDD.")
    return created_chunks_in_db

def get_embedding_for_query(query: str, model_name: str = 'multi-qa-mpnet-base-dot-v1') -> List[float]:
    """
    Obtiene el embedding para una consulta de usuario.

    Args:
        query: La pregunta del usuario.
        model_name: El nombre del modelo de embedding a utilizar.

    Returns:
        El embedding como una lista de floats, o una lista vacía en caso de error.
    """
    try:
        # Reutiliza el singleton para cargar el modelo SentenceTransformer
        embedding_model = load_sentence_transformer_model_singleton(model_name=model_name)
        if not embedding_model:
            logger.error(f"Modelo de embedding '{model_name}' no pudo ser cargado.")
            return []

        logger.info(f"Generando embedding para la consulta: \"{query[:100]}...\"")
        # El método .encode() de SentenceTransformer puede tomar un string o una lista de strings.
        # Para una sola consulta, devuelve directamente el array del embedding.
        query_embedding_np = embedding_model.encode(query, convert_to_numpy=True)
        query_embedding_list = query_embedding_np.tolist()
        logger.info("Embedding de consulta generado exitosamente.")
        return query_embedding_list
    except Exception as e:
        logger.error(f"Error generando embedding para la consulta '{query}': {e}", exc_info=True)
        return []