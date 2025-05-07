from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.schemas import SubjectCreate, SubjectOut
from ..services.subject_service import (
    create_subject,
    get_subject_by_id,
    get_all_subjects,
    update_subject,
    delete_subject,
    add_teacher_to_subject,
    add_student_to_subject,
    remove_teacher_from_subject,
    remove_student_from_subject
)

subjects_routes = APIRouter()

@subjects_routes.post("/", response_model=SubjectOut)
def create_new_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    """Crea una nueva asignatura"""
    return create_subject(db=db, subject=subject)

@subjects_routes.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    """Obtiene una asignatura por su ID"""
    subject = get_subject_by_id(db=db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return subject

@subjects_routes.get("/", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    """Lista todas las asignaturas"""
    return get_all_subjects(db=db)

@subjects_routes.put("/{subject_id}", response_model=SubjectOut)
def update_subject_route(subject_id: int, subject: SubjectCreate, db: Session = Depends(get_db)):
    """Actualiza una asignatura"""
    updated_subject = update_subject(db=db, subject_id=subject_id, subject=subject)
    if not updated_subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return updated_subject

@subjects_routes.delete("/{subject_id}")
def delete_subject_route(subject_id: int, db: Session = Depends(get_db)):
    """Elimina una asignatura"""
    if not delete_subject(db=db, subject_id=subject_id):
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return {"message": "Asignatura eliminada correctamente"}

@subjects_routes.post("/{subject_id}/teachers/{teacher_id}")
def add_teacher(subject_id: int, teacher_id: int, db: Session = Depends(get_db)):
    """Añade un profesor a una asignatura"""
    if not add_teacher_to_subject(db=db, subject_id=subject_id, teacher_id=teacher_id):
        raise HTTPException(status_code=404, detail="Asignatura o profesor no encontrado")
    return {"message": "Profesor añadido correctamente a la asignatura"}

@subjects_routes.post("/{subject_id}/students/{student_id}")
def add_student(subject_id: int, student_id: int, db: Session = Depends(get_db)):
    """Añade un estudiante a una asignatura"""
    if not add_student_to_subject(db=db, subject_id=subject_id, student_id=student_id):
        raise HTTPException(status_code=404, detail="Asignatura o estudiante no encontrado")
    return {"message": "Estudiante añadido correctamente a la asignatura"}

@subjects_routes.delete("/{subject_id}/teachers/{teacher_id}")
def remove_teacher(subject_id: int, teacher_id: int, db: Session = Depends(get_db)):
    """Elimina un profesor de una asignatura"""
    if not remove_teacher_from_subject(db=db, subject_id=subject_id, teacher_id=teacher_id):
        raise HTTPException(status_code=404, detail="Asignatura o profesor no encontrado")
    return {"message": "Profesor eliminado correctamente de la asignatura"}

@subjects_routes.delete("/{subject_id}/students/{student_id}")
def remove_student(subject_id: int, student_id: int, db: Session = Depends(get_db)):
    """Elimina un estudiante de una asignatura"""
    if not remove_student_from_subject(db=db, subject_id=subject_id, student_id=student_id):
        raise HTTPException(status_code=404, detail="Asignatura o estudiante no encontrado")
    return {"message": "Estudiante eliminado correctamente de la asignatura"}