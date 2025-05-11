from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_role
from app.services.user_service import get_student_by_id, get_students, get_teacher_by_id, get_teachers, registrar_student, registrar_teacher, update_teacher_service
from app.models.schemas import StudentCreate, StudentOut, TeacherCreate, TeacherOut

users_routes = APIRouter()

@users_routes.post("/register/student")
def student_register(
    student: StudentCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Registrar un nuevo estudiante (profesores y administradores)"""
    return registrar_student(student, db)

@users_routes.post("/register/teacher")
def teacher_register(
    teacher: TeacherCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Registrar un nuevo profesor (profesores y administradores)"""
    return registrar_teacher(teacher, db)

@users_routes.get("/list/students", response_model=List[StudentOut])
def list_students(
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Listar todos los estudiantes (profesores y administradores)"""
    students = get_students(db)
    if not students:
        raise HTTPException(status_code=404, detail="No hay estudiantes registrados.")
    return students

@users_routes.get("/students/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Obtener información de un estudiante (profesores, estudiantes y administradores)"""
    student = get_student_by_id(student_id, db)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    return student

@users_routes.get("/teachers", response_model=List[TeacherOut])
def list_teachers(
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Listar todos los profesores (profesores, estudiantes y administradores)"""
    teachers = get_teachers(db)
    if not teachers:
        raise HTTPException(status_code=404, detail="No hay profesores registrados.")
    return teachers

@users_routes.get("/teachers/{teacher_id}", response_model=TeacherOut)
def get_teacher(
    teacher_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Obtener información de un profesor (profesores, estudiantes y administradores)"""
    teacher = get_teacher_by_id(teacher_id, db)
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")
    return teacher

@users_routes.put("/teachers/{teacher_id}")
def update_teacher(
    teacher_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Actualizar información de un profesor (profesores y administradores)"""
    return update_teacher_service(teacher_id, db)

