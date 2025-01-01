import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Cargar las variables de entorno desde .env
load_dotenv()

# Configuración de Alembic
config = context.config

# Reemplazar sqlalchemy.url con la URL de la base de datos desde .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Configurar logging
fileConfig(config.config_file_name)

# Metadata de los modelos de SQLAlchemy
from db_config import Base  # Ruta donde está declarado Base
from models.user_models import Usuario
from models.content_models import Temario
target_metadata = Base.metadata

# Definir conexión
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
