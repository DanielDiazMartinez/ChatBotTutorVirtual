from fastapi import status

def test_agregar_multiples_usuarios_asignatura(client, db_session_test, admin_auth_headers):
    """Test para verificar que se pueden añadir múltiples usuarios a una asignatura a la vez"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Programación",
        "code": "PRG101",
        "description": "Curso de programación"
    }
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert create_subject_response.status_code == status.HTTP_201_CREATED
    subject_id = create_subject_response.json()["data"]["id"]
    
    # Crear varios usuarios para la prueba
    users = []
    
    # Crear dos profesores
    teacher1_data = {
        "email": "profesor1_prog@example.com",
        "password": "password123",
        "full_name": "Profesor 1 Programación",
        "role": "teacher"
    }
    create_teacher1_response = client.post(
        "/api/v1/users/register",
        json=teacher1_data,
        headers=admin_auth_headers
    )
    assert create_teacher1_response.status_code == status.HTTP_201_CREATED
    teacher1_id = create_teacher1_response.json()["data"]["id"]
    users.append(teacher1_id)
    
    teacher2_data = {
        "email": "profesor2_prog@example.com",
        "password": "password123",
        "full_name": "Profesor 2 Programación",
        "role": "teacher"
    }
    create_teacher2_response = client.post(
        "/api/v1/users/register",
        json=teacher2_data,
        headers=admin_auth_headers
    )
    assert create_teacher2_response.status_code == status.HTTP_201_CREATED
    teacher2_id = create_teacher2_response.json()["data"]["id"]
    users.append(teacher2_id)
    
    # Crear dos estudiantes
    student1_data = {
        "email": "estudiante1_prog@example.com",
        "password": "password123",
        "full_name": "Estudiante 1 Programación",
        "role": "student"
    }
    create_student1_response = client.post(
        "/api/v1/users/register",
        json=student1_data,
        headers=admin_auth_headers
    )
    assert create_student1_response.status_code == status.HTTP_201_CREATED
    student1_id = create_student1_response.json()["data"]["id"]
    users.append(student1_id)
    
    student2_data = {
        "email": "estudiante2_prog@example.com",
        "password": "password123",
        "full_name": "Estudiante 2 Programación",
        "role": "student"
    }
    create_student2_response = client.post(
        "/api/v1/users/register",
        json=student2_data,
        headers=admin_auth_headers
    )
    assert create_student2_response.status_code == status.HTTP_201_CREATED
    student2_id = create_student2_response.json()["data"]["id"]
    users.append(student2_id)
    
    # Añadir los usuarios a la asignatura de forma masiva
    add_users_request = {
        "user_ids": users
    }
    
    add_users_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=add_users_request,
        headers=admin_auth_headers
    )
    
    assert add_users_response.status_code == status.HTTP_200_OK, f"Error: {add_users_response.text}"
    response_data = add_users_response.json()
    
    # Verificar que todos los usuarios fueron añadidos correctamente
    assert len(response_data["data"]["added"]) == 4, "No se añadieron todos los usuarios"
    assert len(response_data["data"]["failed"]) == 0, "Hubo errores al añadir usuarios"
    
    # Ahora intentamos verificar que al obtener la asignatura, aparecen todos los usuarios
    get_subject_response = client.get(
        f"/api/v1/subjects/{subject_id}",
        headers=admin_auth_headers
    )
    
    assert get_subject_response.status_code == status.HTTP_200_OK
    subject_data = get_subject_response.json()["data"]
    
    # Verificar que están los dos profesores
    teacher_ids = [teacher["id"] for teacher in subject_data["teachers"]]
    assert teacher1_id in teacher_ids, "Profesor 1 no está asociado a la asignatura"
    assert teacher2_id in teacher_ids, "Profesor 2 no está asociado a la asignatura"
    
    # Verificar que están los dos estudiantes
    student_ids = [student["id"] for student in subject_data["students"]]
    assert student1_id in student_ids, "Estudiante 1 no está asociado a la asignatura"
    assert student2_id in student_ids, "Estudiante 2 no está asociado a la asignatura"

def test_agregar_usuarios_asignatura_inexistente(client, db_session_test, admin_auth_headers):
    """Test para verificar el comportamiento al intentar añadir usuarios a una asignatura inexistente"""
    # ID de asignatura que no existe
    subject_id = 999
    
    # Crear un usuario de prueba
    user_data = {
        "email": "usuario_test@example.com",
        "password": "password123",
        "full_name": "Usuario Test",
        "role": "teacher"
    }
    create_user_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    assert create_user_response.status_code == status.HTTP_201_CREATED
    user_id = create_user_response.json()["data"]["id"]
    
    # Intentar añadir el usuario a una asignatura que no existe
    add_users_request = {
        "user_ids": [user_id]
    }
    
    add_users_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=add_users_request,
        headers=admin_auth_headers
    )
    
    # Verificar que se maneja correctamente el error
    assert add_users_response.status_code == status.HTTP_404_NOT_FOUND
    assert "Asignatura no encontrada" in add_users_response.text

def test_verificar_permisos_agregar_usuarios_masivo(client, db_session_test, admin_auth_headers, teacher_auth_headers, student_auth_headers):
    """Test para verificar que solo los administradores pueden agregar usuarios masivamente a asignaturas"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Diseño Web",
        "code": "DIS101",
        "description": "Curso de diseño web"
    }
    create_subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = create_subject_response.json()["data"]["id"]
    
    # Crear un usuario de prueba
    user_data = {
        "email": "usuario_permisos@example.com",
        "password": "password123",
        "full_name": "Usuario Permisos",
        "role": "student"
    }
    create_user_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    user_id = create_user_response.json()["data"]["id"]
    
    # Datos para la solicitud
    add_users_request = {
        "user_ids": [user_id]
    }
    
    # Profesor intenta agregar usuarios - debería fallar
    teacher_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=add_users_request,
        headers=teacher_auth_headers
    )
    assert teacher_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Estudiante intenta agregar usuarios - debería fallar
    student_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=add_users_request,
        headers=student_auth_headers
    )
    assert student_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Sin autenticación - debería fallar
    unauth_response = client.post(
        f"/api/v1/subjects/{subject_id}/users",
        json=add_users_request
    )
    assert unauth_response.status_code == status.HTTP_401_UNAUTHORIZED
