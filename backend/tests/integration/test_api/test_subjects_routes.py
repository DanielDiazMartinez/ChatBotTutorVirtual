from fastapi import status
from typing import Dict

def test_crear_asignatura_como_admin(client, db_session_test, admin_auth_headers):
    subject_data = {
        "name": "Matemáticas",
        "code": "MAT101",
        "description": "Curso básico de matemáticas"
    }
    response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == subject_data["name"]
    assert data["code"] == subject_data["code"]
    assert data["description"] == subject_data["description"]

def test_listar_asignaturas(client, db_session_test, admin_auth_headers, teacher_auth_headers, student_auth_headers):
    # Test con admin
    response = client.get("/api/v1/subjects", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Test con profesor
    response = client.get("/api/v1/subjects", headers=teacher_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Test con estudiante
    response = client.get("/api/v1/subjects", headers=student_auth_headers)
    assert response.status_code == status.HTTP_200_OK

def test_obtener_asignatura_por_id(client, db_session_test, admin_auth_headers):
    # Primero crear una asignatura
    subject_data = {
        "name": "Física",
        "code": "FIS101",
        "description": "Curso básico de física"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_response.json()["id"]

    # Obtener la asignatura creada
    response = client.get(f"/api/v1/subjects/{subject_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == subject_data["name"]

def test_actualizar_asignatura(client, db_session_test, admin_auth_headers):
    # Primero crear una asignatura
    subject_data = {
        "name": "Química",
        "code": "QUI101",
        "description": "Curso básico de química"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_response.json()["id"]

    # Actualizar la asignatura
    update_data = {
        "name": "Química Avanzada",
        "code": "QUI101",  
        "description": "Curso avanzado de química"
    }
    response = client.put(
        f"/api/v1/subjects/{subject_id}",
        json=update_data,
        headers=admin_auth_headers
    )

    print("Response status:", response.status_code)
    print("Response body:", response.text)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["code"] == update_data["code"]
    assert data["description"] == update_data["description"]

def test_eliminar_asignatura(client, db_session_test, admin_auth_headers):
    # Primero crear una asignatura
    subject_data = {
        "name": "Biología",
        "code": "BIO101",
        "description": "Curso básico de biología"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_response.json()["id"]

    # Eliminar la asignatura
    response = client.delete(f"/api/v1/subjects/{subject_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK

    # Verificar que la asignatura fue eliminada
    get_response = client.get(f"/api/v1/subjects/{subject_id}", headers=admin_auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
