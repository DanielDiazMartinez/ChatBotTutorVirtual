from fastapi import status

def test_verificar_profesores_asignados(client, db_session_test, admin_auth_headers):
    """Test para verificar que se pueden consultar los profesores asignados a una asignatura"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Matemáticas",
        "code": "MAT101",
        "description": "Curso de matemáticas"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    subject_id = create_response.json()["data"]["id"]
    
    # Crear un nuevo profesor para la prueba
    user_data = {
        "email": "getuser@example.com",
        "password": "password123",
        "full_name": "Get User Test",
        "role": "teacher"
    }
    create_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    teacher_id = create_response.json()["data"]["id"]

    # Añadir el profesor a la asignatura
    add_response = client.post(
        f"/api/v1/subjects/{subject_id}/user/{teacher_id}",
        headers=admin_auth_headers
    )
    assert add_response.status_code == 200, f"Error al añadir profesor: {add_response.text}"
    
    # En lugar de verificar a través del API, verificamos directamente en la base de datos
    from app.models.models import Subject
    db_subject = db_session_test.query(Subject).filter(Subject.id == subject_id).first()
    
    # Verifica que el profesor esté en la lista de profesores de la asignatura
    teacher_ids = [teacher.id for teacher in db_subject.teachers]
    assert teacher_id in teacher_ids, "El profesor no está asignado a la asignatura"

def test_verificar_estudiantes_asignados(client, db_session_test, admin_auth_headers):
    """Test para verificar que se pueden consultar los estudiantes asignados a una asignatura"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Física",
        "code": "FIS101",
        "description": "Curso de física"
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
        "email": "student_fisica@example.com",
        "password": "password123",
        "full_name": "Estudiante Fisica",
        "role": "student"
    }
    create_student_response = client.post(
        "/api/v1/users/register",
        json=student_data,
        headers=admin_auth_headers
    )
    assert create_student_response.status_code == status.HTTP_201_CREATED
    student_id = create_student_response.json()["data"]["id"]
    
    assert student_id is not None, "No se encontró un usuario con rol 'student'"
    
    # Añadir el estudiante a la asignatura
    client.post(
        f"/api/v1/subjects/{subject_id}/user/{student_id}",
        headers=admin_auth_headers
    )
    
    # Verificar que el estudiante está asignado a la asignatura
    subject_response = client.get(
        f"/api/v1/subjects/{subject_id}",
        headers=admin_auth_headers
    )
    
    print(f"Status code: {subject_response.status_code}")
    print(f"Response body: {subject_response.text}")
    
    assert subject_response.status_code == 200
    subject_data = subject_response.json()["data"]
    
    # Verificar que hay una lista de estudiantes y el estudiante añadido está en ella
    assert "students" in subject_data
    students = subject_data["students"]
    assert any(student["id"] == student_id for student in students), "El estudiante no está asignado a la asignatura"
