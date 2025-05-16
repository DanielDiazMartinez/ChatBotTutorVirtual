from fastapi import status
from typing import Dict

def test_crear_asignatura_permisos(client, db_session_test, admin_auth_headers, teacher_auth_headers, student_auth_headers):
    """Test para verificar que solo los administradores pueden crear asignaturas"""
    subject_data = {
        "name": "Matemáticas Avanzadas",
        "code": "MAT202",
        "description": "Curso avanzado de matemáticas"
    }
    
    # Administrador debería poder crear una asignatura
    admin_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert admin_response.status_code == status.HTTP_201_CREATED
    
    # Crear una asignatura con un código diferente para los siguientes tests
    subject_data["code"] = "MAT203"
    
    # Profesor no debería poder crear una asignatura
    teacher_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=teacher_auth_headers
    )
    assert teacher_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Estudiante no debería poder crear una asignatura
    student_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=student_auth_headers
    )
    assert student_response.status_code == status.HTTP_403_FORBIDDEN

def test_modificar_asignatura_permisos(client, db_session_test, admin_auth_headers, teacher_auth_headers, student_auth_headers):
    """Test para verificar que solo los administradores pueden modificar asignaturas"""
    # Primero crear una asignatura como admin
    subject_data = {
        "name": "Física Básica",
        "code": "FIS201",
        "description": "Curso básico de física"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_response.json()["id"]
    
    update_data = {
        "name": "Física Modificada",
        "code": "FIS201",
        "description": "Descripción modificada"
    }
    
    # Administrador debería poder modificar una asignatura
    admin_response = client.put(
        f"/api/v1/subjects/{subject_id}",
        json=update_data,
        headers=admin_auth_headers
    )
    assert admin_response.status_code == status.HTTP_200_OK
    assert admin_response.json()["name"] == "Física Modificada"
    
    # Profesor no debería poder modificar una asignatura
    teacher_response = client.put(
        f"/api/v1/subjects/{subject_id}",
        json=update_data,
        headers=teacher_auth_headers
    )
    assert teacher_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Estudiante no debería poder modificar una asignatura
    student_response = client.put(
        f"/api/v1/subjects/{subject_id}",
        json=update_data,
        headers=student_auth_headers
    )
    assert student_response.status_code == status.HTTP_403_FORBIDDEN

def test_eliminar_asignatura_permisos(client, db_session_test, admin_auth_headers, teacher_auth_headers, student_auth_headers):
    """Test para verificar que solo los administradores pueden eliminar asignaturas"""
    # Primero crear asignaturas para cada prueba
    subject_data_admin = {
        "name": "Asignatura para eliminar por admin",
        "code": "DEL101",
        "description": "Descripción"
    }
    admin_create = client.post(
        "/api/v1/subjects",
        json=subject_data_admin,
        headers=admin_auth_headers
    )
    subject_id_admin = admin_create.json()["id"]
    
    subject_data_teacher = {
        "name": "Asignatura para intent por profesor",
        "code": "DEL102",
        "description": "Descripción"
    }
    teacher_create = client.post(
        "/api/v1/subjects",
        json=subject_data_teacher,
        headers=admin_auth_headers
    )
    subject_id_teacher = teacher_create.json()["id"]
    
    subject_data_student = {
        "name": "Asignatura para intent por estudiante",
        "code": "DEL103",
        "description": "Descripción"
    }
    student_create = client.post(
        "/api/v1/subjects",
        json=subject_data_student,
        headers=admin_auth_headers
    )
    subject_id_student = student_create.json()["id"]
    
    # Admin debería poder eliminar
    admin_response = client.delete(
        f"/api/v1/subjects/{subject_id_admin}",
        headers=admin_auth_headers
    )
    assert admin_response.status_code == status.HTTP_200_OK
    
    # Profesor no debería poder eliminar
    teacher_response = client.delete(
        f"/api/v1/subjects/{subject_id_teacher}",
        headers=teacher_auth_headers
    )
    assert teacher_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Estudiante no debería poder eliminar
    student_response = client.delete(
        f"/api/v1/subjects/{subject_id_student}",
        headers=student_auth_headers
    )
    assert student_response.status_code == status.HTTP_403_FORBIDDEN
