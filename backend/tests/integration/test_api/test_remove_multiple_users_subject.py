from fastapi import status
import json

def test_eliminar_multiples_usuarios_asignatura(client, db_session_test, admin_auth_headers):
    """Test para verificar que se pueden eliminar múltiples usuarios de una asignatura a la vez"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Bases de Datos",
        "code": "BD101",
        "description": "Curso de bases de datos"
    }
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert create_subject_response.status_code == status.HTTP_201_CREATED
    subject_id = create_subject_response.json()["data"]["id"]
    
    # Crear usuarios para la prueba
    users = []
    
    # Crear un profesor
    teacher_data = {
        "email": "profesor_bd@example.com",
        "password": "password123",
        "full_name": "Profesor BD",
        "role": "teacher"
    }
    create_teacher_response = client.post(
        "/api/v1/users/register",
        json=teacher_data,
        headers=admin_auth_headers
    )
    assert create_teacher_response.status_code == status.HTTP_201_CREATED
    teacher_id = create_teacher_response.json()["data"]["id"]
    users.append(teacher_id)
    
    # Crear un estudiante
    student_data = {
        "email": "estudiante_bd@example.com",
        "password": "password123",
        "full_name": "Estudiante BD",
        "role": "student"
    }
    create_student_response = client.post(
        "/api/v1/users/register",
        json=student_data,
        headers=admin_auth_headers
    )
    assert create_student_response.status_code == status.HTTP_201_CREATED
    student_id = create_student_response.json()["data"]["id"]
    users.append(student_id)
    
    # Añadir los usuarios a la asignatura
    add_users_request = {
        "user_ids": users
    }
    
    client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=add_users_request,
        headers=admin_auth_headers
    )
    
    # Verificar que se agregaron correctamente
    get_subject_response = client.get(
        f"/api/v1/subjects/{subject_id}",
        headers=admin_auth_headers
    )
    subject_data = get_subject_response.json()["data"]
    
    teacher_ids = [teacher["id"] for teacher in subject_data["teachers"]]
    student_ids = [student["id"] for student in subject_data["students"]]
    
    assert teacher_id in teacher_ids
    assert student_id in student_ids
    
    # Ahora eliminar los usuarios de la asignatura
    remove_users_request = {
        "user_ids": users
    }
    
    remove_response = client.delete(
        f"/api/v1/subjects/{subject_id}/users",
        content=json.dumps(remove_users_request).encode('utf-8'),
        headers={**admin_auth_headers, 'Content-Type': 'application/json'}
    )
    
    assert remove_response.status_code == status.HTTP_200_OK
    response_data = remove_response.json()["data"]
    
    # Verificar que todos los usuarios fueron eliminados correctamente
    assert len(response_data["removed"]) == 2
    assert len(response_data["failed"]) == 0
    
    # Verificar que ya no están asociados a la asignatura
    get_subject_response = client.get(
        f"/api/v1/subjects/{subject_id}",
        headers=admin_auth_headers
    )
    
    subject_data = get_subject_response.json()["data"]
    
    teacher_ids = [teacher["id"] for teacher in subject_data["teachers"]]
    student_ids = [student["id"] for student in subject_data["students"]]
    
    assert teacher_id not in teacher_ids
    assert student_id not in student_ids

def test_eliminar_usuarios_asignatura_inexistente(client, db_session_test, admin_auth_headers):
    """Test para verificar el comportamiento al intentar eliminar usuarios de una asignatura inexistente"""
    # ID de asignatura que no existe
    subject_id = 999
    
    # Crear un usuario de prueba
    user_data = {
        "email": "usuario_eliminar@example.com",
        "password": "password123",
        "full_name": "Usuario Eliminar",
        "role": "teacher"
    }
    create_user_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    user_id = create_user_response.json()["data"]["id"]
    
    # Intentar eliminar el usuario de una asignatura que no existe
    remove_users_request = {
        "user_ids": [user_id]
    }
    
    remove_response = client.delete(
        f"/api/v1/subjects/{subject_id}/users",
        content=json.dumps(remove_users_request).encode('utf-8'),
        headers={**admin_auth_headers, 'Content-Type': 'application/json'}
    )
    
    # Verificar que se maneja correctamente el error
    assert remove_response.status_code == status.HTTP_404_NOT_FOUND
    assert "Asignatura no encontrada" in remove_response.text

def test_verificar_permisos_eliminar_usuarios_masivo(client, db_session_test, admin_auth_headers, teacher_auth_headers, student_auth_headers):
    """Test para verificar que solo los administradores pueden eliminar usuarios masivamente de asignaturas"""
    # Crear una asignatura
    subject_data = {
        "name": "Redes",
        "code": "RED101",
        "description": "Curso de redes"
    }
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_subject_response.json()["data"]["id"]
    
    # Crear un usuario
    user_data = {
        "email": "usuario_permisos_eliminar@example.com",
        "password": "password123",
        "full_name": "Usuario Permisos Eliminar",
        "role": "student"
    }
    create_user_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    user_id = create_user_response.json()["data"]["id"]
    
    # Datos para la solicitud
    remove_users_request = {
        "user_ids": [user_id]
    }
    
    # Profesor intenta eliminar usuarios - debería fallar
    teacher_response = client.delete(
        f"/api/v1/subjects/{subject_id}/users",
        content=json.dumps(remove_users_request).encode('utf-8'),
        headers={**teacher_auth_headers, 'Content-Type': 'application/json'}
    )
    assert teacher_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Estudiante intenta eliminar usuarios - debería fallar
    student_response = client.delete(
        f"/api/v1/subjects/{subject_id}/users",
        content=json.dumps(remove_users_request).encode('utf-8'),
        headers={**student_auth_headers, 'Content-Type': 'application/json'}
    )
    assert student_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Sin autenticación - debería fallar
    unauth_response = client.delete(
        f"/api/v1/subjects/{subject_id}/users",
        content=json.dumps(remove_users_request).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    assert unauth_response.status_code == status.HTTP_401_UNAUTHORIZED
