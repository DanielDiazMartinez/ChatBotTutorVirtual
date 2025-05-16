from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.models import Subject, User, teacher_subject, student_subject
from ..models.schemas import SubjectCreate

def create_subject(db: Session, subject: SubjectCreate) -> dict:
    """Crea una nueva asignatura"""
    
    # Primero verificamos si ya existe una asignatura con ese código
    existing_subject = db.query(Subject).filter(Subject.code == subject.code).first()
    if existing_subject:
        return {
            "error": "Ya existe una asignatura con ese código",
            "status": 400
        }
        
    # Si no existe, creamos la nueva asignatura
    db_subject = Subject(
        name=subject.name,
        code=subject.code,
        description=subject.description
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return {
        "id": db_subject.id,
        "name": db_subject.name,
        "code": db_subject.code,
        "description": db_subject.description,
        "created_at": db_subject.created_at
    }

def get_subject_by_id(db: Session, subject_id: int) -> dict:
    """Obtiene una asignatura por su ID"""
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return None
    
    # Obtener listas de profesores y estudiantes
    teachers = [
        {
            "id": teacher.id,
            "email": teacher.email,
            "full_name": teacher.full_name,
            "role": teacher.role
        }
        for teacher in db_subject.teachers
    ] if db_subject.teachers else []
    
    students = [
        {
            "id": student.id,
            "email": student.email,
            "full_name": student.full_name,
            "role": student.role
        }
        for student in db_subject.students
    ] if db_subject.students else []
    
    return {
        "id": db_subject.id,
        "name": db_subject.name,
        "code": db_subject.code,
        "description": db_subject.description,
        "created_at": db_subject.created_at,
        "teachers": teachers,
        "students": students
    }

def get_all_subjects(db: Session) -> list[dict]:
    """Obtiene todas las asignaturas"""
    subjects = db.query(Subject).all()
    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "created_at": subject.created_at,
            "teachers": [
                {
                    "id": teacher.id,
                    "email": teacher.email,
                    "full_name": teacher.full_name,
                    "role": teacher.role
                }
                for teacher in subject.teachers
            ],
            "students": [
                {
                    "id": student.id,
                    "email": student.email,
                    "full_name": student.full_name,
                    "role": student.role
                }
                for student in subject.students
            ]
        }
        for subject in subjects
    ]

def update_subject(db: Session, subject_id: int, subject: SubjectCreate) -> dict:
    """Actualiza una asignatura existente"""
    # Aquí obtenemos el objeto directamente ya que get_subject_by_id ahora devuelve un dict
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return None
    
    db_subject.name = subject.name
    db_subject.code = subject.code
    db_subject.description = subject.description
    
    db.commit()
    db.refresh(db_subject)
    
    # Preparamos la respuesta
    teachers = [
        {
            "id": teacher.id,
            "email": teacher.email,
            "full_name": teacher.full_name,
            "role": teacher.role
        }
        for teacher in db_subject.teachers
    ] if db_subject.teachers else []
    
    students = [
        {
            "id": student.id,
            "email": student.email,
            "full_name": student.full_name,
            "role": student.role
        }
        for student in db_subject.students
    ] if db_subject.students else []
    
    return {
        "id": db_subject.id,
        "name": db_subject.name,
        "code": db_subject.code,
        "description": db_subject.description,
        "created_at": db_subject.created_at,
        "teachers": teachers,
        "students": students
    }

def delete_subject(db: Session, subject_id: int) -> bool:
    """Elimina una asignatura"""
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        return False
    
    db.delete(db_subject)
    db.commit()
    return True

def add_user_to_subject(db: Session, subject_id: int, user_id: int) -> bool:
    """Agrega un usuario a una asignatura"""
    print(f"Intentando agregar: subject_id={subject_id}, user_id={user_id}")

    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    db_user = db.query(User).filter(User.id == user_id).first()
    
    print(f"Subject encontrado: {db_subject is not None}")
    print(f"User encontrado: {db_user is not None}")
    
    if not db_subject or not db_user:
        print("No se encontró asignatura o usuario")
        return False
    
    print(f"Rol del usuario: {db_user.role}")
    if db_user.role == "admin":
        print("El usuario es admin, operación no permitida")
        return False
    
    try:
        if db_user.role == "teacher":
            print("Intentando agregar profesor")
            print(f"Ya está en teachers: {db_user in db_subject.teachers}")
            if db_user not in db_subject.teachers:
                db_subject.teachers.append(db_user)
                print("Profesor agregado correctamente")
                
        elif db_user.role == "student":
            print("Intentando agregar estudiante")
            print(f"Ya está en students: {db_user in db_subject.students}")
            if db_user not in db_subject.students:
                db_subject.students.append(db_user)
                print("Estudiante agregado correctamente")
        else:
            print(f"Rol no reconocido: {db_user.role}")
            return False
        
        db.commit()
        print("Commit realizado con éxito")
        return True
    except Exception as e:
        print(f"Error al agregar usuario: {str(e)}")
        db.rollback()
        return False
