import pytest
from fastapi import status
from sqlalchemy.orm import Session
from app.models.models import User, Document, Conversation, Message
from app.core.security import create_access_token
from datetime import datetime, timedelta

def test_get_conversation_messages(client, db_session_test, student_auth_headers):
    """
    Test para verificar que el endpoint devuelve todos los mensajes de una conversación correctamente
    """
    student_email = "student_test@example.com"
    student = db_session_test.query(User).filter(User.email == student_email).first()
    
    test_document = Document(
        title="Test Document for Messages",
        file_path="/fake/path/test_messages_doc.pdf",
        description="Test Document for Messages API",
        user_id=student.id
    )
    
    db_session_test.add(test_document)
    db_session_test.commit()
    db_session_test.refresh(test_document)
    
    # Crear una conversación de prueba
    conversation = Conversation(
        user_id=student.id,
        subject_id=None,
        created_at=datetime.utcnow()
    )
    
    db_session_test.add(conversation)
    db_session_test.commit()
    db_session_test.refresh(conversation)
    
    message1 = Message(
        conversation_id=conversation.id,
        text="¿Cómo funciona este tutorial?",
        is_bot=False,
        created_at=datetime.utcnow() - timedelta(minutes=10)
    )
    
    message2 = Message(
        conversation_id=conversation.id,
        text="Este tutorial explica los conceptos básicos de programación...",
        is_bot=True,
        created_at=datetime.utcnow() - timedelta(minutes=9)
    )
    
    message3 = Message(
        conversation_id=conversation.id,
        text="¿Puedo ver un ejemplo de código?",
        is_bot=False,
        created_at=datetime.utcnow() - timedelta(minutes=5)
    )
    
    message4 = Message(
        conversation_id=conversation.id,
        text="Claro, aquí tienes un ejemplo: console.log('Hola mundo');",
        is_bot=True,
        created_at=datetime.utcnow() - timedelta(minutes=4)
    )
    
    db_session_test.add_all([message1, message2, message3, message4])
    db_session_test.commit()
    
    response = client.get(
        f"/api/v1/chat/conversation/{conversation.id}/messages",
        headers=student_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    
    messages = data["data"]
    assert len(messages) == 4
    assert messages[0]["text"] == message1.text
    assert messages[1]["text"] == message2.text
    assert messages[2]["text"] == message3.text
    assert messages[3]["text"] == message4.text
    
    assert "id" in messages[0]
    assert "conversation_id" in messages[0]
    assert "text" in messages[0]
    assert "is_bot" in messages[0]
    assert "created_at" in messages[0]
    assert messages[0]["is_bot"] == False
    assert messages[1]["is_bot"] == True
    assert messages[2]["is_bot"] == False
    assert messages[3]["is_bot"] == True

def test_get_conversation_messages_unauthorized(client, db_session_test, student_auth_headers, teacher_auth_headers):
    """
    Test para verificar que un usuario no puede acceder a los mensajes de una conversación que no le pertenece
    """

    teacher_email = "teacher_test@example.com"
    teacher = db_session_test.query(User).filter(User.email == teacher_email).first()

    test_document = Document(
        title="Test Document for Unauthorized",
        file_path="/fake/path/test_unauth_doc.pdf",
        description="Test Document for Unauthorized Access",
        user_id=teacher.id
    )
    
    db_session_test.add(test_document)
    db_session_test.commit()
    db_session_test.refresh(test_document)
    other_student = User(
        email="other_student@example.com",
        full_name="Other Student",
        hashed_password="hashed_password",
        role="student"
    )
    
    db_session_test.add(other_student)
    db_session_test.commit()
    db_session_test.refresh(other_student)
    
    conversation = Conversation(
        user_id=other_student.id,
        subject_id=None,
        created_at=datetime.utcnow()
    )
    
    db_session_test.add(conversation)
    db_session_test.commit()
    db_session_test.refresh(conversation)
    
    message = Message(
        conversation_id=conversation.id,
        text="Este mensaje no debería ser accesible",
        is_bot=False,
        created_at=datetime.utcnow()
    )
    
    db_session_test.add(message)
    db_session_test.commit()
    response = client.get(
        f"/api/v1/chat/conversation/{conversation.id}/messages",
        headers=student_auth_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_conversation_messages_not_found(client, db_session_test, student_auth_headers):
    """
    Test para verificar que se devuelve un error 404 cuando no existe la conversación
    """
    nonexistent_id = 99999
    
    response = client.get(
        f"/api/v1/chat/conversation/{nonexistent_id}/messages",
        headers=student_auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND