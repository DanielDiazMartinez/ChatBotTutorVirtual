from fastapi import APIRouter
from .alumno_routes import router as alumno_router
from .teacher_routes import router as teacher_router

api_router = APIRouter()

api_router.include_router(alumno_router, prefix="/alumnos", tags=["Alumnos"])
api_router.include_router(teacher_router, prefix="/teachers", tags=["Profesores"])
