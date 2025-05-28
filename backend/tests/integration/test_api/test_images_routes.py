import os
import io
import tempfile
import pytest
import shutil
from unittest import mock
from fastapi import status
from PIL import Image

def test_upload_image_success(client, db_session_test, admin_auth_headers):
    """
    Prueba la subida exitosa de una imagen como un administrador.
    """
    subject_data = {
        "name": "Matemáticas",
        "code": "MAT101",
        "description": "Curso de matemáticas básicas"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == 201
    subject_id = subject_response.json()["data"]["id"]
    
    temp_dir = tempfile.mkdtemp()
    with mock.patch('app.services.image_service.UPLOAD_DIR', temp_dir):
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        files = {
            'file': ('test_image.jpg', img_byte_arr, 'image/jpeg')
        }
        data = {
            'description': 'Test image description',
            'subject_id': str(subject_id)
        }
        
        response = client.post(
            "/api/v1/images/", 
            files=files,
            data=data,
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert "file_path" in response.json()["data"]
        
        response_data = response.json()["data"]
        assert response_data["description"] == "Test image description"
        assert response_data["subject_id"] == subject_id
        
        image_id = response_data["id"]
        
        file_path = response_data["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Limpiar el directorio temporal
    shutil.rmtree(temp_dir)

def test_get_image_by_id(client, db_session_test, admin_auth_headers):
    """
    Prueba la obtención de una imagen por su ID.
    """
    subject_data = {
        "name": "Física",
        "code": "FIS101",
        "description": "Curso de física básica"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == 201
    subject_id = subject_response.json()["data"]["id"]
    
    temp_dir = tempfile.mkdtemp()
    with mock.patch('app.services.image_service.UPLOAD_DIR', temp_dir):
        img = Image.new('RGB', (100, 100), color='blue')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        files = {
            'file': ('test_get_image.jpg', img_byte_arr, 'image/jpeg')
        }
        form_data = {
            'description': 'Test get image',
            'subject_id': str(subject_id)
        }
        
        upload_response = client.post(
            "/api/v1/images/", 
            files=files,
            data=form_data,
            headers=admin_auth_headers
        )
        assert upload_response.status_code == status.HTTP_201_CREATED
        
        image_id = upload_response.json()["data"]["id"]
        file_path = upload_response.json()["data"]["file_path"]
        
        get_response = client.get(
            f"/api/v1/images/{image_id}",
            headers=admin_auth_headers
        )
        
        assert get_response.status_code == status.HTTP_200_OK
        assert "data" in get_response.json()
        assert get_response.json()["data"]["id"] == image_id
        assert get_response.json()["data"]["description"] == "Test get image"
        
        if os.path.exists(file_path):
            os.remove(file_path)
    
    shutil.rmtree(temp_dir)

def test_get_image_not_found(client, db_session_test, admin_auth_headers):
    """
    Prueba el caso en que la imagen solicitada no existe.
    """
    response = client.get(
        "/api/v1/images/99999",
        headers=admin_auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Imagen no encontrada" in response.json()["detail"]

def test_upload_image_invalid_format(client, db_session_test, admin_auth_headers):
    """
    Prueba el rechazo de una imagen con formato inválido.
    """
    temp_dir = tempfile.mkdtemp()
    with mock.patch('app.services.image_service.UPLOAD_DIR', temp_dir):
        text_file = io.BytesIO(b"This is not an image")
        
        files = {
            'file': ('invalid.txt', text_file, 'text/plain')
        }
        
        response = client.post(
            "/api/v1/images/", 
            files=files,
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Formato de imagen no válido" in response.json()["detail"]
    
    shutil.rmtree(temp_dir)

def test_upload_image_student(client, db_session_test, student_auth_headers):
    """
    Prueba que un estudiante NO puede subir imágenes (solo profesores y admins tienen permiso).
    """
    temp_dir = tempfile.mkdtemp()
    with mock.patch('app.services.image_service.UPLOAD_DIR', temp_dir):
        img = Image.new('RGB', (100, 100), color='green')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        files = {
            'file': ('student_test_image.jpg', img_byte_arr, 'image/jpeg')
        }
        
        response = client.post(
            "/api/v1/images/", 
            files=files,
            headers=student_auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    shutil.rmtree(temp_dir)
