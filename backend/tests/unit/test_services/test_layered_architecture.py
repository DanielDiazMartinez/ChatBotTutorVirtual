import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.models import Document, User, Conversation, Message
from app.services.embedding_service import get_embedding_for_query
from app.services.vector_service import (
    search_similar_chunks, 
    create_conversation,
    add_user_message,
    add_bot_message,
    get_conversation_context,
    get_conversation_history
)
from app.services.chat_service import (
    process_message,
    add_message_and_generate_response,
    generate_conversation
)

@pytest.fixture
def mock_embedding():
    return [0.1] * 768  # Vector de embedding simulado

@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    
    # Mock para simular document_exists
    mock_exists_query = MagicMock()
    mock_scalar = MagicMock(return_value=True)
    mock_exists_query.scalar = mock_scalar
    session.query().filter().exists.return_value = mock_exists_query
    
    # Mock para simular búsqueda de usuario
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.role = "student"
    session.query().filter().first.return_value = mock_user
    
    # Mock para simular creación de conversación
    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = 1
    mock_conversation.document_id = 1
    mock_conversation.user_id = 1
    session.add.return_value = None
    
    # Mock para mensajes
    mock_messages = [MagicMock(spec=Message) for _ in range(3)]
    for i, msg in enumerate(mock_messages):
        msg.text = f"Mensaje {i+1}"
        msg.is_bot = i % 2 == 0
        msg.created_at = datetime.utcnow()
    
    session.query().filter().order_by().limit().all.return_value = mock_messages
    
    return session

def test_create_conversation(mock_db_session):
    """Prueba la creación de una conversación"""
    conversation = create_conversation(
        db=mock_db_session,
        document_id=1,
        user_id=1,
        user_type="student",
        subject_id=1
    )
    
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called
    assert conversation is not None

def test_add_user_message(mock_db_session, mock_embedding):
    """Prueba añadir un mensaje de usuario"""
    with patch('app.services.embedding_service.get_embedding_for_query', return_value=mock_embedding):
        user_msg = add_user_message(
            db=mock_db_session,
            conversation_id=1,
            message_text="Hola, ¿cómo estás?"
        )
        
        assert mock_db_session.add.called
        assert mock_db_session.flush.called
        assert mock_db_session.refresh.called
        assert user_msg is not None

def test_add_bot_message(mock_db_session, mock_embedding):
    """Prueba añadir un mensaje del bot"""
    with patch('app.services.embedding_service.get_embedding_for_query', return_value=mock_embedding):
        bot_msg = add_bot_message(
            db=mock_db_session,
            conversation_id=1,
            message_text="Estoy bien, ¿en qué puedo ayudarte?"
        )
        
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        assert mock_db_session.refresh.called
        assert bot_msg is not None

def test_get_conversation_history(mock_db_session):
    """Prueba obtener el historial de conversación"""
    history = get_conversation_history(
        db=mock_db_session,
        conversation_id=1,
        limit=3
    )
    
    assert isinstance(history, str)
    assert "Usuario" in history or "Bot" in history

def test_generate_conversation(mock_db_session, mock_embedding):
    """Prueba la generación de una nueva conversación con mensaje inicial"""
    with patch('app.services.chat_service.create_conversation_in_vector', return_value=MagicMock(spec=Conversation)) as mock_create:
        with patch('app.services.chat_service.process_message', return_value="Respuesta del bot"):
            response, conversation = generate_conversation(
                db=mock_db_session,
                document_id=1,
                user_id=1,
                user_type="student",
                subject_id=1,
                initial_message_text="Hola"
            )
            
            assert mock_create.called
            assert response == "Respuesta del bot"
            assert conversation is not None

def test_add_message_and_generate_response(mock_db_session):
    """Prueba añadir un mensaje y generar respuesta"""
    # Mock de la conversación
    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = 1
    mock_conversation.user_id = 1
    mock_conversation.user_role = "student"
    mock_conversation.document_id = 1
    
    # Configurar el mock_db_session para devolver la conversación
    mock_db_session.query().filter().first.return_value = mock_conversation
    
    with patch('app.services.chat_service.add_user_message') as mock_add_user_msg:
        with patch('app.services.chat_service.get_conversation_context', return_value="Contexto simulado"):
            with patch('app.services.chat_service.get_conversation_history', return_value="Historial simulado"):
                with patch('app.services.chat_service.generate_ai_response', return_value="Respuesta IA"):
                    with patch('app.services.chat_service.add_bot_message') as mock_add_bot_msg:
                        user_msg = MagicMock(spec=Message)
                        bot_msg = MagicMock(spec=Message)
                        mock_add_user_msg.return_value = user_msg
                        mock_add_bot_msg.return_value = bot_msg
                        
                        result_user_msg, result_bot_msg = add_message_and_generate_response(
                            db=mock_db_session,
                            conversation_id=1,
                            user_id=1,
                            user_type="student",
                            message_text="¿Qué es Python?"
                        )
                        
                        assert result_user_msg is user_msg
                        assert result_bot_msg is bot_msg
                        assert mock_add_user_msg.called
                        assert mock_add_bot_msg.called
