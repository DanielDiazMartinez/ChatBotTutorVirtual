import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.models import User
from app.core.security import create_access_token

def create_test_user(db_session: Session):
    """Crear un usuario de prueba para los tests"""
    test_user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",  # En un caso real usaríamos get_password_hash
        role="student"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    return test_user

def test_get_me_endpoint(client: TestClient, db_session_test: Session):
    """Test para verificar el funcionamiento del endpoint /me"""
    # Crear usuario de prueba
    test_user = create_test_user(db_session_test)
    
    # Crear token de acceso para ese usuario
    token = create_access_token({"sub": str(test_user.id), "role": test_user.role})
    
    # Realizar petición con el token
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    assert data["data"]["id"] == test_user.id
    assert data["data"]["email"] == test_user.email
    
    # Limpiar
    db_session_test.delete(test_user)
    db_session_test.commit()

def test_get_me_unauthorized(client: TestClient):
    """Test para verificar que se requiere autenticación"""
    # Realizar petición sin token
    response = client.get("/api/v1/users/me")
    
    # Verificar que se recibe un error de autenticación
    assert response.status_code == 401
