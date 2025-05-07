from sqlalchemy.orm import Session


from ..models.models import Subject, Teacher, Student
from ..models.schemas import SubjectCreate

def create_subject(db: Session, subject: SubjectCreate) -> Subject:
    """Crea una nueva asignatura"""
    db_subject = Subject(
        name=subject.name,
        code=subject.code,
        description=subject.description
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def get_subject_by_id(db: Session, subject_id: int) -> Subject:
    """Obtiene una asignatura por su ID"""
    return db.query(Subject).filter(Subject.id == subject_id).first()

def get_all_subjects(db: Session) -> list[Subject]:
    """Obtiene todas las asignaturas"""
    return db.query(Subject).all()

def update_subject(db: Session, subject_id: int, subject: SubjectCreate) -> Subject:
    """Actualiza una asignatura existente"""
    db_subject = get_subject_by_id(db, subject_id)
    if not db_subject:
        return None
    
    db_subject.name = subject.name
    db_subject.code = subject.code
    db_subject.description = subject.description
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

def delete_subject(db: Session, subject_id: int) -> bool:
    """Elimina una asignatura"""
    db_subject = get_subject_by_id(db, subject_id)
    if not db_subject:
        return False
    
    db.delete(db_subject)
    db.commit()
    return True

def add_teacher_to_subject(db: Session, subject_id: int, teacher_id: int) -> bool:
    """Añade un profesor a una asignatura"""
    subject = get_subject_by_id(db, subject_id)
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    
    if not subject or not teacher:
        return False
    
    subject.teachers.append(teacher)
    db.commit()
    return True

def add_student_to_subject(db: Session, subject_id: int, student_id: int) -> bool:
    """Añade un estudiante a una asignatura"""
    subject = get_subject_by_id(db, subject_id)
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not subject or not student:
        return False
    
    subject.students.append(student)
    db.commit()
    return True

def remove_teacher_from_subject(db: Session, subject_id: int, teacher_id: int) -> bool:
    """Elimina un profesor de una asignatura"""
    subject = get_subject_by_id(db, subject_id)
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    
    if not subject or not teacher:
        return False
    
    if teacher in subject.teachers:
        subject.teachers.remove(teacher)
        db.commit()
        return True
    return False

def remove_student_from_subject(db: Session, subject_id: int, student_id: int) -> bool:
    """Elimina un estudiante de una asignatura"""
    subject = get_subject_by_id(db, subject_id)
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not subject or not student:
        return False
    
    if student in subject.students:
        subject.students.remove(student)
        db.commit()
        return True
    return False