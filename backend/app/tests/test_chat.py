import pytest
from app.models.models import Student, Document, Conversation, Message

@pytest.fixture
def setup_test_data(db):
    from app.models.models import Teacher, Student, Document

    # Crear un Teacher
    teacher = Teacher(id=1, email="teacher@example.com", full_name="Test Teacher", hashed_password="hashed_pw")
    db.add(teacher)
    db.commit()  

    # Crear un Student
    student = Student(id=1, email="student@example.com", full_name="Test Student", hashed_password="hashed_pw")
    db.add(student)
    db.commit() 

    # Crear un Document asociado al Teacher
    document = Document(id=1, title="Test Document", file_path="/path/to/test.pdf", teacher_id=1)
    db.add(document)
    db.commit()  

    return student, document


def test_create_conversation(client, db, setup_test_data):
    """Prueba la creación de una conversación."""
    student, document = setup_test_data

    response = client.post("/chat/conversation", json={"student_id": student.id, "document_id": document.id})
    
    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert data["student_id"] == student.id
    assert data["document_id"] == document.id


def test_send_message(client, db, setup_test_data):
    """Prueba enviar un mensaje dentro de una conversación."""
    student, document = setup_test_data

    # Crear la conversación primero
    conv_response = client.post("/chat/conversation", json={"student_id": student.id, "document_id": document.id})
    assert conv_response.status_code == 201, conv_response.text
    conv_data = conv_response.json()
    conv_id = conv_data["id"]

    # Enviar un mensaje en la conversación creada
    message_payload = {"text": "¿Qué es IA?", "is_bot": False}
    response = client.post(f"/chat/message/{conv_id}", json=message_payload)
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["text"] == "¿Qué es IA?"
    assert data["conversation_id"] == conv_id
