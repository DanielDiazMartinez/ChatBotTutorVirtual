import pytest
from unittest.mock import patch, MagicMock
import io
import numpy as np

from app.utils.document_utils import extract_text_from_pdf
from app.services.embedding_service import (
    load_sentence_transformer_model_singleton, 
    get_embedding_for_query,
    semantic_split_text,
    create_document_chunks
)

@pytest.fixture
def mock_pdf_file():
    """
    Crea un mock de un archivo PDF para pruebas
    """
    content = b"%PDF-1.4\nMock PDF Content\nThis is a test PDF file."
    mock_file = MagicMock()
    mock_file.file = io.BytesIO(content)
    mock_file.filename = "test_document.pdf"
    return mock_file

@pytest.fixture
def mock_db_session():
    return MagicMock()

class TestDocumentUtils:
    """Tests para funciones de extracción de texto y procesamiento de documentos"""
    
    @patch('pypdf.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader, mock_pdf_file):
        """
        Test para verificar que la función extract_text_from_pdf funciona correctamente
        """
        # Configurar el mock
        mock_reader_instance = MagicMock()
        mock_pdf_reader.return_value = mock_reader_instance
        
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Página 1 de prueba"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Página 2 de prueba"
        
        mock_reader_instance.pages = [mock_page1, mock_page2]
        
        # Llamar a la función
        result = extract_text_from_pdf(mock_pdf_file)
        
        # Verificar resultado
        assert result == "Página 1 de prueba Página 2 de prueba"
        mock_pdf_reader.assert_called_once_with(mock_pdf_file.file)
        
class TestEmbeddingService:
    """Tests para el servicio de embeddings"""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_load_sentence_transformer_model_singleton(self, mock_st):
        """Test para el patrón singleton del modelo de transformers"""
        # Primero, resetear la variable global para la prueba
        import app.services.embedding_service
        app.services.embedding_service.sentence_transformer_model_instance = None
        
        # Configurar el mock
        mock_model = MagicMock()
        mock_st.return_value = mock_model
        
        # Llamar a la función dos veces
        model1 = load_sentence_transformer_model_singleton()
        model2 = load_sentence_transformer_model_singleton()
        
        # Verificar que solo se crea una instancia
        assert model1 == model2
        mock_st.assert_called_once()
    
    @patch('app.services.embedding_service.load_sentence_transformer_model_singleton')
    def test_get_embedding_for_query(self, mock_load_model):
        """Test para obtener embeddings de consultas"""
        # Configurar el mock
        mock_model = MagicMock()
        mock_embedding = np.random.rand(768)
        mock_model.encode.return_value = mock_embedding
        mock_load_model.return_value = mock_model
        
        # Llamar a la función
        result = get_embedding_for_query("¿Qué es Python?")
        
        # Verificar resultado
        assert isinstance(result, list)
        assert len(result) == 768
        mock_model.encode.assert_called_once_with("¿Qué es Python?")
    
    @patch('nltk.tokenize.sent_tokenize')
    @patch('app.services.embedding_service.load_sentence_transformer_model_singleton')
    def test_semantic_split_text(self, mock_load_model, mock_sent_tokenize):
        """Test para la división semántica de textos"""
        # Configurar el mock
        mock_sent_tokenize.return_value = ["Oración 1.", "Oración 2."]
        
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_load_model.return_value = mock_model
        
        # Llamar a la función
        result = semantic_split_text(
            text="Este es un texto de prueba que debería dividirse en chunks.",
            model=mock_model
        )
        
        # Verificar resultado
        assert len(result) > 0  # Al menos debería devolver algún chunk
        mock_sent_tokenize.assert_called_once_with("Este es un texto de prueba que debería dividirse en chunks.")
    
    @patch('app.services.embedding_service.semantic_split_text')
    @patch('app.services.embedding_service.load_sentence_transformer_model_singleton')
    def test_create_document_chunks(self, mock_load_model, mock_split, mock_db_session):
        """Test para la creación de chunks de documento"""
        # Configurar los mocks
        mock_split.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
        
        mock_model = MagicMock()
        mock_embeddings = np.random.rand(3, 768)
        mock_model.encode.return_value = mock_embeddings
        mock_load_model.return_value = mock_model
        
        # Llamar a la función
        chunks = create_document_chunks(mock_db_session, 1, "Este es un texto de prueba.")
        
        # Verificar resultado
        assert mock_db_session.add_all.called
        assert mock_db_session.flush.called
        mock_split.assert_called_once_with("Este es un texto de prueba.", mock_model)
        mock_model.encode.assert_called_once()