from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.auth import get_current_active_admin
from app.core.database import get_db

from app.models.models import Admin
from app.models.schemas import (
    AdminCreate, AdminOut,
    SubjectCreate, SubjectOut,
    TeacherCreate, TeacherOut,
    StudentCreate, StudentOut
)
from app.services.admin_service import AdminService
from app.services.subject_service import create_subject

router = APIRouter()

@router.post("/register", response_model=AdminOut)
def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo administrador"""
    admin_service = AdminService(db)
    if admin_service.get_admin_by_email(admin.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return admin_service.create_admin(admin)

@router.post("/subjects", response_model=SubjectOut)
def create_subject_route(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Crear una nueva asignatura (solo administradores)"""

    return create_subject(db=db,subject=subject)

@router.get("/subjects", response_model=List[SubjectOut])
def get_subjects(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Obtener todas las asignaturas (solo administradores)"""
    admin_service = AdminService(db)
    return admin_service.get_all_subjects()

@router.post("/teachers", response_model=TeacherOut)
def create_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Crear un nuevo profesor (solo administradores)"""
    admin_service = AdminService(db)
    return admin_service.create_teacher(teacher)

@router.post("/students", response_model=StudentOut)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Crear un nuevo estudiante (solo administradores)"""
    admin_service = AdminService(db)
    return admin_service.create_student(student)

@router.get("/teachers", response_model=List[TeacherOut])
def get_teachers(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Obtener todos los profesores (solo administradores)"""
    admin_service = AdminService(db)
    return admin_service.get_all_teachers()

@router.get("/students", response_model=List[StudentOut])
def get_students(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Obtener todos los estudiantes (solo administradores)"""
    admin_service = AdminService(db)
    return admin_service.get_all_students()