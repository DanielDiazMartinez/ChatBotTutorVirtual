from fastapi import status
from typing import Dict

def test_crear_asignatura_codigo_duplicado(client, db_session_test, admin_auth_headers):
    """Test para verificar que no se pueden crear asignaturas con código duplicado"""
    # Crear la primera asignatura
    subject_data = {
        "name": "Matemáticas",
        "code": "MAT301",
        "description": "Descripción"
    }
    response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # Intentar crear otra asignatura con el mismo código
    duplicate_subject = {
        "name": "Otra Matemáticas",
        "code": "MAT301",  # mismo código
        "description": "Otra descripción"
    }
    duplicate_response = client.post(
        "/api/v1/subjects",
        json=duplicate_subject,
        headers=admin_auth_headers
    )
    # Debería fallar porque el código debe ser único
    assert duplicate_response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]

def test_obtener_asignatura_inexistente(client, db_session_test, admin_auth_headers):
    """Test para verificar la respuesta al solicitar una asignatura que no existe"""
    # Intentar obtener una asignatura con un ID que no existe
    response = client.get("/api/v1/subjects/9999", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_actualizar_asignatura_inexistente(client, db_session_test, admin_auth_headers):
    """Test para verificar la respuesta al actualizar una asignatura que no existe"""
    update_data = {
        "name": "Asignatura Inexistente",
        "code": "INE101",
        "description": "No debería actualizarse"
    }
    response = client.put("/api/v1/subjects/9999", json=update_data, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_eliminar_asignatura_inexistente(client, db_session_test, admin_auth_headers):
    """Test para verificar la respuesta al eliminar una asignatura que no existe"""
    response = client.delete("/api/v1/subjects/9999", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_campos_requeridos_crear_asignatura(client, db_session_test, admin_auth_headers):
    """Test para verificar que se requieren los campos obligatorios para crear una asignatura"""
    # Sin nombre
    subject_missing_name = {
        "code": "REQ101",
        "description": "Sin nombre"
    }
    response = client.post(
        "/api/v1/subjects",
        json=subject_missing_name,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Sin código
    subject_missing_code = {
        "name": "Asignatura sin código",
        "description": "Sin código"
    }
    response = client.post(
        "/api/v1/subjects",
        json=subject_missing_code,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # La descripción es opcional, debería crear correctamente
    subject_missing_description = {
        "name": "Asignatura sin descripción",
        "code": "DESC101"
    }
    response = client.post(
        "/api/v1/subjects",
        json=subject_missing_description,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    
def test_unauthorized_access(client, db_session_test):
    """Test para verificar que usuarios sin autenticación no pueden acceder"""
    # Intentar obtener la lista de asignaturas sin autenticación
    response = client.get("/api/v1/subjects")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Intentar crear una asignatura sin autenticación
    subject_data = {
        "name": "Prueba sin auth",
        "code": "NOAUTH",
        "description": "No debería crearse"
    }
    response = client.post("/api/v1/subjects", json=subject_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
