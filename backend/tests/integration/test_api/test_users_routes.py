# tests/integration/test_api/test_users_routes.py
from fastapi import status

def test_registrar_estudiante_exitoso(client, db_session_test, admin_auth_headers): # Añade admin_auth_headers
    student_data = {
        "email": "teststudent@example.com",
        "password": "password123",
        "full_name": "Test Student"
    }
    response = client.post(
        "/api/v1/users/register/student",
        json=student_data,
        headers=admin_auth_headers # <--- USA LOS HEADERS AQUÍ
    )
    assert response.status_code == status.HTTP_200_OK # O 201 Created, según tu implementación
    # ... más aserciones ...

def test_registrar_estudiante_email_duplicado(client, db_session_test, admin_auth_headers): # Añade admin_auth_headers
    # Primero, crea un estudiante (necesitarás autenticación también)
    initial_student_data = {"email": "duplicate@example.com", "password": "password123", "full_name": "First Student"}
    response_initial = client.post(
        "/api/v1/users/register/student",
        json=initial_student_data,
        headers=admin_auth_headers # <--- USA LOS HEADERS AQUÍ
    )
    assert response_initial.status_code == status.HTTP_200_OK # o 201

    # Intenta registrar otro con el mismo email
    duplicate_student_data = {"email": "duplicate@example.com", "password": "newpassword", "full_name": "Second Student"}
    response_duplicate = client.post(
        "/api/v1/users/register/student",
        json=duplicate_student_data,
        headers=admin_auth_headers # <--- USA LOS HEADERS AQUÍ
    )
    assert response_duplicate.status_code == status.HTTP_400_BAD_REQUEST
    # ... más aserciones ...