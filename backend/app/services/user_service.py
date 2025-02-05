from sqlalchemy.orm import Session
from app.models.models import Teacher, Student
from app.models.schemas import  TeacherCreate, StudentCreate
from fastapi import HTTPException

def registrar_profesor(profesor: TeacherCreate, db: Session):
    """
    Registra un profesor en la base de datos.
    """

    # Verificar si ya existe un profesor con el mismo email
    existing_teacher = db.query(Teacher).filter(Teacher.email == profesor.email).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="El profesor ya está registrado.")

    # Se crea el profesor en la base de datos
    profesor_db = Teacher(**profesor.model_dump())
    db.add(profesor_db)
    db.commit()
    db.refresh(profesor_db)
    return profesor_db

def registrar_alumno(student: StudentCreate, db: Session):
    """
    Registra un alumno en la base de datos.
    """

    # Verificar si ya existe un alumno con el mismo email
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="El alumno ya está registrado.")

    # Se crea el alumno en la base de datos
    student_db = Student(**student.model_dump())
    db.add(student_db)
    db.commit()
    db.refresh(student_db)
    return student_db
