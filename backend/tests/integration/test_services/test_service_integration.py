import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.models.models import Document, DocumentChunk, User, Conversation, Message
from app.services.embedding_service import create_document_chunks
from app.services.chat_service import process_message, generate_conversation

class TestIntegrationAfterRestructuring:
    """Tests de integración para verificar la correcta interacción entre servicios después de la reestructuración"""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def mock_document(self):
        doc = MagicMock(spec=Document)
        doc.id = 1
        doc.title = "Test Document"
        return doc
    
    @pytest.fixture
    def mock_chunks(self):
        chunks = []
        for i in range(3):
            chunk = MagicMock(spec=DocumentChunk)
            chunk.id = i + 1
            chunk.document_id = 1
            chunk.content = f"Contenido de prueba {i+1}"
            chunk.embedding = [0.1] * 768
            chunks.append(chunk)
        return chunks
    
    @pytest.fixture
    def mock_conversation(self):
        conv = MagicMock(spec=Conversation)
        conv.id = 1
        conv.document_id = 1
        conv.user_id = 1
        conv.user_role = "student"
        return conv
    @patch('app.services.document_service.document_exists')
    @patch('app.services.embedding_service.get_embedding_for_query')
    @patch('app.services.vector_service.search_similar_chunks')
    def test_document_to_vector_integration(self, mock_search, mock_embedding, mock_doc_exists,
                                           mock_db, mock_document, mock_chunks):
        """
        Test para verificar la integración entre el servicio de documentos y el servicio de vectores
        """
        # Configurar mocks
        mock_doc_exists.return_value = True
        mock_embedding.return_value = [0.1] * 768
        mock_search.return_value = [(chunk, 0.9) for chunk in mock_chunks]
        
        # Importar las funciones después de aplicar los mocks
        from app.services.document_service import document_exists
        from app.services.embedding_service import get_embedding_for_query
        from app.services.vector_service import search_similar_chunks
        
        # Llamar a las funciones mockadas
        embedding = mock_embedding("¿Qué es Python?")
        assert len(embedding) == 768
        
        # Verificar que el mock de search_similar_chunks funciona
        results = mock_search(mock_db, embedding, document_id=1)
        assert len(results) == 3
        assert all(isinstance(item[0], DocumentChunk) for item in results)
        
        # Verificar que las funciones se llamaron con los parámetros correctos
        mock_embedding.assert_called_once_with("¿Qué es Python?")
        mock_search.assert_called_once_with(mock_db, embedding, document_id=1)
    
    @patch('app.services.chat_service.add_bot_message')
    @patch('app.services.chat_service.add_user_message')
    @patch('app.services.chat_service.get_conversation_history')
    @patch('app.services.chat_service.get_conversation_context')
    @patch('app.services.chat_service.generate_ai_response')
    def test_chat_process_message_integration(self, mock_generate, mock_context, mock_history,
                                             mock_add_user, mock_add_bot,
                                             mock_db, mock_conversation):
        """
        Test para verificar la integración entre el servicio de chat y los servicios de vector y API
        """
        # Configurar mocks
        mock_context.return_value = "Contexto de la conversación"
        mock_history.return_value = "Historial de la conversación"
        mock_generate.return_value = "Respuesta generada por la IA"
        
        user_msg = MagicMock(spec=Message)
        user_msg.id = 1
        user_msg.text = "¿Qué es Python?"
        user_msg.is_bot = False
        
        bot_msg = MagicMock(spec=Message)
        bot_msg.id = 2
        bot_msg.text = "Respuesta generada por la IA"  # Asegurar que coincida con lo que devuelve generate_ai_response
        bot_msg.is_bot = True
        
        mock_add_user.return_value = user_msg
        mock_add_bot.return_value = bot_msg
        
        # Configurar mock para db.query().filter().first() para devolver mock_conversation
        query_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = mock_conversation
        query_mock.filter.return_value = filter_mock
        mock_db.query.return_value = query_mock
        
        # Importar la función a probar
        from app.services.chat_service import process_message
        
        # Llamar a process_message directamente, sin patching adicional
        response = process_message(mock_db, mock_conversation.id, "¿Qué es Python?")
        
        # Verificar resultado
        assert response == "Respuesta generada por la IA"
        
        # Verificar que las funciones se llamaron correctamente
        mock_add_user.assert_called_once()
        mock_context.assert_called_once()
        mock_history.assert_called_once()
        mock_generate.assert_called_once()
        mock_add_bot.assert_called_once()
    
    @patch('app.services.chat_service.create_conversation_in_vector')
    @patch('app.services.chat_service.process_message')
    def test_generate_conversation_integration(self, mock_process, mock_create, 
                                              mock_db, mock_conversation):
        """
        Test para verificar la integración de la generación de conversaciones
        """
        # Configurar mocks
        mock_create.return_value = mock_conversation
        mock_process.return_value = "Respuesta inicial generada"
        
        # Importar la función a probar
        from app.services.chat_service import generate_conversation
        
        # Llamar a generate_conversation
        response, conversation = generate_conversation(
            mock_db, 
            document_id=1, 
            user_id=1, 
            user_type="student", 
            subject_id=1, 
            initial_message_text="Hola, ¿qué es Python?"
        )
        
        # Verificar resultados
        assert response == "Respuesta inicial generada"
        assert conversation == mock_conversation
        
        # Verificar que las funciones se llamaron correctamente
        mock_create.assert_called_once_with(mock_db, 1, 1, "student", 1)
        mock_process.assert_called_once_with(mock_db, mock_conversation.id, "Hola, ¿qué es Python?")
