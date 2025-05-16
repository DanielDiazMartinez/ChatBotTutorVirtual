from fastapi import status

def test_crear_tema_como_admin(client, db_session_test, admin_auth_headers):
    
    subject_data = {
        "name": "Matemáticas",
        "code": "MAT101",
        "description": "Curso básico de matemáticas"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = subject_response.json()["id"]["data"]

    topic_data = {
        "name": "Álgebra Lineal",
        "description": "Introducción al álgebra lineal",
        "subject_id": subject_id
    }
    response = client.post(
        "/api/v1/topics",
        json=topic_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()["data"]
    assert data["name"] == topic_data["name"]
    assert data["description"] == topic_data["description"]
    assert data["subject_id"] == subject_id

def test_listar_temas(client, db_session_test, admin_auth_headers, teacher_auth_headers):
    # Test con admin
    response = client.get("/api/v1/topics", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Test con profesor
    response = client.get("/api/v1/topics", headers=teacher_auth_headers)
    assert response.status_code == status.HTTP_200_OK

def test_obtener_tema_por_id(client, db_session_test, admin_auth_headers):
    # Primero crear una asignatura y un tema
    subject_data = {
        "name": "Física",
        "code": "FIS101",
        "description": "Curso básico de física"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = subject_response.json()["id"]

    topic_data = {
        "name": "Mecánica Clásica",
        "description": "Leyes de Newton y aplicaciones",
        "subject_id": subject_id
    }
    create_response = client.post(
        "/api/v1/topics",
        json=topic_data,
        headers=admin_auth_headers
    )
    topic_id = create_response.json()["id"]

    # Obtener el tema creado
    response = client.get(f"/api/v1/topics/{topic_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == topic_data["name"]

def test_actualizar_tema(client, db_session_test, admin_auth_headers):
    # Primero crear una asignatura y un tema
    subject_data = {
        "name": "Química",
        "code": "QUI101",
        "description": "Curso básico de química"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = subject_response.json()["id"]

    topic_data = {
        "name": "Química Orgánica",
        "description": "Introducción a la química orgánica",
        "subject_id": subject_id
    }
    create_response = client.post(
        "/api/v1/topics",
        json=topic_data,
        headers=admin_auth_headers
    )
    topic_id = create_response.json()["id"]

    # Actualizar el tema
    update_data = {
        "name": "Química Orgánica Avanzada",
        "description": "Curso avanzado de química orgánica"
    }
    response = client.put(
        f"/api/v1/topics/{topic_id}",
        json=update_data,
        headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_eliminar_tema(client, db_session_test, admin_auth_headers):
    # Primero crear una asignatura y un tema
    subject_data = {
        "name": "Biología",
        "code": "BIO101",
        "description": "Curso básico de biología"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    subject_id = subject_response.json()["id"]

    topic_data = {
        "name": "Genética",
        "description": "Principios básicos de genética",
        "subject_id": subject_id
    }
    create_response = client.post(
        "/api/v1/topics",
        json=topic_data,
        headers=admin_auth_headers
    )
    topic_id = create_response.json()["id"]

    # Eliminar el tema
    response = client.delete(f"/api/v1/topics/{topic_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK

    # Verificar que el tema fue eliminado
    get_response = client.get(f"/api/v1/topics/{topic_id}", headers=admin_auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
