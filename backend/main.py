from fastapi import FastAPI
from routes.profesor_routes import router as profesor_router
from routes.alumnos_routes import router as alumno_router
from routes.user_routes import router as user_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:4200",  # Origen del frontend Angular
    "http://127.0.0.1:4200",  # Alternativa para localhost
]

# Configurar el middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Orígenes permitidos
    allow_credentials=True,  # Permitir cookies y credenciales
    allow_methods=["*"],  # Métodos HTTP permitidos (GET, POST, etc.)
    allow_headers=["*"],  # Encabezados permitidos
)
# Registrar rutas por rol
app.include_router(profesor_router, prefix="/profesor", tags=["Profesor"])
app.include_router(alumno_router, prefix="/alumno", tags=["Alumno"])
app.include_router(user_router, prefix="/usuario", tags=["Usuario"])

