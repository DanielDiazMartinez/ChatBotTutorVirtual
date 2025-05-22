import pytest
import os
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User, Document
from app.core.security import create_access_token
from app.core.config import settings
from app.models.schemas import DocumentCreate

def test_delete_document_physical_file(db_session_test: Session, client: TestClient):
    """
    Test para verificar que el endpoint de eliminación borra el archivo físico
    """
    # Crear un usuario profesor para la prueba
    test_teacher = User(
        email="teacher_test@example.com",
        full_name="Teacher Test",
        hashed_password="hashed_password",
        role="teacher"
    )
    db_session_test.add(test_teacher)
    db_session_test.commit()
    db_session_test.refresh(test_teacher)
    
    # Crear un directorio temporal para la prueba
    test_upload_folder = os.path.join(settings.UPLOAD_FOLDER, str(test_teacher.id))
    os.makedirs(test_upload_folder, exist_ok=True)
    
    # Crear un archivo de prueba
    test_filename = "test_document.pdf"
    test_file_path = os.path.join(test_upload_folder, test_filename)
    
    # Escribir contenido en el archivo de prueba
    with open(test_file_path, "wb") as f:
        f.write(b"PDF test content")
    
    # Verificar que el archivo existe
    assert os.path.exists(test_file_path)
    
    # Crear un documento en la base de datos asociado al archivo
    test_document = Document(
        title="Test Document",
        file_path=test_file_path,
        description="Test Description",
        user_id=test_teacher.id  # Cambiado de teacher_id a user_id
    )
    db_session_test.add(test_document)
    db_session_test.commit()
    db_session_test.refresh(test_document)
    
    # Crear token de acceso para el profesor
    token = create_access_token({"sub": test_teacher.id, "role": test_teacher.role})
    
    # Realizar petición de eliminación con el token
    response = client.delete(
        f"/api/v1/documents/{test_document.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar que la respuesta es correcta
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["data"]["id"] == test_document.id
    
    # Verificar que el archivo físico ya no existe
    assert not os.path.exists(test_file_path)
    
    # Limpiar
    db_session_test.query(User).filter(User.id == test_teacher.id).delete()
    db_session_test.commit()

def test_delete_document_without_permission(db_session_test: Session, client: TestClient):
    """
    Test para verificar que un profesor no puede eliminar documentos que no le pertenecen
    """
    # Crear dos usuarios profesor para la prueba
    test_teacher1 = User(
        email="teacher1@example.com",
        full_name="Teacher 1",
        hashed_password="hashed_password",
        role="teacher"
    )
    test_teacher2 = User(
        email="teacher2@example.com",
        full_name="Teacher 2",
        hashed_password="hashed_password",
        role="teacher"
    )
    db_session_test.add(test_teacher1)
    db_session_test.add(test_teacher2)
    db_session_test.commit()
    db_session_test.refresh(test_teacher1)
    db_session_test.refresh(test_teacher2)
    
    # Crear un directorio temporal para la prueba
    test_upload_folder = os.path.join(settings.UPLOAD_FOLDER, str(test_teacher1.id))
    os.makedirs(test_upload_folder, exist_ok=True)
    
    # Crear un archivo de prueba
    test_filename = "test_document2.pdf"
    test_file_path = os.path.join(test_upload_folder, test_filename)
    
    # Escribir contenido en el archivo de prueba
    with open(test_file_path, "wb") as f:
        f.write(b"PDF test content")
    
    # Crear un documento en la base de datos asociado al archivo y al profesor 1
    test_document = Document(
        title="Test Document",
        file_path=test_file_path,
        description="Test Description",
        user_id=test_teacher1.id  # Cambiado de teacher_id a user_id
    )
    db_session_test.add(test_document)
    db_session_test.commit()
    db_session_test.refresh(test_document)
    
    # Crear token de acceso para el profesor 2
    token = create_access_token({"sub": test_teacher2.id, "role": test_teacher2.role})
    
    # Intentar eliminar el documento del profesor 1 con el token del profesor 2
    response = client.delete(
        f"/api/v1/documents/{test_document.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar que se recibe un error de permiso
    assert response.status_code == 403
    
    # Verificar que el archivo físico aún existe
    assert os.path.exists(test_file_path)
    
    # Limpiar
    os.remove(test_file_path)
    db_session_test.query(Document).filter(Document.id == test_document.id).delete()
    db_session_test.query(User).filter(User.id.in_([test_teacher1.id, test_teacher2.id])).delete()
    db_session_test.commit()
