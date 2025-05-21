# tests/unit/test_services/test_user_service.py
from unittest.mock import MagicMock # o pytest-mock: mocker
import pytest # Para usar pytest.raises

from app.services.user_service import create_user # Usamos la función existente
from app.models.schemas import UserCreate
from fastapi import HTTPException # Si tu servicio lanza estas excepciones

def test_registrar_teacher_nuevo(mocker): # Usando pytest-mock
    mock_db = MagicMock()
    # Simula que el profesor no existe
    mocker.patch.object(mock_db, 'query')
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Usamos UserCreate en lugar de TeacherCreate
    teacher_data = UserCreate(email="newteacher@example.com", password="securepassword", full_name="New Teacher", role="teacher")
    
    # Llama a la función del servicio
    created_teacher = create_user(teacher_data, mock_db)
    
    assert created_teacher["email"] == teacher_data.email
    assert created_teacher["full_name"] == teacher_data.full_name
    assert created_teacher["role"] == "teacher"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_registrar_teacher_existente(mocker):
    mock_db = MagicMock()
    existing_teacher_mock = MagicMock() # Simula un objeto profesor ya existente
    # Simula que el profesor ya existe
    mocker.patch.object(mock_db, 'query')
    mock_db.query.return_value.filter.return_value.first.return_value = existing_teacher_mock
    
    # Usamos UserCreate en lugar de TeacherCreate
    teacher_data = UserCreate(email="existingteacher@example.com", password="securepassword", full_name="Existing Teacher", role="teacher")
    
    with pytest.raises(HTTPException) as exc_info:
        create_user(teacher_data, mock_db)
    
    assert exc_info.value.status_code == 400
    assert "Email already registered" in str(exc_info.value.detail) # Ajusta al mensaje real
    mock_db.add.assert_not_called() # No se debería haber llamado a add