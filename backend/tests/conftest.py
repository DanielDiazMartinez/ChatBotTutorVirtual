import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker,Session

from app.core.security import get_password_hash
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.models import User
from app.models.schemas import UserCreate
from app.services.user_service import create_user, get_user_by_email
from typing import Iterator

SQLALCHEMY_DATABASE_URL_TEST = settings.TEST_DATABASE_URL

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

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

    yield

    print("DEBUG: Intentando Base.metadata.drop_all()")
    Base.metadata.drop_all(bind=engine_test)
    print("DEBUG: Base.metadata.drop_all() ejecutado.")


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
    admin_full_name = "Admin Test Fixture User"

    user_details_tuple = get_user_by_email(email=admin_email, db=db_session_test)

    if user_details_tuple is None:
        admin_user_to_create = UserCreate(
            email=admin_email,
            password=admin_password,
            full_name=admin_full_name,
            role="admin",
        )
        create_user(user=admin_user_to_create, db=db_session_test)
    login_data = {"username": admin_email, "password": admin_password}
    token_url = "api/v1/auth/token" 
    response = client.post(token_url, data=login_data)

    if response.status_code != 200:
        print(f"Error al intentar loguear al admin '{admin_email}'. Status: {response.status_code}")
        print(f"Respuesta del servidor: {response.text}")
        user_check = get_user_by_email(email=admin_email, db=db_session_test)
        if user_check:
            print(f"El usuario '{admin_email}' SÍ existe en la BD.")
        else:
            print(f"El usuario '{admin_email}' NO existe en la BD.")
        response.raise_for_status()

    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    return headers

@pytest.fixture(scope="function")
def teacher_auth_headers(client: TestClient, db_session_test: Session):
    teacher_email = "teacher_test@example.com"
    teacher_password = "teacherpassword"
    teacher_full_name = "Teacher Test User"

    user_details_tuple = get_user_by_email(email=teacher_email, db=db_session_test)

    if user_details_tuple is None:
        teacher_user_to_create = UserCreate(
            email=teacher_email,
            password=teacher_password,
            full_name=teacher_full_name,
            role="teacher"
        )
        create_user(user=teacher_user_to_create, db=db_session_test)

    login_data = {"username": teacher_email, "password": teacher_password}
    token_url = "api/v1/auth/token"
    response = client.post(token_url, data=login_data)

    if response.status_code != 200:
        print(f"Error al intentar loguear al profesor '{teacher_email}'. Status: {response.status_code}")
        print(f"Respuesta del servidor: {response.text}")
        user_check = get_user_by_email(email=teacher_email, db=db_session_test)
        if user_check:
            print(f"El usuario '{teacher_email}' SÍ existe en la BD.")
        else:
            print(f"El usuario '{teacher_email}' NO existe en la BD.")
        response.raise_for_status()

    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    return headers

@pytest.fixture(scope="function")
def student_auth_headers(client: TestClient, db_session_test: Session):
    student_email = "student_test@example.com"
    student_password = "studentpassword"
    student_full_name = "Student Test User"

    user_details_tuple = get_user_by_email(email=student_email, db=db_session_test)

    if user_details_tuple is None:
        student_user_to_create = UserCreate(
            email=student_email,
            password=student_password,
            full_name=student_full_name,
            role="student"
        )
        create_user(user=student_user_to_create, db=db_session_test)

    login_data = {"username": student_email, "password": student_password}
    token_url = "api/v1/auth/token"
    response = client.post(token_url, data=login_data)

    if response.status_code != 200:
        print(f"Error al intentar loguear al estudiante '{student_email}'. Status: {response.status_code}")
        print(f"Respuesta del servidor: {response.text}")
        user_check = get_user_by_email(email=student_email, db=db_session_test)
        if user_check:
            print(f"El usuario '{student_email}' SÍ existe en la BD.")
        else:
            print(f"El usuario '{student_email}' NO existe en la BD.")
        response.raise_for_status()

    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    return headers