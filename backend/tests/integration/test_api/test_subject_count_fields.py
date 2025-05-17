from fastapi import status
from typing import Dict

def test_subject_count_fields_get_by_id(client, db_session_test, admin_auth_headers):
    """Verificar que los campos de conteo estén presentes en get_subject_by_id"""
    # Crear una asignatura
    subject_data = {
        "name": "Informática",
        "code": "INF101",
        "description": "Curso de informática"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_response.json()["data"]["id"]

    # Obtener la asignatura
    response = client.get(f"/api/v1/subjects/{subject_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()["data"]
    
    # Verificar que los campos de conteo estén presentes
    assert "teacher_count" in data
    assert "student_count" in data
    
    # Inicialmente debería ser 0
    assert data["teacher_count"] == 0
    assert data["student_count"] == 0

def test_subject_count_fields_in_list(client, db_session_test, admin_auth_headers):
    """Verificar que los campos de conteo estén presentes en get_all_subjects"""
    # Crear una asignatura
    subject_data = {
        "name": "Estadística",
        "code": "EST101",
        "description": "Curso de estadística"
    }
    client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )

    # Listar asignaturas
    response = client.get("/api/v1/subjects", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    subjects = response.json()["data"]
    
    # Verificar que haya al menos una asignatura
    assert len(subjects) > 0
    
    # Verificar que todas las asignaturas tengan los campos de conteo
    for subject in subjects:
        assert "teacher_count" in subject
        assert "student_count" in subject

def test_subject_count_fields_in_update(client, db_session_test, admin_auth_headers):
    """Verificar que los campos de conteo estén presentes después de actualizar"""
    # Crear una asignatura
    subject_data = {
        "name": "Programación",
        "code": "PRG101",
        "description": "Curso de programación"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_response.json()["data"]["id"]
    
    # Actualizar la asignatura
    update_data = {
        "name": "Programación Avanzada",
        "code": "PRG101",
        "description": "Curso avanzado de programación"
    }
    
    update_response = client.put(
        f"/api/v1/subjects/{subject_id}",
        json=update_data,
        headers=admin_auth_headers
    )
    
    assert update_response.status_code == status.HTTP_200_OK
    
    data = update_response.json()["data"]
    
    # Verificar que los campos de conteo estén presentes
    assert "teacher_count" in data
    assert "student_count" in data
