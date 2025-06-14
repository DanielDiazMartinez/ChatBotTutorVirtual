# TutorIA 🤖

Un sistema avanzado de tutoría virtual basado en Inteligencia Artificial que conecta profesores y estudiantes a través de un chatbot inteligente.

## 📋 Descripción del Proyecto

TutorIA es una plataforma educativa integral que permite a los profesores gestionar asignaturas y cargar materiales de estudio, mientras que los estudiantes pueden interactuar con un chatbot especializado que responde preguntas basadas en esos contenidos. El sistema utiliza procesamiento de lenguaje natural y búsqueda semántica vectorial para proporcionar respuestas precisas y contextualizadas.

## 🛠️ Stack Tecnológico

### Backend
- **Framework principal**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Migraciones**: Alembic
- **Autenticación**: JWT con interceptores automáticos
- **Procesamiento LLM**: Google AI API con análisis multimodal
- **Vectorización**: pgVector con embeddings de 1024 dimensiones
- **Logging**: Sistema avanzado para análisis de contextos y uso
- **Análisis de datos**: Servicios de IA para análisis estudiantil

### Base de datos
- **Motor principal**: PostgreSQL
- **Búsqueda vectorial**: pgvector (índices vectoriales optimizados)
- **Estructura**: 8+ modelos con relaciones complejas

### Frontend
- **Framework**: Angular 17+ (standalone components, signals)
- **Estilos**: SCSS personalizado con variables globales
- **Componentes UI**: Material Design adaptado
- **Estado**: Servicios reactivos con RxJS
- **Modales**: Sistema de modales reutilizables
- **Chat**: Interfaz moderna con soporte multimedia

### Infraestructura
- **Contenedores**: Docker y Docker Compose
- **Almacenamiento**: Volúmenes Docker para persistencia de archivos
- **Archivos**: Sistema de gestión de imágenes y documentos

## 🏗️ Arquitectura del Proyecto

```
TutorIA/
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

- **User**: Base para todos los tipos de usuarios con autenticación JWT
- **Subject**: Asignaturas con relaciones profesor-estudiante y resúmenes
- **Topic**: Temas organizados por asignatura para estructurar contenidos
- **Document**: Materiales de estudio con metadatos y resúmenes automáticos
- **DocumentChunk**: Fragmentos de documentos vectorizados para búsqueda semántica
- **Conversation**: Hilos de chat entre estudiantes y el sistema con contexto
- **Message**: Mensajes individuales con soporte para texto e imágenes
- **Image**: Gestión de archivos de imagen adjuntos en conversaciones

## 🚀 Cómo Ejecutar el Proyecto

### Requisitos Previos

- Docker y Docker Compose
- Git

### Instalación y Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/Tutor.IA.git
   cd TutorIA
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

### 🎓 Gestión Académica
- **Gestión completa de asignaturas** con relaciones profesor-estudiante
- **Sistema de temas (topics)** para organizar contenidos por asignatura
- **Carga y procesamiento** de documentos PDF con vectorización automática
- **Análisis de participación estudiantil** con IA para identificar deficiencias
- **Resúmenes automáticos** de asignaturas y documentos

### 🤖 Sistema de Chat Inteligente
- **Chat multimodal** con soporte para texto e imágenes
- **Prompts predefinidos** para generar exámenes, resúmenes y ejercicios
- **Búsqueda semántica vectorial** para respuestas contextualizadas
- **Historial de conversaciones** persistente y organizado
- **Modal de visualización** de imágenes adjuntas

### 👥 Gestión de Usuarios y Roles
- **Autenticación JWT** con interceptor para manejo automático de tokens
- **Sistema de roles** (admin, profesor, estudiante) con permisos específicos
- **Panel de administración** para gestión de usuarios y asignaturas
- **Dashboard para profesores** con estadísticas y métricas

### 📊 Análisis y Reportes
- **Análisis de estudiantes con IA** para detectar patrones de aprendizaje
- **Estadísticas de participación** por asignatura y período
- **Monitor de calidad de contexto** para optimizar respuestas del chatbot
- **Sistema de logs avanzado** para análisis de uso del sistema

## 💡 Implementación Técnica

### Sistema de Logs para Contextos de Google AI

El sistema incluye una funcionalidad de logging avanzada para registrar los contextos enviados a la API de Google AI:

1. Guarda automáticamente en archivos JSON el contexto completo de cada consulta, incluyendo:
   - Pregunta del usuario
   - Contexto extraído de los documentos
   - Historial de conversación
   - Prompt completo enviado a Google AI
   - Estadísticas de tokens y longitud

2. Organiza los logs por fecha para facilitar su análisis

3. Incluye una herramienta de análisis (`analyze_google_ai_logs.py`) para extraer estadísticas y visualizar patrones de uso.

Para analizar los logs, ejecuta:
```bash
python backend/app/utils/analyze_google_ai_logs.py
```

Para ver opciones adicionales:
```bash
python backend/app/utils/analyze_google_ai_logs.py --help
```

### Sistema de Chat Multimodal

**Funcionalidades avanzadas del chat:**

1. **Soporte para imágenes**: Los usuarios pueden adjuntar imágenes que se procesan y analizan por el LLM
2. **Prompts predefinidos**: Menú de templates para generar contenido específico (exámenes, resúmenes, ejercicios)
3. **Modal de visualización**: Sistema para ver imágenes adjuntas en tamaño completo
4. **Interceptor de autenticación**: Manejo automático de tokens JWT con renovación transparente

### Análisis de Estudiantes con IA

**Sistema de análisis avanzado:**

1. **Detección de patrones**: Identifica deficiencias comunes en el aprendizaje
2. **Análisis contextual**: Relaciona preguntas con documentos y temas específicos
3. **Reportes personalizados**: Genera recomendaciones específicas por asignatura
4. **Estadísticas de participación**: Métricas detalladas de actividad estudiantil

### Gestión de Temas y Documentos

**Organización estructurada:**

1. **Jerarquía por temas**: Los documentos se organizan bajo temas específicos
2. **Resúmenes automáticos**: Generación de resúmenes para asignaturas y documentos
3. **Modal de subida**: Interfaz moderna para cargar documentos con validación
4. **Búsqueda semántica**: Vectorización avanzada para recuperación de contexto

### Búsqueda Vectorial

El sistema utiliza embeddings vectoriales para:

1. Convertir fragmentos de texto en vectores de alta dimensionalidad
2. Almacenar estos vectores de manera eficiente en PostgreSQL con pgvector
3. Realizar búsquedas por similitud semántica utilizando distancia coseno
4. Encontrar el contenido más relevante contextualmente a cada pregunta

### Flujo de una Consulta

1. El estudiante realiza una pregunta en el chat (con texto y/o imagen)
2. La pregunta se vectoriza y se buscan fragmentos relevantes en la base de datos
3. Los fragmentos recuperados proporcionan contexto a un LLM
4. El modelo genera una respuesta precisa basada en los documentos de la asignatura
5. La interacción se guarda en el historial de conversaciones con metadatos completos

## 🚀 Nuevas Funcionalidades Destacadas

### 🖼️ **Chat Multimodal con Imágenes**
- Soporte completo para adjuntar y procesar imágenes en conversaciones
- Modal de visualización de imágenes en pantalla completa
- Procesamiento de imágenes por Google AI para análisis contextual
- Sistema de almacenamiento seguro con control de acceso por roles

### 📝 **Prompts Predefinidos Inteligentes**
- Menú desplegable con templates para casos de uso común:
  - Generación de exámenes completos (opción múltiple, verdadero/falso, desarrollo)
  - Creación de resúmenes estructurados
  - Ejercicios de práctica con soluciones
  - Mapas conceptuales en formato texto
  - Casos de estudio específicos
- Interfaz moderna con iconos y previsualizaciones

### 🔒 **Sistema de Autenticación Avanzado**
- Interceptor HTTP automático para manejo de tokens JWT
- Renovación transparente de sesiones expiradas
- Redirección automática al login cuando es necesario
- Manejo de errores de autenticación con feedback al usuario

### 📊 **Análisis de Estudiantes con IA**
- **Detección automática de deficiencias** en el aprendizaje por asignatura
- **Análisis de patrones** de preguntas y participación estudiantil
- **Reportes personalizados** con recomendaciones específicas
- **Estadísticas detalladas**: tasa de participación, estudiantes más activos
- **Configuración flexible**: períodos de análisis y criterios de participación

### 🏷️ **Sistema de Temas (Topics)**
- Organización jerárquica de documentos por temas dentro de cada asignatura
- CRUD completo para gestión de temas por profesores
- Vinculación automática de documentos a temas específicos
- Estadísticas de documentos por tema

### 📋 **Gestión Avanzada de Documentos**
- **Modal moderno de subida** con drag & drop
- **Validación automática** de tipos y tamaños de archivo
- **Organización por temas** y asignaturas
- **Resúmenes automáticos** generados por IA
- **Control de acceso** basado en roles de usuario

### 💬 **Mejoras en el Sistema de Chat**
- **Barra lateral de conversaciones** con historial completo
- **Filtrado por asignatura** para organizar conversaciones
- **Indicadores visuales** para imágenes adjuntas
- **Scroll automático** optimizado para mejor UX
- **Estados de carga** y feedback visual mejorado

### 📈 **Dashboard para Profesores**
- **Estadísticas en tiempo real** de estudiantes y documentos
- **Mensajes recientes** de todas las asignaturas
- **Navegación rápida** a gestión de asignaturas
- **Métricas de participación** estudiantil

### 🛠️ **Herramientas de Monitoreo**
- **Monitor de calidad de contexto** para optimizar respuestas del chatbot
- **Análisis de logs** con estadísticas detalladas de uso
- **Recomendaciones automáticas** para mejorar el rendimiento del sistema

### 🎨 **Mejoras en la Interfaz**
- **Componentes standalone** de Angular 17+ para mejor performance
- **Sistema de modales** reutilizable y accesible
- **Estilos SCSS** organizados con variables globales
- **Responsive design** optimizado para dispositivos móviles
- **Feedback visual** mejorado en todas las interacciones

## 👨‍💻 Desarrollo y Contribuciones

Este proyecto forma parte de mi portfolio profesional, demostrando habilidades avanzadas en:

- **Desarrollo fullstack moderno** con Python (FastAPI) y Angular 17+
- **Arquitectura de monolitica en capas** con separación clara de responsabilidades
- **Integración de IA multimodal** para procesamiento de texto e imágenes
- **Diseño de bases de datos** relacionales complejas con optimizaciones vectoriales
- **Implementación de autenticación** y autorización robusta con JWT
- **Testing e integración continua** con cobertura completa
- **Documentación técnica** y API comprehensiva
- **UI/UX design** con interfaces modernas y accesibles
- **Gestión de estado** compleja en aplicaciones SPA
- **Optimización de rendimiento** tanto en frontend como backend

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 📬 Contacto

Para consultas o sugerencias sobre este proyecto, puedes contactarme en:

- Email: diazmartinezdaniel30@gmail.com
- LinkedIn: www.linkedin.com/in/daniel-diaz-martinez
- GitHub: https://github.com/DanielDiazMartinez