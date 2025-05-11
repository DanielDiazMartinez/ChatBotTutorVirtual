import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker,Session

from app.core.security import get_password_hash
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.models import Admin
from app.services.user_service import get_user_by_email
from typing import Iterator

SQLALCHEMY_DATABASE_URL_TEST = settings.TEST_DATABASE_URL


engine_test = create_engine(SQLALCHEMY_DATABASE_URL_TEST)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Fixture para crear las tablas y la extensión ANTES de la sesión de tests
# y borrarlas DESPUÉS.
@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown():
    with engine_test.connect() as connection:
        try:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            connection.commit()
            print("DEBUG: Extensión 'vector' creada/verificada.")
        except Exception as e:
            print(f"DEBUG: Error al intentar crear la extensión 'vector': {e}")

    try:
        print("DEBUG: Intentando Base.metadata.create_all()")
        Base.metadata.create_all(bind=engine_test)
        print("DEBUG: Base.metadata.create_all() ejecutado.")
    except Exception as e:
        print(f"DEBUG: Error durante Base.metadata.create_all: {e}")
        raise

    yield # Los tests se ejecutan aquí

    # Borrar todas las tablas después de que todos los tests de la sesión hayan terminado
    print("DEBUG: Intentando Base.metadata.drop_all()")
    Base.metadata.drop_all(bind=engine_test)
    print("DEBUG: Base.metadata.drop_all() ejecutado.")


# Fixture para la sesión de base de datos de prueba por función (test individual)
@pytest.fixture(scope="function")
def db_session_test() -> Iterator[Session]:
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session_test: Session) -> Iterator[TestClient]:
    def override_get_db():
        try:
            yield db_session_test
        finally:
            pass 
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
def admin_auth_headers(client: TestClient, db_session_test: Session):
    admin_email = "admin_test@example.com"
    admin_password = "adminpassword"

    user_candidate, candidate_role = get_user_by_email(email=admin_email, db=db_session_test)

    actual_admin_user_for_login = None

    if user_candidate and candidate_role == "admin":
        actual_admin_user_for_login = user_candidate
    if not actual_admin_user_for_login:
        _existing_specific_admin = db_session_test.query(Admin).filter(Admin.email == admin_email).first()
        if _existing_specific_admin:
            actual_admin_user_for_login = _existing_specific_admin
        else:
            hashed_password = get_password_hash(admin_password)
            new_admin = Admin(
                email=admin_email,
                hashed_password=hashed_password,
                full_name="Admin Test User"
            )
            db_session_test.add(new_admin)
            db_session_test.commit()
            db_session_test.refresh(new_admin)
            actual_admin_user_for_login = new_admin
    
    login_data = {"username": admin_email, "password": admin_password}
    response = client.post("/api/v1/auth/token", data=login_data)
    
    if response.status_code != 200:
        print(f"DEBUG FIXTURE: Login falló. Status: {response.status_code}, Response: {response.json()}")

    assert response.status_code == 200, f"No se pudo loguear como admin para obtener el token: {response.json()}"
    
    tokens = response.json()
    access_token = tokens["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}