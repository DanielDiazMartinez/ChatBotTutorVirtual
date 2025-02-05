from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.user_service import registrar_profesor
from ..models.schemas import TeacherCreate, StudentCreate
from ..models.models import Student
router = APIRouter()


endpoint = "/teacher/"

@router.post(f"{endpoint}register")
def teacher_register(profesor: TeacherCreate , db: Session = Depends(get_db)):
    return registrar_profesor(profesor, db)

@router.get(f"{endpoint}list/students")
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()
    