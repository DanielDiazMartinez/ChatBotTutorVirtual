# tests/conftest.py (CORREGIDO)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker,Session
# Remueve StaticPool si no es específicamente necesario para tu setup de PostgreSQL;
# SQLAlchemy usará su pool por defecto que es generalmente QueuePool para PostgreSQL.
# from sqlalchemy.pool import StaticPool # QUITAR O REVISAR SI REALMENTE LO NECESITAS

from app.core.security import get_password_hash
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.models import Admin
from app.services.user_service import get_user_by_email

SQLALCHEMY_DATABASE_URL_TEST = settings.TEST_DATABASE_URL


engine_test = create_engine(SQLALCHEMY_DATABASE_URL_TEST)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Fixture para crear las tablas y la extensión ANTES de la sesión de tests
# y borrarlas DESPUÉS.
@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown(): # Ya no necesita engine_test como argumento si engine_test es global
    # Conéctate para habilitar la extensión en la base de datos de prueba
    with engine_test.connect() as connection:
        try:
            # Habilita la extensión 'vector' si no existe ya
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            connection.commit() # Importante hacer commit para DDL como CREATE EXTENSION
            print("DEBUG: Extensión 'vector' creada/verificada.")
        except Exception as e:
            print(f"DEBUG: Error al intentar crear la extensión 'vector': {e}")
            # Podrías querer relanzar el error si es crítico y no es "ya existe"
            # Por ahora, si falla, create_all probablemente fallará después con el mismo error de tipo.

    # Crear todas las tablas (después de asegurar que la extensión existe)
    try:
        # Asegúrate de que todos tus modelos (Admin, Teacher, Student, Document, DocumentChunk, etc.)
        # estén importados y usen la 'Base' de app.core.database para que sean detectados aquí.
        # Si el problema de 'Base' no se solucionó, este create_all seguirá sin crear todas las tablas.
        print("DEBUG: Intentando Base.metadata.create_all()")
        Base.metadata.create_all(bind=engine_test)
        print("DEBUG: Base.metadata.create_all() ejecutado.")
    except Exception as e:
        print(f"DEBUG: Error durante Base.metadata.create_all: {e}")
        raise # Relanza la excepción para que el test falle claramente

    yield # Los tests se ejecutan aquí

    # Borrar todas las tablas después de que todos los tests de la sesión hayan terminado
    print("DEBUG: Intentando Base.metadata.drop_all()")
    Base.metadata.drop_all(bind=engine_test)
    print("DEBUG: Base.metadata.drop_all() ejecutado.")


# Fixture para la sesión de base de datos de prueba por función (test individual)
@pytest.fixture(scope="function")
def db_session_test() -> pytest.Session: # Añadido type hint para claridad
    # La conexión se establece aquí, hereda la configuración del engine_test
    # que ya apunta a la base de datos con la extensión habilitada.
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Fixture para el cliente de API (ya la tenías)
@pytest.fixture(scope="function")
def client(db_session_test: Session) -> TestClient: # Añadido type hint para claridad
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

    # 1. Busca un usuario Admin existente
    user_candidate, candidate_role = get_user_by_email(email=admin_email, db=db_session_test)

    actual_admin_user_for_login = None # Esta variable contendrá el admin que se usará para el login

    if user_candidate and candidate_role == "admin":
        # Se encontró un admin con ese email
        actual_admin_user_for_login = user_candidate
        # Opcional: Podrías verificar/actualizar la contraseña aquí si es necesario
        # from app.core.security import verify_password
        # if not verify_password(admin_password, actual_admin_user_for_login.hashed_password):
        #     actual_admin_user_for_login.hashed_password = get_password_hash(admin_password)
        #     db_session_test.add(actual_admin_user_for_login)
        #     db_session_test.commit()
        #     db_session_test.refresh(actual_admin_user_for_login)
        
    if not actual_admin_user_for_login:
        # Si no se encontró un admin (o si el email correspondía a otro rol),
        # creamos nuestro usuario admin de prueba.
        # Primero, comprobamos si ya existe específicamente en la tabla Admin para evitar duplicados
        # si la lógica de get_user_by_email no lo devolvió por alguna razón o si se quiere asegurar.
        _existing_specific_admin = db_session_test.query(Admin).filter(Admin.email == admin_email).first()
        if _existing_specific_admin:
            actual_admin_user_for_login = _existing_specific_admin
            # (Aquí también podrías actualizar la contraseña si es necesario)
        else:
            # Crear un nuevo Admin porque no existe
            hashed_password = get_password_hash(admin_password)
            new_admin = Admin( # <--- USA db_models.Admin
                email=admin_email,
                hashed_password=hashed_password,
                full_name="Admin Test User"
                # NO incluyas 'role' ni 'is_active'
            )
            db_session_test.add(new_admin)
            db_session_test.commit()
            db_session_test.refresh(new_admin)
            actual_admin_user_for_login = new_admin
    
    # 2. Realiza una petición de login para obtener el token
    login_data = {"username": admin_email, "password": admin_password}
    response = client.post("/api/v1/auth/token", data=login_data)
    
    if response.status_code != 200:
        print(f"DEBUG FIXTURE: Login falló. Status: {response.status_code}, Response: {response.json()}")
        # Añade más información de depuración si es necesario
        # print(f"DEBUG FIXTURE: Intentando loguear con email='{admin_email}', password='{admin_password}'")
        # if actual_admin_user_for_login:
        #     print(f"DEBUG FIXTURE: Admin en BD: email='{actual_admin_user_for_login.email}', "
        #           f"tiene hashed_password='{actual_admin_user_for_login.hashed_password is not None}'")
        # else:
        #     print("DEBUG FIXTURE: Usuario admin no encontrado/creado en BD antes del login.")

    assert response.status_code == 200, f"No se pudo loguear como admin para obtener el token: {response.json()}"
    
    tokens = response.json()
    access_token = tokens["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}