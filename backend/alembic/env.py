import os
from sqlalchemy import engine_from_config, pool, create_engine
from logging.config import fileConfig
from alembic import context
from app.core.config import settings
# Cargar configuración de logging
fileConfig(context.config.config_file_name)

# Obtener la URL de la base de datos desde una variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)


# Importa los modelos para que Alembic pueda detectar cambios automáticamente
from app.models.models import Base  # Asegúrate de que `Base` está correctamente importado desde tu app

target_metadata = Base.metadata

def run_migrations_offline():
    """Corre las migraciones en modo 'offline' (sin conectarse a la BD)."""
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Corre las migraciones en modo 'online' (conectándose a la BD)."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
