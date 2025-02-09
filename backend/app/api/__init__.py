from fastapi import APIRouter
from .student_routes import router as alumno_router
from .teacher_routes import router as teacher_router

api_router = APIRouter()

api_router.include_router(alumno_router, prefix="/student", tags=["Student"])
api_router.include_router(teacher_router, prefix="/teacher", tags=["Profesores"])
