import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User, Document, Conversation, Message
from app.core.security import create_access_token

def test_get_my_conversations(db_session_test: Session, client: TestClient):
    """
    Test para verificar que el endpoint /me/conversations devuelve las conversaciones del usuario autenticado
    """
    # Crear un usuario de prueba
    test_user = User(
        email="test_conv_user@example.com",
        full_name="Test Conversation User",
        hashed_password="hashed_password",
        role="student"
    )
    
    db_session_test.add(test_user)
    db_session_test.commit()
    db_session_test.refresh(test_user)
    
    # Crear un documento de prueba
    test_document = Document(
        title="Test Document",
        file_path="/fake/path/test_doc.pdf",
        description="Test Document Description",
        teacher_id=1  # Asumimos que existe un profesor con ID 1
    )
    
    db_session_test.add(test_document)
    db_session_test.commit()
    db_session_test.refresh(test_document)
    
    # Crear conversaciones de prueba para el usuario
    conversation1 = Conversation(
        student_id=test_user.id,
        document_id=test_document.id
    )
    
    conversation2 = Conversation(
        student_id=test_user.id,
        document_id=test_document.id
    )
    
    db_session_test.add(conversation1)
    db_session_test.add(conversation2)
    db_session_test.commit()
    db_session_test.refresh(conversation1)
    db_session_test.refresh(conversation2)
    
    # Añadir mensajes a las conversaciones
    message1 = Message(
        conversation_id=conversation1.id,
        text="Test message 1",
        is_bot=False
    )
    
    message2 = Message(
        conversation_id=conversation1.id,
        text="Bot response 1",
        is_bot=True
    )
    
    message3 = Message(
        conversation_id=conversation2.id,
        text="Test message 2",
        is_bot=False
    )
    
    db_session_test.add_all([message1, message2, message3])
    db_session_test.commit()
    
    # Crear token de acceso para el usuario
    token = create_access_token({"sub": test_user.id, "role": test_user.role})
    
    # Realizar la petición al endpoint
    response = client.get(
        "/api/v1/chat/me/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    
    # Verificar que se devuelven las dos conversaciones
    conversations = data["data"]
    assert len(conversations) == 2
    
    # Verificar que los ids de las conversaciones son correctos
    conversation_ids = [conv["id"] for conv in conversations]
    assert conversation1.id in conversation_ids
    assert conversation2.id in conversation_ids
    
    # Verificar que la conversación 1 tiene el último mensaje
    for conv in conversations:
        if conv["id"] == conversation1.id:
            assert conv["last_message"] is not None
            assert conv["last_message"]["text"] == "Bot response 1"
            assert conv["last_message"]["is_bot"] is True
    
    # Limpiar datos de prueba
    db_session_test.query(Message).filter(
        Message.conversation_id.in_([conversation1.id, conversation2.id])
    ).delete(synchronize_session=False)
    db_session_test.query(Conversation).filter(
        Conversation.id.in_([conversation1.id, conversation2.id])
    ).delete(synchronize_session=False)
    db_session_test.delete(test_document)
    db_session_test.delete(test_user)
    db_session_test.commit()

def test_get_my_conversations_empty(db_session_test: Session, client: TestClient):
    """
    Test para verificar que el endpoint /me/conversations devuelve una lista vacía si no hay conversaciones
    """
    # Crear un usuario de prueba sin conversaciones
    test_user_no_convs = User(
        email="no_convs_user@example.com",
        full_name="No Conversations User",
        hashed_password="hashed_password",
        role="student"
    )
    
    db_session_test.add(test_user_no_convs)
    db_session_test.commit()
    db_session_test.refresh(test_user_no_convs)
    
    # Crear token de acceso para el usuario
    token = create_access_token({"sub": test_user_no_convs.id, "role": test_user_no_convs.role})
    
    # Realizar la petición al endpoint
    response = client.get(
        "/api/v1/chat/me/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    
    # Verificar que se devuelve una lista vacía
    conversations = data["data"]
    assert len(conversations) == 0
    
    # Limpiar datos de prueba
    db_session_test.delete(test_user_no_convs)
    db_session_test.commit()

def test_get_my_conversations_unauthorized(client: TestClient):
    """
    Test para verificar que el endpoint requiere autenticación
    """
    # Realizar la petición sin token
    response = client.get("/api/v1/chat/me/conversations")
    
    # Verificar que se recibe un error de autenticación
    assert response.status_code == 401
