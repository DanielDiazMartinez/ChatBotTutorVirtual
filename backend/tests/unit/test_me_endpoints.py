import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.models import User, Subject, Document
from app.core.security import create_access_token

def create_test_user_with_subject_and_document(db_session: Session):
    """Crear un usuario de prueba con asignatura y documento para los tests"""
    # Crear usuario
    test_user = User(
        email="testuser@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        role="teacher"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    
    # Crear asignatura
    test_subject = Subject(
        name="Matemáticas",
        code="MAT101",
        description="Curso de matemáticas"
    )
    db_session.add(test_subject)
    db_session.commit()
    db_session.refresh(test_subject)
    
    # Asociar usuario con asignatura (profesor con teaching_subjects)
    test_user.teaching_subjects.append(test_subject)
    db_session.commit()
    
    # Crear documento
    test_document = Document(
        title="Documento de prueba",
        description="Descripción de prueba",
        file_path="/path/to/file.pdf",
        teacher_id=test_user.id,
        subject_id=test_subject.id
    )
    db_session.add(test_document)
    db_session.commit()
    db_session.refresh(test_document)
    
    return test_user, test_subject, test_document

def test_get_me_subjects_endpoint(db_session_test: Session, client: TestClient):
    """Test para verificar el funcionamiento del endpoint /me/subjects"""
    # Crear usuario de prueba con asignatura
    test_user, test_subject, _ = create_test_user_with_subject_and_document(db_session_test)
    
    # Crear token de acceso para ese usuario
    token = create_access_token({"sub": str(test_user.id), "role": test_user.role})
    
    # Realizar petición con el token
    response = client.get(
        "/api/v1/users/me/subjects",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["name"] == test_subject.name
    
    # Limpiar
    db_session_test.delete(test_user)
    db_session_test.commit()

def test_get_me_subjects_unauthorized(client: TestClient):
    """Test para verificar que se requiere autenticación para /me/subjects"""
    # Realizar petición sin token
    response = client.get("/api/v1/users/me/subjects")
    assert response.status_code == 401

def test_get_documents_me_endpoint(db_session_test: Session, client: TestClient):
    """Test para verificar el funcionamiento del endpoint /documents/me"""
    # Crear usuario de prueba con documento
    test_user, _, test_document = create_test_user_with_subject_and_document(db_session_test)
    
    # Crear token de acceso para ese usuario
    token = create_access_token({"sub": str(test_user.id), "role": test_user.role})
    
    # Realizar petición con el token
    response = client.get(
        "/api/v1/documents/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["title"] == test_document.title
    assert data["data"][0]["teacher_id"] == test_user.id
    
    # Limpiar
    db_session_test.delete(test_user)
    db_session_test.commit()

def test_get_documents_me_unauthorized(client: TestClient):
    """Test para verificar que se requiere autenticación para /documents/me"""
    # Realizar petición sin token
    response = client.get("/api/v1/documents/me")
    assert response.status_code == 401
