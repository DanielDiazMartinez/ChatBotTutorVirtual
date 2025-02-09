from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import registrar_student
from app.models.schemas import StudentCreate

router = router = APIRouter(prefix="/student", tags=["Student"])

@router.post("/register")
def teacher_register(student: StudentCreate , db: Session = Depends(get_db)):
    return registrar_student(student, db)

@router.get("/pregunta")
def pregunta():
    return {"pregunta": "¿Cuál es la capital de Francia?"}
