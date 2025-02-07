from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.user_service import registrar_teacher, get_students, get_student_by_id, get_teachers, get_teacher_by_id, save_document
from ..models.schemas import DocumentCreate, TeacherCreate, StudentOut, TeacherOut
from typing import List
from fastapi import HTTPException

router = APIRouter(prefix="/teacher", tags=["Teacher"])

@router.post("/register")
def teacher_register(teacher: TeacherCreate , db: Session = Depends(get_db)):
    return registrar_teacher(teacher, db)

@router.get("/list/students",response_model=List[StudentOut])
def list_students(db: Session = Depends(get_db)):

    students = get_students(db)

    if not students:
        raise HTTPException(status_code=404, detail="No hay estudiantes registrados.")
    
    return students

@router.get("/students/{student_id}", response_model=StudentOut)
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

@router.get("/{teacher_id}", response_model=TeacherOut)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = get_teacher_by_id(teacher_id, db)
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")
    return teacher

@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    return delete_teacher(teacher_id, db)

@router.put("/{teacher_id}")
def update_teacher(teacher_id: int, db: Session = Depends(get_db)):
    return update_teacher(teacher_id, db)


@router.post("/upload")
async def upload_document(
    title: str = Form(...),  
    description: str = Form(None),
    teacher_id: int = Form(...),
    pdf_file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    print(f"📌 Recibido en el servidor: title={title}, description={description}, teacher_id={teacher_id}, pdf_file={pdf_file.filename}")
    """
    Sube un documento PDF, guarda los metadatos en PostgreSQL y almacena el embedding en Pinecone.
    """
    
    document_data = DocumentCreate(title=title, description=description, teacher_id=teacher_id)
    document = save_document(db, pdf_file, document_data)
    return {"message": "Documento subido exitosamente", "document_id": document.id}