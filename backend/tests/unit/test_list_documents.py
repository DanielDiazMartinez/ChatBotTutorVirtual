import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User, Document
from app.core.security import create_access_token

def test_list_documents_admin(db_session_test: Session, client: TestClient, admin_auth_headers):
    """
    Test para verificar que un administrador puede ver todos los documentos
    """
    # Crear usuario profesor para la prueba
    teacher_user = User(
        email="teacher_test@example.com",
        full_name="Teacher Test",
        hashed_password="hashed_password",
        role="teacher"
    )
    
    db_session_test.add(teacher_user)
    db_session_test.commit()
    db_session_test.refresh(teacher_user)
    
    # Crear documentos de prueba
    doc1 = Document(
        title="Test Document 1",
        file_path="/fake/path/doc1.pdf",
        description="Test Description 1",
        user_id=teacher_user.id  # Cambiado de teacher_id a user_id
    )
    doc2 = Document(
        title="Test Document 2",
        file_path="/fake/path/doc2.pdf",
        description="Test Description 2",
        user_id=teacher_user.id  # Cambiado de teacher_id a user_id
    )
    
    db_session_test.add(doc1)
    db_session_test.add(doc2)
    db_session_test.commit()
    db_session_test.refresh(doc1)
    db_session_test.refresh(doc2)
    
    # Realizar petición con el token de administrador utilizando el fixture
    response = client.get(
        "/api/v1/documents/list",
        headers=admin_auth_headers
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
    db_session_test.commit()

def test_list_documents_teacher(db_session_test: Session, client: TestClient, teacher_auth_headers):
    """
    Test para verificar que un profesor solo puede ver sus propios documentos
    """
    # Primero necesitamos encontrar el ID del profesor que está en el token
    # Hacemos una petición al endpoint /me para obtener el ID
    me_response = client.get("/api/v1/users/me", headers=teacher_auth_headers)
    assert me_response.status_code == 200
    teacher_id = me_response.json()["data"]["id"]
    
    # Obtener el profesor del token
    teacher1 = db_session_test.query(User).filter(User.id == teacher_id).first()
    
    # Crear otro profesor para la prueba
    teacher2 = User(
        email="teacher2@example.com",
        full_name="Teacher 2",
        hashed_password="hashed_password",
        role="teacher"
    )
    
    db_session_test.add(teacher2)
    db_session_test.commit()
    db_session_test.refresh(teacher2)
    
    # Crear asignaturas para cada profesor
    from app.models.models import Subject
    subject1 = Subject(
        name="Subject for Teacher 1",
        code="SUBJ1",
        description="Subject assigned to teacher 1"
    )
    subject2 = Subject(
        name="Subject for Teacher 2", 
        code="SUBJ2",
        description="Subject assigned to teacher 2"
    )
    
    db_session_test.add(subject1)
    db_session_test.add(subject2)
    db_session_test.commit()
    db_session_test.refresh(subject1)
    db_session_test.refresh(subject2)
    
    # Asignar profesores a sus respectivas asignaturas
    teacher1.subjects.append(subject1)
    teacher2.subjects.append(subject2)
    db_session_test.commit()
    
    # Crear documentos de prueba para cada profesor con sus respectivas asignaturas
    doc_teacher1 = Document(
        title="Document Teacher 1",
        file_path="/fake/path/doc_t1.pdf",
        description="Document for Teacher 1",
        user_id=teacher_id,
        subject_id=subject1.id
    )
    doc_teacher2 = Document(
        title="Document Teacher 2",
        file_path="/fake/path/doc_t2.pdf",
        description="Document for Teacher 2",
        user_id=teacher2.id,
        subject_id=subject2.id
    )
    
    db_session_test.add(doc_teacher1)
    db_session_test.add(doc_teacher2)
    db_session_test.commit()
    db_session_test.refresh(doc_teacher1)
    db_session_test.refresh(doc_teacher2)
    
    # Realizar petición con el token del profesor del fixture
    response = client.get(
        "/api/v1/documents/list",
        headers=teacher_auth_headers
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
    db_session_test.delete(teacher2)
    db_session_test.commit()
