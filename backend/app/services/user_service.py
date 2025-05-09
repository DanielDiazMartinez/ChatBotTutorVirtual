from sqlalchemy.orm import Session
from app.models.models import Admin, Message, Teacher, Student
from app.models.schemas import TeacherCreate, StudentCreate, TeacherUpdate
from fastapi import HTTPException 
from app.core.security import get_password_hash

def registrar_teacher(teacher: TeacherCreate, db: Session):
    """
    Registra un teacher en la base de datos.
    """
    existing_teacher = db.query(Teacher).filter(Teacher.email == teacher.email).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Email already registered")

    teacher_data = teacher.model_dump()
    teacher_data["hashed_password"] = get_password_hash(teacher_data.pop("password"))
    
    teacher_db = Teacher(**teacher_data)
    db.add(teacher_db)
    db.commit()
    db.refresh(teacher_db)
    return teacher_db

def get_teachers(db: Session):
    """
    Obtiene todos los teachers registrados.
    """
    return db.query(Teacher).all()

def get_teacher_by_id(teacher_id: int, db: Session):
    """
    Obtiene un teacher por su identificador.
    """
    return db.query(Teacher).filter(Teacher.id == teacher_id).first()

def update_teacher_service(teacher_id: int, teacherUpdate: TeacherUpdate, db: Session):
    """
    Actualiza un teacher por su identificador.
    """
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")
    
    teacher.email = teacherUpdate.email
    teacher.full_name = teacherUpdate.full_name
    teacher.hashed_password = get_password_hash(teacherUpdate.password) 
    db.commit()
    return teacher

def registrar_student(student: StudentCreate, db: Session):
    """
    Registra un alumno en la base de datos.
    """
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="El alumno ya está registrado.")

    student_data = student.model_dump()
    student_data["hashed_password"] = get_password_hash(student_data.pop("password"))
    
    student_db = Student(**student_data)
    db.add(student_db)
    db.commit()
    db.refresh(student_db)
    return student_db

def get_students(db: Session):
    """
    Obtiene todos los alumnos registrados.
    """
    return db.query(Student).all()

def get_student_by_id(student_id: int, db: Session):
    """
    Obtiene un alumno por su identificador.
    """
    return db.query(Student).filter(Student.id == student_id).first()

def delete_student(student_id: int, db: Session):
    """
    Elimina un alumno por su identificador.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    db.delete(student)
    db.commit()
    return student

def get_user_by_email(email: str, db: Session):
    """
    Función centralizada que busca un usuario por email en todas las tablas (Teacher y Student).
    Retorna una tupla (usuario, rol) donde rol puede ser 'teacher' o 'student'.
    """
    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin:
        return admin, 'admin'
    
    teacher = db.query(Teacher).filter(Teacher.email == email).first()
    if teacher:
        return teacher, 'teacher'
    
    
    student = db.query(Student).filter(Student.email == email).first()
    if student:
        return student, 'student'
   
    return None, None
