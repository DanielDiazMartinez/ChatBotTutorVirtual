import pytest
from unittest.mock import patch, MagicMock

from app.services.api_service import generate_ai_response

class TestApiService:
    """Tests para el servicio de API (Google AI)"""
    
    @patch('app.services.api_service.google_client')
    def test_generate_ai_response(self, mock_google_client):
        """Test para generación de respuestas a través de la API de Google AI"""
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.text = "Python es un lenguaje de programación interpretado de alto nivel."
        
        mock_google_client.generate_content.return_value = mock_response
        
        # Llamar a la función
        result = generate_ai_response(
            user_question="¿Qué es Python?",
            context="Python es un lenguaje de programación",
            conversation_history="Usuario: Hola\nBot: Hola, ¿en qué puedo ayudarte?",
            user_id="test_user",
            conversation_id=1
        )
        
        # Verificar resultado
        assert result == "Python es un lenguaje de programación interpretado de alto nivel."
        mock_google_client.generate_content.assert_called_once()
        
        # Verificar que los parámetros incluyen el contexto y la conversación
        args, kwargs = mock_google_client.generate_content.call_args
        prompt = args[0]
        assert "Python es un lenguaje de programación" in prompt
        assert "Usuario: Hola\nBot: Hola, ¿en qué puedo ayudarte?" in prompt
    
    @patch('app.services.api_service.google_client', None)
    def test_generate_ai_response_with_no_client(self):
        """Test para manejo de error cuando no hay cliente Google AI configurado"""
        result = generate_ai_response(
            user_question="¿Qué es Python?",
            context="Python es un lenguaje de programación",
            conversation_history="",
            user_id="test_user",
            conversation_id=2
        )
        
        assert "Lo siento, la configuración del servicio de IA no es correcta" in result
    
    @patch('app.services.api_service.google_client')
    def test_generate_ai_response_api_error(self, mock_google_client):
        """Test para manejo de errores de la API"""
        # Configurar el mock para lanzar una excepción
        error = Exception("API quota exceeded")
        mock_google_client.generate_content.side_effect = error
        
        # Llamar a la función
        result = generate_ai_response(
            user_question="¿Qué es Python?",
            context="Python es un lenguaje de programación",
            conversation_history="",
            user_id="test_user",
            conversation_id=3
        )
        
        # Verificar que se maneja el error
        assert "Lo siento, hubo un error con la API de Google AI" in result
        assert "API quota exceeded" in result
