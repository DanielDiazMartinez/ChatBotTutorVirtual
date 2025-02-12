# 📚 ChatBot Tutor Virtual 🤖🎓

Un sistema de tutoría virtual basado en IA que permite a los estudiantes hacer preguntas sobre documentos y mantener conversaciones contextuales con un chatbot inteligente.

## 🚀 Características Principales

✅ **Autenticación y autorización** para profesores y alumnos  
✅ **Gestión de documentos** educativos en formato PDF  
✅ **Sistema de preguntas y respuestas** con IA  
✅ **Conversaciones contextuales** con un chatbot  
✅ **Integración con Pinecone** para búsqueda semántica eficiente  
✅ **Integración con Groq** para generación de respuestas inteligentes  

---

## 🏗️ **Estructura del Proyecto**

```
📦 backend/
│── 📂 app/                         # Código principal del backend
│   ├── 📂 api/                     # Definición de endpoints
│   │   ├── student_routes.py       # Rutas de estudiantes
│   │   ├── teacher_routes.py       # Rutas de profesores
│   │   ├── __init__.py
│   │
│   ├── 📂 core/                    # Configuraciones de la aplicación
│   │   ├── config.py               # Configuración global
│   │   ├── database.py             # Conexión con PostgreSQL
│   │   ├── pinecone.py             # Configuración de Pinecone
│   │   ├── security.py             # Seguridad y autenticación
│   │   ├── __init__.py
│   │
│   ├── 📂 models/                  # Modelos SQLAlchemy
│   │   ├── models.py               # Modelos de BD
│   │   ├── schemas.py              # Esquemas Pydantic
│   │   ├── __init__.py
│   │
│   ├── 📂 services/                # Lógica de negocio
│   │   ├── chat_service.py         # Procesamiento de conversaciones
│   │   ├── document_service.py     # Procesamiento de documentos
│   │   ├── groq_service.py         # Integración con Groq
│   │   ├── pinecone_service.py     # Gestión de embeddings
│   │   ├── user_service.py         # Gestión de usuarios
│   │   ├── __init__.py
│   │
│   ├── 📂 utils/                   # Utilidades generales
│   │   ├── document_utils.py       # Procesamiento de documentos PDF
│   │   ├── __init__.py
│   │
│   ├── 📂 uploads/                 # Carpeta donde se almacenan los PDFs subidos
│   │   ├── (Archivos PDF)
│   │
│   ├── main.py                     # Punto de entrada del backend
│
📦 frontend/
│── 📂 src/                         # Código fuente del frontend Angular
│── 📂 public/                      # Archivos estáticos
│── angular.json                    # Configuración de Angular
│── package.json                     # Dependencias del frontend
│
📜 .env                              # Variables de entorno
📜 requirements.txt                   # Dependencias de Python
📜 Dockerfile                         # Configuración de Docker
📜 docker-compose.yml                 # Configuración para Docker Compose
📜 README.md                          # Documentación del proyecto
```

---

## 🛠️ **Instalación y Configuración**

### **1️⃣ Requisitos previos**
Asegúrate de tener instalado en tu sistema:
- **Python 3.10+**
- **Node.js & npm**
- **PostgreSQL**
- **Docker y Docker Compose (Opcional, pero recomendado)**

---

### **2️⃣ Configuración del Backend**

#### 🔹 **1. Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/chatbot-tutor-virtual.git
cd chatbot-tutor-virtual/backend
```

#### 🔹 **2. Crear un entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

#### 🔹 **3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

#### 🔹 **4. Configurar variables de entorno**
Crea un archivo `.env` en la raíz del backend y añade:
```ini
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

#### 🔹 **5. Iniciar el backend**
```bash
uvicorn app.main:app --reload
```

---

### **3️⃣ Configuración del Frontend**
#### 🔹 **1. Instalar dependencias**
```bash
cd ../frontend
npm install
```

#### 🔹 **2. Iniciar el frontend**
```bash
ng serve --open
```

---

### **4️⃣ Opcional: Ejecutar con Docker**
```bash
docker-compose up --build
```

---

## 📡 **Endpoints de la API**

### **🔐 Autenticación**
- **POST** `/auth/login` → Iniciar sesión
- **POST** `/auth/register` → Registrar nuevo usuario

### **📄 Documentos**
- **POST** `/documents/upload` → Subir un documento PDF
- **GET** `/documents` → Listar documentos disponibles
- **DELETE** `/documents/{id}` → Eliminar documento

### **💬 Chat y Preguntas**
- **POST** `/chat/preguntar` → Hacer una pregunta sobre un documento
- **POST** `/chat/conversaciones` → Crear una nueva conversación
- **GET** `/chat/conversaciones` → Listar conversaciones del usuario
- **POST** `/chat/conversaciones/{id}/mensajes` → Enviar un mensaje
- **GET** `/chat/conversaciones/{id}/mensajes` → Obtener mensajes de una conversación

---

## ⭐ **Contribuciones**
Las contribuciones son bienvenidas. Puedes:
1. Hacer un **fork** 🍴
2. Crear una rama (`git checkout -b feature-nueva`)
3. Hacer tus cambios y commit (`git commit -m "Agregada nueva funcionalidad"`)
4. Hacer un push (`git push origin feature-nueva`)
5. Abrir un **Pull Request** 🚀

---

## 📌 **Contacto**
Si tienes dudas o sugerencias, puedes contactarme en **tu-email@ejemplo.com** 📩

