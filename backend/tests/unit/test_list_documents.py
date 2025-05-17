import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User, Document
from app.core.security import create_access_token

def test_list_documents_admin(db_session_test: Session, client: TestClient):
    """
    Test para verificar que un administrador puede ver todos los documentos
    """
    # Crear usuarios para la prueba
    admin_user = User(
        email="admin_test@example.com",
        full_name="Admin Test",
        hashed_password="hashed_password",
        role="admin"
    )
    teacher_user = User(
        email="teacher_test@example.com",
        full_name="Teacher Test",
        hashed_password="hashed_password",
        role="teacher"
    )
    
    db_session_test.add(admin_user)
    db_session_test.add(teacher_user)
    db_session_test.commit()
    db_session_test.refresh(admin_user)
    db_session_test.refresh(teacher_user)
    
    # Crear documentos de prueba
    doc1 = Document(
        title="Test Document 1",
        file_path="/fake/path/doc1.pdf",
        description="Test Description 1",
        teacher_id=teacher_user.id
    )
    doc2 = Document(
        title="Test Document 2",
        file_path="/fake/path/doc2.pdf",
        description="Test Description 2",
        teacher_id=teacher_user.id
    )
    
    db_session_test.add(doc1)
    db_session_test.add(doc2)
    db_session_test.commit()
    db_session_test.refresh(doc1)
    db_session_test.refresh(doc2)
    
    # Crear token de acceso para el administrador
    admin_token = create_access_token({"sub": admin_user.id, "role": admin_user.role})
    
    # Realizar petición con el token de administrador
    response = client.get(
        "/api/v1/documents/list",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Verificar que la respuesta es correcta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    
    # El administrador debe poder ver todos los documentos
    documents = data["data"]
    assert len(documents) >= 2  # Podría haber más documentos en la BD
    
    # Verificar que los IDs de los documentos creados están presentes
    document_ids = [doc["id"] for doc in documents]
    assert doc1.id in document_ids
    assert doc2.id in document_ids
    
    # Limpiar
    db_session_test.delete(doc1)
    db_session_test.delete(doc2)
    db_session_test.delete(teacher_user)
    db_session_test.delete(admin_user)
    db_session_test.commit()

def test_list_documents_teacher(db_session_test: Session, client: TestClient):
    """
    Test para verificar que un profesor solo puede ver sus propios documentos
    """
    # Crear usuarios profesor para la prueba
    teacher1 = User(
        email="teacher1@example.com",
        full_name="Teacher 1",
        hashed_password="hashed_password",
        role="teacher"
    )
    teacher2 = User(
        email="teacher2@example.com",
        full_name="Teacher 2",
        hashed_password="hashed_password",
        role="teacher"
    )
    
    db_session_test.add(teacher1)
    db_session_test.add(teacher2)
    db_session_test.commit()
    db_session_test.refresh(teacher1)
    db_session_test.refresh(teacher2)
    
    # Crear documentos de prueba para cada profesor
    doc_teacher1 = Document(
        title="Document Teacher 1",
        file_path="/fake/path/doc_t1.pdf",
        description="Document for Teacher 1",
        teacher_id=teacher1.id
    )
    doc_teacher2 = Document(
        title="Document Teacher 2",
        file_path="/fake/path/doc_t2.pdf",
        description="Document for Teacher 2",
        teacher_id=teacher2.id
    )
    
    db_session_test.add(doc_teacher1)
    db_session_test.add(doc_teacher2)
    db_session_test.commit()
    db_session_test.refresh(doc_teacher1)
    db_session_test.refresh(doc_teacher2)
    
    # Crear token de acceso para el profesor 1
    teacher1_token = create_access_token({"sub": teacher1.id, "role": teacher1.role})
    
    # Realizar petición con el token del profesor 1
    response = client.get(
        "/api/v1/documents/list",
        headers={"Authorization": f"Bearer {teacher1_token}"}
    )
    
    # Verificar que la respuesta es correcta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    
    # El profesor 1 solo debe ver sus propios documentos
    documents = data["data"]
    document_ids = [doc["id"] for doc in documents]
    
    # Debe incluir el documento del profesor 1
    assert doc_teacher1.id in document_ids
    
    # No debe incluir el documento del profesor 2
    assert doc_teacher2.id not in document_ids
    
    # Limpiar
    db_session_test.delete(doc_teacher1)
    db_session_test.delete(doc_teacher2)
    db_session_test.delete(teacher1)
    db_session_test.delete(teacher2)
    db_session_test.commit()
