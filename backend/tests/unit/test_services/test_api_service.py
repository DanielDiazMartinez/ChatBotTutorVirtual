import pytest
from unittest.mock import patch, MagicMock

from app.services.api_service import generate_ai_response

class TestApiService:
    """Tests para el servicio de API (Groq)"""
    
    @patch('app.services.api_service.client')
    def test_generate_ai_response(self, mock_client):
        """Test para generación de respuestas a través de la API de Groq"""
        # Configurar el mock
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        mock_message.content = "Python es un lenguaje de programación interpretado de alto nivel."
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        
        mock_client.chat.completions.create.return_value = mock_completion
        
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
        mock_client.chat.completions.create.assert_called_once()
        
        # Verificar que los parámetros incluyen el contexto y la conversación
        args, kwargs = mock_client.chat.completions.create.call_args
        assert "Python es un lenguaje de programación" in kwargs["messages"][0]["content"]
        assert "Usuario: Hola\nBot: Hola, ¿en qué puedo ayudarte?" in kwargs["messages"][0]["content"]
    
    @patch('app.services.api_service.client', None)
    def test_generate_ai_response_with_no_client(self):
        """Test para manejo de error cuando no hay cliente Groq configurado"""
        result = generate_ai_response(
            user_question="¿Qué es Python?",
            context="Python es un lenguaje de programación",
            conversation_history="",
            user_id="test_user",
            conversation_id=2
        )
        
        assert "Lo siento, la configuración del servicio de IA no es correcta" in result
    
    @patch('app.services.api_service.client')
    def test_generate_ai_response_api_error(self, mock_client):
        """Test para manejo de errores de la API"""
        # Configurar el mock para lanzar una excepción
        from groq import GroqError
        # Crear un objeto GroqError personalizado
        # La clase GroqError no acepta argumentos con nombre, así que creamos la instancia
        # y luego añadimos los atributos necesarios manualmente
        error = GroqError("API rate limit exceeded")
        error.status_code = 429
        # Asegurarse de que tiene el atributo message
        if not hasattr(error, 'message'):
            error.message = "API rate limit exceeded"
        mock_client.chat.completions.create.side_effect = error
        
        # Llamar a la función
        result = generate_ai_response(
            user_question="¿Qué es Python?",
            context="Python es un lenguaje de programación",
            conversation_history="",
            user_id="test_user",
            conversation_id=3
        )
        
        # Verificar que se maneja el error
        assert "Lo siento, hubo un error con la API de Groq" in result
        assert "429" in result
        assert "API rate limit exceeded" in result
