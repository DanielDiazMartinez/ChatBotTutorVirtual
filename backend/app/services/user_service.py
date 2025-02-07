import os
from sqlalchemy.orm import Session
from app.models.models import Document, Teacher, Student
from app.models.schemas import  DocumentCreate, TeacherCreate, StudentCreate, TeacherUpdate
from fastapi import HTTPException, UploadFile
from app.core.security import get_password_hash
from app.core.pinecone import get_pinecone_index
from app.utils.document_utils import extract_text_from_pdf, generate_embedding
from app.core.config import settings


##############################################
# FUNCIONES PARA TEACHERS
##############################################

def registrar_teacher(teacher: TeacherCreate, db: Session):
    """
    Registra un teacher en la base de datos.
    """

    # Verificar si ya existe un teacher con el mismo email
    existing_teacher = db.query(Teacher).filter(Teacher.email == teacher.email).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="El teacher ya está registrado.")

    teacher_data = teacher.model_dump()
    
   
    teacher_data["hashed_password"] = get_password_hash(teacher_data.pop("password"))

    # Crear el objeto de base de datos
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

def delete_teacher(teacher_id: int, db: Session):
    """
    Elimina un teacher por su identificador.
    """
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")
    db.delete(teacher)
    db.commit()
    return teacher

def update_teacher(teacher_id: int, teacherUpdate: TeacherUpdate, db: Session):
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

def update_teacher(teacher_id: int, db: Session):
    """
    Actualiza un teacher por su identificador.
    """
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")
    db.commit()
    return teacher


def save_document(db: Session,pdf_file: UploadFile,document: DocumentCreate):
    """
    Guarda el documento en PostgreSQL y envía su embedding a Pinecone.
    """
   
    if not pdf_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    content = extract_text_from_pdf(pdf_file)

    if not content:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")

    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    
    file_path = os.path.join(settings.UPLOAD_FOLDER, pdf_file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(pdf_file.file.read())

    pinecone = get_pinecone_index()

    new_document = Document(
        title=document.title,
        file_path=file_path,
        description=document.description,
        teacher_id=document.teacher_id
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    embedding = generate_embedding(content)  
   
    pinecone.upsert(vectors=[(str(new_document.id), embedding)])

    return new_document

##############################################
# FUNCIONES PARA STUDENTS
##############################################
def registrar_student(student: StudentCreate, db: Session):
    """
    Registra un alumno en la base de datos.
    """

    # Verificar si ya existe un alumno con el mismo email
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="El alumno ya está registrado.")

    student_data = student.model_dump()
    
   
    student_data["hashed_password"] = get_password_hash(student_data.pop("password"))

    # Crear el objeto de base de datos
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

