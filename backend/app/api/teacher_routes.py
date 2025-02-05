from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.user_service import registrar_teacher, get_students, get_student_by_id, get_teachers, get_teacher_by_id
from ..models.schemas import TeacherCreate, StudentOut, TeacherOut
from typing import List
from fastapi import HTTPException

router = APIRouter()

@router.post("/teacher/register")
def teacher_register(teacher: TeacherCreate , db: Session = Depends(get_db)):
    return registrar_teacher(teacher, db)

@router.get("/teacher/list/students",response_model=List[StudentOut])
def list_students(db: Session = Depends(get_db)):

    students = get_students(db)

    if not students:
        raise HTTPException(status_code=404, detail="No hay estudiantes registrados.")
    
    return students

@router.get("/teacher/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = get_student_by_id(student_id, db)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    return student

@router.get("/teachers", response_model=List[TeacherOut])
def list_teachers(db: Session = Depends(get_db)):
    teachers = get_teachers(db)

    if not teachers:
        raise HTTPException(status_code=404, detail="No hay profesores registrados.")
    
    return teachers

@router.get("/teacher/{teacher_id}", response_model=TeacherOut)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = get_teacher_by_id(teacher_id, db)
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")
    return teacher

@router.delete("/teacher/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    return delete_teacher(teacher_id, db)

@router.put("/teacher/{teacher_id}")
def update_teacher(teacher_id: int, db: Session = Depends(get_db)):
    return update_teacher(teacher_id, db)
