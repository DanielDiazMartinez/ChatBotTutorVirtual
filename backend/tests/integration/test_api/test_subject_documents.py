from fastapi import status
import pytest
from sqlalchemy.orm import Session
import os
import tempfile

from app.models.models import Subject, Document, User


def test_get_subject_documents(client, db_session_test, admin_auth_headers, teacher_auth_headers):
    """Test para verificar la obtención de documentos de una asignatura"""
    
    # 1. Crear un profesor para los documentos
    teacher = User(
        email="teacher_test_doc@example.com",
        full_name="Teacher Test Doc",
        hashed_password="hashed_password",
        role="teacher"
    )
    db_session_test.add(teacher)
    db_session_test.commit()
    db_session_test.refresh(teacher)
    
    # 2. Crear una asignatura de prueba
    subject_data = {
        "name": "Física Aplicada",
        "code": "FIS202",
        "description": "Curso avanzado de física"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == status.HTTP_201_CREATED
    subject_id = subject_response.json()["data"]["id"]
    
    # 3. Crear documentos asociados a la asignatura
    db = db_session_test
    
    # Crear documentos de prueba en la base de datos
    doc1 = Document(
        title="Introducción a la Física",
        description="Conceptos básicos de física",
        teacher_id=teacher.id,
        subject_id=subject_id
    )
    
    doc2 = Document(
        title="Dinámica de partículas",
        description="Estudio del movimiento",
        teacher_id=teacher.id,
        subject_id=subject_id
    )
    
    db.add(doc1)
    db.add(doc2)
    db.commit()
    
    # 3. Obtener los documentos usando el endpoint
    response = client.get(
        f"/api/v1/subjects/{subject_id}/documents",
        headers=admin_auth_headers
    )
    
    # 4. Verificar respuesta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) == 2
    assert any(doc["title"] == "Introducción a la Física" for doc in data)
    assert any(doc["title"] == "Dinámica de partículas" for doc in data)
    

def test_get_documents_nonexistent_subject(client, admin_auth_headers):
    """Test para verificar comportamiento con asignaturas inexistentes"""
    
    # Intentar obtener documentos de una asignatura que no existe
    response = client.get(
        "/api/v1/subjects/99999/documents",
        headers=admin_auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Asignatura no encontrada" in response.json()["detail"]


def test_get_subject_documents_empty(client, db_session_test, admin_auth_headers):
    """Test para verificar el comportamiento con asignatura sin documentos"""
    
    # 1. Crear una asignatura de prueba
    subject_data = {
        "name": "Química General",
        "code": "QUIM101",
        "description": "Introducción a la química"
    }
    subject_response = client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=admin_auth_headers
    )
    assert subject_response.status_code == status.HTTP_201_CREATED
    subject_id = subject_response.json()["data"]["id"]
    
    # 2. Obtener los documentos usando el endpoint
    response = client.get(
        f"/api/v1/subjects/{subject_id}/documents",
        headers=admin_auth_headers
    )
    
    # 3. Verificar que la asignatura existe pero no tiene documentos
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) == 0
