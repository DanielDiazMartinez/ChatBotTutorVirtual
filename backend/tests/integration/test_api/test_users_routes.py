from fastapi import status

def test_registrar_usuario_admin(client, db_session_test, admin_auth_headers):
    admin_data = {
        "email": "newadmin@example.com",
        "password": "password123",
        "full_name": "New Admin",
        "role": "admin"
    }
    response = client.post(
        "/api/v1/users/register",
        json=admin_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()["data"]
    assert data["email"] == admin_data["email"]
    assert data["role"] == "admin"

def test_registrar_profesor(client, db_session_test, admin_auth_headers):
    teacher_data = {
        "email": "newteacher@example.com",
        "password": "password123",
        "full_name": "New Teacher",
        "role": "teacher"
    }
    response = client.post(
        "/api/v1/users/register",
        json=teacher_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()["data"]
    assert data["email"] == teacher_data["email"]
    assert data["role"] == "teacher"

def test_registrar_estudiante(client, db_session_test, admin_auth_headers):
    student_data = {
        "email": "teststudent@example.com",
        "password": "password123",
        "full_name": "Test Student",
        "role": "student"
    }
    response = client.post(
        "/api/v1/users/register",
        json=student_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()["data"]
    assert data["email"] == student_data["email"]
    assert data["role"] == "student"

def test_listar_usuarios_por_rol(client, db_session_test, admin_auth_headers, teacher_auth_headers):
    # Verificar que exista al menos un estudiante para listar
    student_data = {
        "email": "student_to_list@example.com",
        "password": "password123",
        "full_name": "Student To List",
        "role": "student"
    }
    create_response = client.post(
        "/api/v1/users/register",
        json=student_data,
        headers=admin_auth_headers
    )
    
    # Test como admin
    response = client.get("/api/v1/users/list/student", headers=admin_auth_headers)
    
    assert response.status_code == status.HTTP_200_OK, f"Falló con status code: {response.status_code}, respuesta: {response.text}"

    # Test como profesor
    response = client.get("/api/v1/users/list/student", headers=teacher_auth_headers)
    assert response.status_code == status.HTTP_200_OK, f"Falló con status code: {response.status_code}, respuesta: {response.text}"


def test_obtener_usuario_por_id(client, db_session_test, admin_auth_headers):
    # Primero crear un usuario
    user_data = {
        "email": "getuser@example.com",
        "password": "password123",
        "full_name": "Get User Test",
        "role": "student"
    }
    create_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    user_id = create_response.json()["data"]["id"]

    # Obtener el usuario creado
    response = client.get(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["email"] == user_data["email"]

def test_actualizar_usuario(client, db_session_test, admin_auth_headers):
    # Primero crear un usuario
    user_data = {
        "email": "updateuser@example.com",
        "password": "password123",
        "full_name": "Update User Test",
        "role": "student"
    }
    create_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    user_id = create_response.json()["data"]["id"]

    # Actualizar el usuario
    update_data = {
        "full_name": "Updated Name",
        "password": "newpassword123"
    }
    response = client.put(
        f"/api/v1/users/{user_id}",
        json=update_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["full_name"] == update_data["full_name"]

def test_eliminar_usuario(client, db_session_test, admin_auth_headers):
    # Primero crear un usuario
    user_data = {
        "email": "deleteuser@example.com",
        "password": "password123",
        "full_name": "Delete User Test",
        "role": "student"
    }
    create_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    user_id = create_response.json()["data"]["id"]

    # Eliminar el usuario
    response = client.delete(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK

    # Verificar que el usuario fue eliminado
    get_response = client.get(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_registrar_usuario_email_duplicado(client, db_session_test, admin_auth_headers):
    initial_user_data = {
        "email": "duplicate_test@example.com",
        "password": "password123",
        "full_name": "First User",
        "role": "student"
    }
    response_initial = client.post(
        "/api/v1/users/register",
        json=initial_user_data,
        headers=admin_auth_headers
    )

    if response_initial.status_code != status.HTTP_201_CREATED:
        print("Error al registrar el estudiante inicial en test_registrar_estudiante_email_duplicado:")
        try:
            print(response_initial.json())
        except ValueError:
            print(response_initial.text)

    assert response_initial.status_code == status.HTTP_201_CREATED

    duplicate_student_data = {
        "email": "duplicate_test@example.com",
        "password": "newpassword",
        "full_name": "Second Student Duplicate Test",
        "role": "student"
    }
    response_duplicate = client.post(
        "/api/v1/users/register",
        json=duplicate_student_data,
        headers=admin_auth_headers
    )

    if response_duplicate.status_code != status.HTTP_400_BAD_REQUEST:
        print("Error al intentar registrar estudiante duplicado:")
        try:
            print(response_duplicate.json())
        except ValueError:
            print(response_duplicate.text)
            
    assert response_duplicate.status_code == status.HTTP_400_BAD_REQUEST
    error_data = response_duplicate.json()
    assert error_data["detail"] == "Email already registered"