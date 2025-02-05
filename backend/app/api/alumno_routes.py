from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import registrar_student
from app.models.schemas import StudentCreate
router = APIRouter()


endpoint = "/student/"

@router.post(f"{endpoint}register")
def teacher_register(student: StudentCreate , db: Session = Depends(get_db)):
    return registrar_student(student, db)
    