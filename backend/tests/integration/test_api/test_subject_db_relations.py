from fastapi import status

def test_verificar_profesores_en_base_de_datos(client, db_session_test, admin_auth_headers):
    """Test para verificar que se pueden asignar profesores a una asignatura (verificando en BD)"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Matemáticas Avanzadas",
        "code": "MAT201",
        "description": "Curso de matemáticas avanzadas"
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
        "email": "test_teacher_math@example.com",
        "password": "password123",
        "full_name": "Math Teacher",
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
    
    # Verificamos directamente en la base de datos
    from app.models.models import Subject
    db_subject = db_session_test.query(Subject).filter(Subject.id == subject_id).first()
    
    # Verifica que el profesor esté en la lista de usuarios de la asignatura
    teacher_ids = [user.id for user in db_subject.users]
    assert teacher_id in teacher_ids, "El profesor no está asignado a la asignatura"

def test_verificar_estudiantes_en_base_de_datos(client, db_session_test, admin_auth_headers):
    """Test para verificar que se pueden asignar estudiantes a una asignatura (verificando en BD)"""
    # Primero crear una asignatura
    subject_data = {
        "name": "Física Cuántica",
        "code": "FIS301",
        "description": "Curso de física cuántica"
    }
    create_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    subject_id = create_response.json()["data"]["id"]
    
    # Crear un nuevo estudiante para la prueba
    user_data = {
        "email": "test_student_physics@example.com",
        "password": "password123",
        "full_name": "Physics Student",
        "role": "student"
    }
    create_response = client.post(
        "/api/v1/users/register",
        json=user_data,
        headers=admin_auth_headers
    )
    student_id = create_response.json()["data"]["id"]
    
    # Añadir el estudiante a la asignatura
    add_response = client.post(
        f"/api/v1/subjects/{subject_id}/user/{student_id}",
        headers=admin_auth_headers
    )
    assert add_response.status_code == 200, f"Error al añadir estudiante: {add_response.text}"
    
    # Verificamos directamente en la base de datos
    from app.models.models import Subject
    db_subject = db_session_test.query(Subject).filter(Subject.id == subject_id).first()
    
    # Verifica que el estudiante esté en la lista de usuarios de la asignatura
    student_ids = [user.id for user in db_subject.users]
    assert student_id in student_ids, "El estudiante no está asignado a la asignatura"
