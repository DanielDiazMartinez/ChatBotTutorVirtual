# ChatBotTutorVirtual 🤖

Un sistema avanzado de tutoría virtual basado en Inteligencia Artificial que conecta profesores y estudiantes a través de un chatbot inteligente.

## 📋 Descripción del Proyecto

ChatBotTutorVirtual es una plataforma educativa integral que permite a los profesores gestionar asignaturas y cargar materiales de estudio, mientras que los estudiantes pueden interactuar con un chatbot especializado que responde preguntas basadas en esos contenidos. El sistema utiliza procesamiento de lenguaje natural y búsqueda semántica vectorial para proporcionar respuestas precisas y contextualizadas.

## 🛠️ Stack Tecnológico

### Backend
- **Framework principal**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Migraciones**: Alembic
- **Autenticación**: JWT
- **Procesamiento LLM**: Groq API
- **Vectorización**: PineconeDB

### Base de datos
- **Motor principal**: PostgreSQL
- **Búsqueda vectorial**: pgvector (índices vectoriales para búsqueda semántica)

### Frontend
- **Framework**: Angular 17+ (standalone components)
- **Estilos**: SCSS personalizado
- **Componentes UI**: Material Design

### Infraestructura
- **Contenedores**: Docker y Docker Compose
- **Almacenamiento**: Volúmenes Docker para persistencia

## 🏗️ Arquitectura del Proyecto

```
ChatBotTutorVirtual/
├── backend/                # API y lógica de servidor
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuración y utilidades
│   │   ├── models/         # Modelos de datos y schemas
│   │   └── services/       # Lógica de negocio
│   ├── alembic/            # Migraciones de base de datos
│   └── tests/              # Tests unitarios e integración
├── frontend/              # Aplicación Angular
│   ├── src/
│   │   ├── app/           # Componentes y servicios
│   │   └── styles/        # Estilos SCSS
│   └── public/            # Assets estáticos
└── docker-compose.yml     # Configuración de servicios
```


## 📊 Modelos de Datos

El sistema está estructurado alrededor de estos modelos principales:

- **User**: Base para todos los tipos de usuarios con autenticación
- **Subject**: Asignaturas con relaciones a profesores y estudiantes
- **Document**: Materiales de estudio con metadatos
- **DocumentChunk**: Fragmentos de documentos vectorizados
- **Conversation**: Hilos de chat entre estudiantes y el sistema
- **Message**: Mensajes individuales con su contexto

## 🚀 Cómo Ejecutar el Proyecto

### Requisitos Previos

- Docker y Docker Compose
- Git

### Instalación y Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/ChatBotTutorVirtual.git
   cd ChatBotTutorVirtual
   ```

2. **Configurar variables de entorno**
   ```bash
   cp backend/.env.example backend/.env
   # Editar .env con tus credenciales y configuración
   ```

3. **Iniciar los servicios**
   ```bash
   docker-compose up -d
   ```

4. **Acceder a las interfaces**
   - API y documentación: http://localhost:8000/docs
   - Aplicación web: http://localhost:4200



## 🔍 Funcionalidades Destacadas

- **Gestión de asignaturas** con relaciones profesor-estudiante
- **Carga y procesamiento** de documentos PDF, DOCX, etc.
- **Vectorización automática** de contenidos para búsqueda semántica
- **Autenticación y autorización** basada en roles (admin, profesor, estudiante)
- **Procesamiento de lenguaje natural** para responder consultas complejas
- **Historial de conversaciones** persistente con contexto de preguntas anteriores
- **Interfaz administrativa** para profesores y gestores del sistema

## 💡 Implementación Técnica

### Búsqueda Vectorial

El sistema utiliza embeddings vectoriales para:

1. Convertir fragmentos de texto en vectores de alta dimensionalidad
2. Almacenar estos vectores de manera eficiente en PostgreSQL con pgvector
3. Realizar búsquedas por similitud semántica utilizando distancia coseno
4. Encontrar el contenido más relevante contextualmente a cada pregunta

### Flujo de una Consulta

1. El estudiante realiza una pregunta en el chat
2. La pregunta se vectoriza y se buscan fragmentos relevantes en la base de datos
3. Los fragmentos recuperados proporcionan contexto a un LLM
4. El modelo genera una respuesta precisa basada en los documentos de la asignatura
5. La interacción se guarda en el historial de conversaciones

## 👨‍💻 Desarrollo y Contribuciones

Este proyecto forma parte de mi portfolio profesional, demostrando habilidades en:

- Desarrollo fullstack con Python (FastAPI) y Angular
- Diseño e implementación de bases de datos relacionales
- Integración de modelos de IA y procesamiento de lenguaje natural
- Arquitectura de sistemas distribuidos con Docker
- Testing y documentación de APIs

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 📬 Contacto

Para consultas o sugerencias sobre este proyecto, puedes contactarme en:

- Email: diazmartinezdaniel30@gmail.com
- LinkedIn: [Tu perfil de LinkedIn](www.linkedin.com/in/daniel-diaz-martinez)
- GitHub: [Tu perfil de GitHub](https://github.com/DanielDiazMartinez)