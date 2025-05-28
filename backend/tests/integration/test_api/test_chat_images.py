import os
import io
import json
import pytest
import tempfile
from fastapi import status
from PIL import Image

# Crear un directorio temporal para las pruebas
TEST_UPLOAD_DIR = tempfile.mkdtemp()

# Patch para el directorio de subida durante las pruebas
@pytest.fixture(autouse=True)
def patch_upload_dir(monkeypatch):
    """
    Reemplaza la constante UPLOAD_DIR en image_service.py durante las pruebas
    """
    import app.services.image_service
    monkeypatch.setattr(app.services.image_service, "UPLOAD_DIR", TEST_UPLOAD_DIR)
    yield

def test_add_message_with_image(client, db_session_test, admin_auth_headers, student_auth_headers):
    """
    Prueba añadir un mensaje con imagen a una conversación existente.
    """
    subject_data = {
        "name": "Matemáticas Test",
        "code": "MAT-TEST",
        "description": "Asignatura de prueba para test"
    }
    
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    
    assert create_subject_response.status_code == 201
    subject_id = create_subject_response.json()["data"]["id"]
    
    conv_data = {
        "subject_id": subject_id
    }
    
    create_conv_response = client.post(
        "/api/v1/chat/conversation",
        json=conv_data,
        headers=student_auth_headers
    )
    
    assert create_conv_response.status_code == status.HTTP_200_OK
    conversation_id = create_conv_response.json()["data"]["conversation"]["id"]
    
    img = Image.new('RGB', (100, 100), color='purple')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    files = {
        'file': ('message_image.jpg', img_byte_arr, 'image/jpeg')
    }
    
    import json
    message_text = 'Este mensaje incluye una imagen'
    data = {
        'message_data': json.dumps({'text': message_text})
    }
    
    response = client.post(
        f"/api/v1/chat/c/{conversation_id}",
        files=files,
        data=data,
        headers=student_auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    assert "user_message" in response.json()["data"]
    assert "bot_message" in response.json()["data"]
    
    user_message = response.json()["data"]["user_message"]
    assert user_message["text"] == message_text
    assert user_message["image_id"] is not None
    
    messages_response = client.get(
        f"/api/v1/chat/conversation/{conversation_id}/messages",
        headers=student_auth_headers
    )
    
    assert messages_response.status_code == status.HTTP_200_OK
    messages = messages_response.json()["data"]
    
    image_message = next((m for m in messages if m["image_id"] is not None), None)
    assert image_message is not None
    
    image_id = user_message["image_id"]
    image_response = client.get(
        f"/api/v1/images/{image_id}",
        headers=student_auth_headers
    )
    
    assert image_response.status_code == status.HTTP_200_OK
    file_path = image_response.json()["data"]["file_path"]
    
    if os.path.exists(file_path):
        os.remove(file_path)

def test_add_message_only_image(client, db_session_test, admin_auth_headers, student_auth_headers):
    """
    Prueba añadir un mensaje que solo contiene una imagen sin texto.
    """
    subject_data = {
        "name": "Física Test",
        "code": "FIS-TEST",
        "description": "Asignatura de prueba para test"
    }
    
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    
    assert create_subject_response.status_code == 201
    subject_id = create_subject_response.json()["data"]["id"]
    
    conv_data = {
        "subject_id": subject_id
    }
    
    create_conv_response = client.post(
        "/api/v1/chat/conversation",
        json=conv_data,
        headers=student_auth_headers
    )
    
    assert create_conv_response.status_code == status.HTTP_200_OK
    conversation_id = create_conv_response.json()["data"]["conversation"]["id"]
    
    img = Image.new('RGB', (100, 100), color='yellow')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    files = {
        'file': ('only_image.jpg', img_byte_arr, 'image/jpeg')
    }
    
    # Para el mensaje que solo contiene una imagen, podemos enviar message_data vacío
    data = {
        'message_data': json.dumps({'text': ''})
    }
    
    response = client.post(
        f"/api/v1/chat/c/{conversation_id}",
        files=files,
        data=data,
        headers=student_auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    assert "user_message" in response.json()["data"]
    
    user_message = response.json()["data"]["user_message"]
    assert user_message["text"] is None or user_message["text"] == ""
    assert user_message["image_id"] is not None
    
    image_id = user_message["image_id"]
    image_response = client.get(
        f"/api/v1/images/{image_id}",
        headers=student_auth_headers
    )
    
    assert image_response.status_code == status.HTTP_200_OK
    file_path = image_response.json()["data"]["file_path"]
    
    if os.path.exists(file_path):
        os.remove(file_path)

def test_message_no_content_error(client, db_session_test, admin_auth_headers, student_auth_headers):
    """
    Prueba que se produce un error si no se proporciona ni texto ni imagen.
    """
    subject_data = {
        "name": "Química Test",
        "code": "QUI-TEST",
        "description": "Asignatura de prueba para test"
    }
    
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    
    assert create_subject_response.status_code == 201
    subject_id = create_subject_response.json()["data"]["id"]
    
    conv_data = {
        "subject_id": subject_id
    }
    
    create_conv_response = client.post(
        "/api/v1/chat/conversation",
        json=conv_data,
        headers=student_auth_headers
    )
    
    assert create_conv_response.status_code == status.HTTP_200_OK
    conversation_id = create_conv_response.json()["data"]["conversation"]["id"]
    
    response = client.post(
        f"/api/v1/chat/c/{conversation_id}",
        json={},
        headers=student_auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Se requiere proporcionar texto del mensaje o un archivo" in response.json()["detail"]

def test_unauthorized_access_to_image(client, db_session_test, teacher_auth_headers, student_auth_headers, admin_auth_headers):
    """
    Prueba que un usuario no puede acceder a las imágenes de otro usuario sin los permisos adecuados.
    """
    # Crear primero una asignatura y una conversación
    subject_data = {
        "name": "Seguridad Test",
        "code": "SEG-TEST",
        "description": "Asignatura de prueba para test de seguridad"
    }
    
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    
    assert create_subject_response.status_code == 201
    subject_id = create_subject_response.json()["data"]["id"]
    
    conv_data = {
        "subject_id": subject_id
    }
    
    create_conv_response = client.post(
        "/api/v1/chat/conversation",
        json=conv_data,
        headers=student_auth_headers
    )
    
    assert create_conv_response.status_code == status.HTTP_200_OK
    conversation_id = create_conv_response.json()["data"]["conversation"]["id"]
    
    # Crear una imagen como parte de un mensaje
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    files = {
        'file': ('private_image.jpg', img_byte_arr, 'image/jpeg')
    }
    
    import json
    message_text = 'Mensaje con imagen para prueba de seguridad'
    data = {
        'message_data': json.dumps({'text': message_text})
    }
    
    # Subir la imagen como parte de un mensaje en una conversación
    upload_response = client.post(
        f"/api/v1/chat/c/{conversation_id}",
        files=files,
        data=data,
        headers=student_auth_headers
    )
    
    assert upload_response.status_code == status.HTTP_200_OK
    image_id = upload_response.json()["data"]["user_message"]["image_id"]
    
    # Obtener información de la imagen para poder limpiarla después
    image_info_response = client.get(
        f"/api/v1/images/{image_id}",
        headers=student_auth_headers
    )
    
    assert image_info_response.status_code == status.HTTP_200_OK
    file_path = image_info_response.json()["data"]["file_path"]
    
    # Crear un segundo usuario para pruebas de acceso no autorizado
    # Usamos un token inválido para simular otro estudiante
    another_student_headers = {
        "Authorization": "Bearer invalid_token_simulating_another_student"
    }
    
    # Intentar acceder a la imagen con un usuario no autorizado
    response = client.get(
        f"/api/v1/images/{image_id}",
        headers=another_student_headers
    )
    
    # Verificar que un usuario no autorizado no puede acceder a la imagen
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Verificar que un profesor sí puede acceder a la imagen
    teacher_response = client.get(
        f"/api/v1/images/{image_id}",
        headers=teacher_auth_headers
    )
    
    assert teacher_response.status_code == status.HTTP_200_OK
    
    # Limpiar recursos (eliminar la imagen temporal)
    if os.path.exists(file_path):
        os.remove(file_path)
