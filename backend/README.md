# ChatBot Tutor Virtual

Sistema de tutoría virtual basado en IA que permite a los alumnos hacer preguntas sobre documentos y mantener conversaciones contextuales.

## Estructura del Proyecto

```
📦 backend/
│── 📂 app/                         # Directorio principal de la aplicación
│   ├── 📂 api/                     # Controladores de las rutas
│   │   ├── chat_routes.py         # Endpoints para chatbot y conversaciones
│   │   ├── document_routes.py     # Endpoints para gestión de documentos
│   │   ├── auth_routes.py         # Autenticación (Login/Register)
│   │   ├── user_routes.py         # Gestión de usuarios
│   │   ├── __init__.py
│   │
│   ├── 📂 core/                    # Configuraciones de la aplicación
│   │   ├── config.py              # Configuración global
│   │   ├── database.py            # Conexión con PostgreSQL
│   │   ├── pinecone.py           # Conexión con Pinecone
│   │   ├── security.py           # Seguridad y autenticación
│   │   ├── __init__.py
│   │
│   ├── 📂 models/                  # Modelos SQLAlchemy
│   │   ├── usuario_model.py
│   │   ├── alumno_model.py
│   │   ├── profesor_model.py
│   │   ├── documento_model.py
│   │   ├── pregunta_model.py
│   │   ├── conversacion_model.py
│   │   ├── mensaje_model.py
│   │   ├── __init__.py
│   │
│   ├── 📂 schemas/                 # Esquemas Pydantic
│   │   ├── usuario_schema.py
│   │   ├── documento_schema.py
│   │   ├── pregunta_schema.py
│   │   ├── conversacion_schema.py
│   │   ├── __init__.py
│   │
│   ├── 📂 services/               # Lógica de negocio
│   │   ├── document_service.py    # Procesamiento de documentos
│   │   ├── chatbot_service.py     # Lógica del chatbot
│   │   ├── user_service.py        # Gestión de usuarios
│   │   ├── pinecone_service.py    # Gestión de embeddings
│   │   ├── __init__.py
│   │
│   ├── main.py                    # Punto de entrada de la aplicación

## Configuración del Entorno

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
Crear un archivo .env en la raíz del proyecto con las siguientes variables:
```
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=tutor_virtual
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
PINECONE_INDEX=your_pinecone_index
GROQ_API_KEY=your_groq_key
SECRET_KEY=your_secret_key
```

4. Iniciar la aplicación:
```bash
uvicorn app.main:app --reload
```

## Características Principales

- Autenticación y autorización de usuarios (alumnos y profesores)
- Gestión de documentos educativos
- Sistema de preguntas y respuestas basado en IA
- Conversaciones contextuales
- Integración con Pinecone para búsqueda semántica
- Integración con Groq para generación de respuestas

## API Endpoints

### Autenticación
- POST /auth/login - Iniciar sesión
- POST /auth/register - Registrar nuevo usuario

### Chat
- POST /chat/preguntar - Hacer una pregunta sobre un documento
- POST /chat/conversaciones - Crear una nueva conversación
- GET /chat/conversaciones - Listar conversaciones del usuario
- POST /chat/conversaciones/{id}/mensajes - Enviar mensaje en una conversación
- GET /chat/conversaciones/{id}/mensajes - Obtener mensajes de una conversación

### Documentos
- POST /documents/upload - Subir nuevo documento
- GET /documents - Listar documentos disponibles
- DELETE /documents/{id} - Eliminar documento

### Usuarios
- GET /users/me - Obtener información del usuario actual
- GET /users - Listar usuarios (admin)
