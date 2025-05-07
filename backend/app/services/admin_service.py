from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from ..models.models import Admin, Subject, Teacher, Student
from ..models.schemas import (
    AdminCreate, AdminOut,
    SubjectCreate, SubjectOut,
    TeacherCreate, StudentCreate
)
from app.core.security import get_password_hash

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def create_admin(self, admin: AdminCreate) -> AdminOut:
        """Crear un nuevo administrador"""
        db_admin = Admin(
            email=admin.email,
            full_name=admin.full_name,
            hashed_password=get_password_hash(admin.password)
        )
        self.db.add(db_admin)
        self.db.commit()
        self.db.refresh(db_admin)
        return db_admin

    def get_admin_by_email(self, email: str) -> Optional[Admin]:
        """Obtener un administrador por su email"""
        return self.db.query(Admin).filter(Admin.email == email).first()

    def create_subject(self, subject: SubjectCreate) -> SubjectOut:
        """Crear una nueva asignatura"""
        db_subject = Subject(
            name=subject.name,
            description=subject.description,
            course_year=subject.course_year,
            teacher_id=subject.teacher_id
        )
        self.db.add(db_subject)
        self.db.commit()
        self.db.refresh(db_subject)
        return db_subject

    def get_all_subjects(self) -> List[SubjectOut]:
        """Obtener todas las asignaturas"""
        return self.db.query(Subject).all()

    def create_teacher(self, teacher: TeacherCreate) -> Teacher:
        """Crear un nuevo profesor"""
        db_teacher = Teacher(
            email=teacher.email,
            full_name=teacher.full_name,
            hashed_password=get_password_hash(teacher.password)
        )
        self.db.add(db_teacher)
        self.db.commit()
        self.db.refresh(db_teacher)
        return db_teacher

    def create_student(self, student: StudentCreate) -> Student:
        """Crear un nuevo estudiante"""
        db_student = Student(
            email=student.email,
            full_name=student.full_name,
            hashed_password=get_password_hash(student.password)
        )
        self.db.add(db_student)
        self.db.commit()
        self.db.refresh(db_student)
        return db_student

    def get_all_teachers(self) -> List[Teacher]:
        """Obtener todos los profesores"""
        return self.db.query(Teacher).all()

    def get_all_students(self) -> List[Student]:
        """Obtener todos los estudiantes"""
        return self.db.query(Student).all()