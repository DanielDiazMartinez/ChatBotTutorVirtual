#!/bin/bash
set -e

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL no está disponible aún - esperando..."
  sleep 1
done
echo "PostgreSQL listo!"

# Crear extensión pgvector - IMPORTANTE: Esto debe ejecutarse ANTES de las migraciones
echo "Creando extensión pgvector..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'CREATE EXTENSION IF NOT EXISTS vector;'
echo "Extensión pgvector creada o ya existente"

# Ejecutar migraciones DESPUÉS de crear la extensión
echo "Ejecutando migraciones de Alembic..."
alembic upgrade head

# Crear directorios de logs y asignar permisos
echo "Configurando directorios de logs..."
mkdir -p /app/logs/chat/groq_contexts
chmod -R 777 /app/logs

# Iniciar la aplicación
echo "Iniciando aplicación..."
exec "$@"