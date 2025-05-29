from fastapi import status
import pytest
from sqlalchemy.orm import Session

from app.models.models import Subject, User


def test_get_subject_users_success(client, db_session_test, admin_auth_headers):
    """Test para verificar la obtención exitosa de usuarios de una asignatura"""
    
    # 1. Crear usuarios de prueba
    teacher = User(
        email="teacher_test@example.com",
        full_name="Teacher Test",
        hashed_password="hashed_password",
        role="teacher"
    )
    student1 = User(
        email="student1_test@example.com",
        full_name="Student One",
        hashed_password="hashed_password",
        role="student"
    )
    student2 = User(
        email="student2_test@example.com",
        full_name="Student Two", 
        hashed_password="hashed_password",
        role="student"
    )
    
    db_session_test.add_all([teacher, student1, student2])
    db_session_test.commit()
    db_session_test.refresh(teacher)
    db_session_test.refresh(student1)
    db_session_test.refresh(student2)
    
    # 2. Crear una asignatura
    subject_data = {
        "name": "Matemáticas Básicas",
        "code": "MAT100",
        "description": "Curso introductorio de matemáticas"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == status.HTTP_201_CREATED
    subject_id = subject_response.json()["data"]["id"]
    
    # 3. Agregar usuarios a la asignatura
    users_to_add = {
        "user_ids": [teacher.id, student1.id, student2.id]
    }
    add_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=users_to_add,
        headers=admin_auth_headers
    )
    assert add_response.status_code == status.HTTP_200_OK
    
    # 4. Obtener usuarios de la asignatura
    response = client.get(
        f"/api/v1/subjects/{subject_id}/users",
        headers=admin_auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    
    # Verificar estructura de respuesta
    assert "subject_id" in data
    assert "subject_name" in data
    assert "subject_code" in data
    assert "teachers" in data
    assert "students" in data
    assert "teacher_count" in data
    assert "student_count" in data
    assert "total_users" in data
    
    # Verificar datos de la asignatura
    assert data["subject_id"] == subject_id
    assert data["subject_name"] == subject_data["name"]
    assert data["subject_code"] == subject_data["code"]
    
    # Verificar conteo de usuarios
    assert data["teacher_count"] == 1
    assert data["student_count"] == 2
    assert data["total_users"] == 3
    
    # Verificar profesores
    assert len(data["teachers"]) == 1
    teacher_data = data["teachers"][0]
    assert teacher_data["id"] == teacher.id
    assert teacher_data["email"] == teacher.email
    assert teacher_data["full_name"] == teacher.full_name
    assert teacher_data["role"] == "teacher"
    
    # Verificar estudiantes
    assert len(data["students"]) == 2
    student_emails = [s["email"] for s in data["students"]]
    assert student1.email in student_emails
    assert student2.email in student_emails


def test_get_subject_users_empty_subject(client, db_session_test, admin_auth_headers):
    """Test para verificar el comportamiento con asignatura sin usuarios"""
    
    # Crear una asignatura sin usuarios
    subject_data = {
        "name": "Física Avanzada",
        "code": "FIS200",
        "description": "Curso avanzado de física"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == status.HTTP_201_CREATED
    subject_id = subject_response.json()["data"]["id"]
    
    # Obtener usuarios de la asignatura vacía
    response = client.get(
        f"/api/v1/subjects/{subject_id}/users",
        headers=admin_auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    
    # Verificar que la asignatura existe pero no tiene usuarios
    assert data["subject_id"] == subject_id
    assert data["subject_name"] == subject_data["name"]
    assert data["teachers"] == []
    assert data["students"] == []
    assert data["teacher_count"] == 0
    assert data["student_count"] == 0
    assert data["total_users"] == 0


def test_get_subject_users_nonexistent_subject(client, admin_auth_headers):
    """Test para verificar comportamiento con asignatura inexistente"""
    
    response = client.get(
        "/api/v1/subjects/9999/users",
        headers=admin_auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Asignatura no encontrada" in response.json()["detail"]


def test_get_subject_users_permissions(client, db_session_test, admin_auth_headers, 
                                      teacher_auth_headers, student_auth_headers):
    """Test para verificar permisos de acceso al endpoint"""
    
    # Crear una asignatura
    subject_data = {
        "name": "Química Orgánica",
        "code": "QUI300",
        "description": "Curso de química orgánica"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == status.HTTP_201_CREATED
    subject_id = subject_response.json()["data"]["id"]
    
    # Test con admin - debería funcionar
    admin_response = client.get(
        f"/api/v1/subjects/{subject_id}/users",
        headers=admin_auth_headers
    )
    assert admin_response.status_code == status.HTTP_200_OK
    
    # Test con teacher - debería funcionar
    teacher_response = client.get(
        f"/api/v1/subjects/{subject_id}/users",
        headers=teacher_auth_headers
    )
    assert teacher_response.status_code == status.HTTP_200_OK
    
    # Test con student - debería funcionar
    student_response = client.get(
        f"/api/v1/subjects/{subject_id}/users",
        headers=student_auth_headers
    )
    assert student_response.status_code == status.HTTP_200_OK


def test_get_subject_users_only_teachers(client, db_session_test, admin_auth_headers):
    """Test para verificar comportamiento con asignatura que solo tiene profesores"""
    
    # Crear profesores
    teacher1 = User(
        email="teacher1_only@example.com",
        full_name="Teacher One Only",
        hashed_password="hashed_password",
        role="teacher"
    )
    teacher2 = User(
        email="teacher2_only@example.com",
        full_name="Teacher Two Only",
        hashed_password="hashed_password", 
        role="teacher"
    )
    
    db_session_test.add_all([teacher1, teacher2])
    db_session_test.commit()
    db_session_test.refresh(teacher1)
    db_session_test.refresh(teacher2)
    
    # Crear asignatura
    subject_data = {
        "name": "Seminario de Investigación",
        "code": "SEM400", 
        "description": "Seminario para profesores"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == status.HTTP_201_CREATED
    subject_id = subject_response.json()["data"]["id"]
    
    # Agregar solo profesores
    users_to_add = {
        "user_ids": [teacher1.id, teacher2.id]
    }
    add_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=users_to_add,
        headers=admin_auth_headers
    )
    assert add_response.status_code == status.HTTP_200_OK
    
    # Verificar usuarios
    response = client.get(
        f"/api/v1/subjects/{subject_id}/users",
        headers=admin_auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    
    assert data["teacher_count"] == 2
    assert data["student_count"] == 0
    assert data["total_users"] == 2
    assert len(data["teachers"]) == 2
    assert len(data["students"]) == 0


def test_get_subject_users_only_students(client, db_session_test, admin_auth_headers):
    """Test para verificar comportamiento con asignatura que solo tiene estudiantes"""
    
    # Crear estudiantes
    student1 = User(
        email="student1_only@example.com",
        full_name="Student One Only",
        hashed_password="hashed_password",
        role="student"
    )
    student2 = User(
        email="student2_only@example.com", 
        full_name="Student Two Only",
        hashed_password="hashed_password",
        role="student"
    )
    student3 = User(
        email="student3_only@example.com",
        full_name="Student Three Only", 
        hashed_password="hashed_password",
        role="student"
    )
    
    db_session_test.add_all([student1, student2, student3])
    db_session_test.commit()
    db_session_test.refresh(student1)
    db_session_test.refresh(student2)
    db_session_test.refresh(student3)
    
    # Crear asignatura
    subject_data = {
        "name": "Taller de Estudiantes",
        "code": "TAL100",
        "description": "Taller exclusivo para estudiantes"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == status.HTTP_201_CREATED
    subject_id = subject_response.json()["data"]["id"]
    
    # Agregar solo estudiantes
    users_to_add = {
        "user_ids": [student1.id, student2.id, student3.id]
    }
    add_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=users_to_add,
        headers=admin_auth_headers
    )
    assert add_response.status_code == status.HTTP_200_OK
    
    # Verificar usuarios
    response = client.get(
        f"/api/v1/subjects/{subject_id}/users",
        headers=admin_auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    
    assert data["teacher_count"] == 0
    assert data["student_count"] == 3
    assert data["total_users"] == 3
    assert len(data["teachers"]) == 0
    assert len(data["students"]) == 3
