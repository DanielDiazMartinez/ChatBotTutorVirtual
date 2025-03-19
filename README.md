ChatBotTutorVirtual 🤖
Un asistente virtual educativo que permite a los profesores cargar documentos y a los estudiantes interactuar con un chatbot que responde preguntas basadas en esos documentos, utilizando procesamiento de lenguaje natural y búsqueda vectorial para proporcionar respuestas precisas.
📋 Descripción
ChatBotTutorVirtual es una aplicación que conecta profesores y estudiantes a través de un sistema de chat inteligente que analiza documentos educativos. Los profesores pueden subir materiales de estudio, mientras que los estudiantes pueden hacer preguntas sobre los contenidos y recibir respuestas contextualizadas gracias a la búsqueda vectorial con pgvector.
🛠️ Tecnologías

Backend: FastAPI, SQLAlchemy, Alembic, pgvector
Base de datos: PostgreSQL
Almacenamiento vectorial: pgvector (búsqueda semántica)
Contenedores: Docker, Docker Compose
Herramientas adicionales: pgAdmin

## 🏗️ Arquitectura

backend/
├── alembic/              # Migraciones de base de datos
├── app/
│   ├── api/              # Endpoints de la API
│   ├── core/             # Configuración central
│   └── models/           # Modelos de datos
├── Dockerfile
├── .env
└── init.sql              # Script inicial para PostgreSQL


📊 Modelos de datos
El sistema utiliza los siguientes modelos principales:

Teacher: Gestiona profesores y sus documentos
Student: Información de estudiantes
Document: Documentos subidos por profesores
DocumentChunk: Fragmentos de documentos con embeddings vectoriales
Conversation: Conversaciones entre estudiantes y el chatbot
Message: Mensajes individuales en las conversaciones

🚀 Instalación y configuración
Requisitos previos

Docker y Docker Compose
Git

Pasos para instalar

Clona el repositorio
bashCopiargit clone https://github.com/tu-usuario/ChatBotTutorVirtual.git
cd ChatBotTutorVirtual

Configura las variables de entorno
bashCopiarcp backend/.env.example backend/.env
# Edita .env con tus valores

Inicia los servicios con Docker Compose
bashCopiardocker-compose up -d

Accede a la aplicación

API: http://localhost:8000
Documentación API: http://localhost:8000/docs
pgAdmin: http://localhost:5050



📄 API Endpoints
La API proporciona los siguientes endpoints principales:

Autenticación: /api/auth/login, /api/auth/register
Profesores: /api/teachers/
Estudiantes: /api/students/
Documentos: /api/documents/
Chat: /api/chat/

💡 Características principales

Autenticación y autorización para profesores y estudiantes
Carga y procesamiento de documentos PDF
Generación automática de embeddings vectoriales
Conversaciones contextualizadas con búsqueda semántica
Interfaz administrativa para profesores

🔍 Búsqueda vectorial con pgvector
El sistema utiliza pgvector para:

Convertir fragmentos de texto en vectores de alta dimensionalidad
Almacenar estos vectores de manera eficiente en PostgreSQL
Realizar búsquedas semánticas utilizando distancia coseno
Encontrar contenido relacionado contextualmente a las preguntas

👥 Contribuir
Las contribuciones son bienvenidas. Para contribuir:

Haz fork del repositorio
Crea una nueva rama (git checkout -b feature/nueva-caracteristica)
Haz commit de tus cambios (git commit -m 'Añadir nueva característica')
Sube tu rama (git push origin feature/nueva-caracteristica)
Abre un Pull Request