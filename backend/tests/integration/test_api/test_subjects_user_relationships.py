from fastapi import status
from typing import Dict


def test_agregar_profesor_a_asignatura(client, db_session_test, admin_auth_headers, teacher_auth_headers):
    """Test para verificar que se puede añadir un profesor a una asignatura"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Historia",
        "code": "HIS101",
        "description": "Curso de historia"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    subject_id = create_response.json()["data"]["id"]
    
    # Crear un nuevo profesor para la prueba
    teacher_data = {
        "email": "profesor_historia@example.com",
        "password": "password123",
        "full_name": "Profesor Historia",
        "role": "teacher"
    }
    create_teacher_response = client.post(
        "/api/v1/users/register",
        json=teacher_data,
        headers=admin_auth_headers
    )

    assert create_teacher_response.status_code == status.HTTP_201_CREATED
    teacher_id = create_teacher_response.json()["data"]["id"]
    
    # Añadir el profesor a la asignatura
    teacher_add_response = client.post(
        f"/api/v1/subjects/{subject_id}/user/{teacher_id}",
        headers=admin_auth_headers
    )
    
    assert teacher_add_response.status_code == 200, f"Error al añadir profesor: {teacher_add_response.text}"
    assert "message" in teacher_add_response.json()
    assert "correctamente" in teacher_add_response.json()["message"]

def test_agregar_estudiante_a_asignatura(client, db_session_test, admin_auth_headers, student_auth_headers):
    """Test para verificar que se puede añadir un estudiante a una asignatura"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Biología",
        "code": "BIO201",
        "description": "Curso de biología"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    subject_id = create_response.json()["data"]["id"]
    
    # Crear un nuevo estudiante para la prueba
    student_data = {
        "email": "estudiante_biologia@example.com",
        "password": "password123",
        "full_name": "Estudiante Biologia",
        "role": "student"
    }
    create_student_response = client.post(
        "/api/v1/users/register",
        json=student_data,
        headers=admin_auth_headers
    )
    assert create_student_response.status_code == status.HTTP_201_CREATED
    student_id = create_student_response.json()["data"]["id"]
    
    # Añadir el estudiante a la asignatura
    student_add_response = client.post(
        f"/api/v1/subjects/{subject_id}/user/{student_id}",
        headers=admin_auth_headers
    )
    
    assert student_add_response.status_code == 200, f"Error al añadir estudiante: {student_add_response.text}"
    assert "message" in student_add_response.json()
    assert "correctamente" in student_add_response.json()["message"]

def test_verificar_permisos_para_agregar_usuarios(client, db_session_test, admin_auth_headers, 
                                                 teacher_auth_headers, student_auth_headers):
    """Test para verificar que solo administradores pueden agregar usuarios a asignaturas"""
    # Crear una asignatura para la prueba
    subject_data = {
        "name": "Química Orgánica",
        "code": "QUI201",
        "description": "Curso de química orgánica"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_response.json()["data"]["id"]
    
    # Crear un nuevo profesor para la prueba
    teacher_data = {
        "email": "profesor_test@example.com",
        "password": "password123",
        "full_name": "Profesor Test",
        "role": "teacher"
    }
    create_teacher_response = client.post(
        "/api/v1/users/register",
        json=teacher_data,
        headers=admin_auth_headers
    )
    assert create_teacher_response.status_code == status.HTTP_201_CREATED
    user_id = create_teacher_response.json()["data"]["id"]
    
    # Profesor intenta agregar un usuario - debería fallar
    teacher_response = client.post(
        f"/api/v1/subjects/{subject_id}/user/{user_id}",
        headers=teacher_auth_headers
    )
    assert teacher_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Estudiante intenta agregar un usuario - debería fallar
    student_response = client.post(
        f"/api/v1/subjects/{subject_id}/user/{user_id}",
        headers=student_auth_headers
    )
    assert student_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Usuario sin autenticación intenta agregar - debería fallar con 401
    unauth_response = client.post(f"/api/v1/subjects/{subject_id}/user/{user_id}")
    assert unauth_response.status_code == status.HTTP_401_UNAUTHORIZED
