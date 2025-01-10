from fastapi import FastAPI
from routes.profesor_routes import router as profesor_router
from routes.alumnos_routes import router as alumno_router
from routes.user_routes import router as user_router

app = FastAPI()

# Registrar rutas por rol
app.include_router(profesor_router, prefix="/profesor", tags=["Profesor"])
app.include_router(alumno_router, prefix="/alumno", tags=["Alumno"])
app.include_router(user_router, prefix="/usuario", tags=["Usuario"])

