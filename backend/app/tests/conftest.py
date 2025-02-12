import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# Crear motor de base de datos de prueba
engine = create_engine(settings.TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Crea las tablas antes de correr los tests y las elimina después."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")  # <-- Cambiado a "module"
def db():
    """Devuelve una sesión de base de datos para los tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="module")  # <-- Ahora coincide con db
def client():
    """Cliente de pruebas para FastAPI."""
    with TestClient(app) as c:
        yield c
