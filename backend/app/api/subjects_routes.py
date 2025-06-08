from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..core.auth import require_role, get_current_user

logger = logging.getLogger(__name__)
from ..models.schemas import APIResponse, SubjectCreate, SubjectOut, UserIdsRequest, DocumentOut, StudentAnalysisSummary, StudentAnalysisRequest, StudentAnalysisStatistics
from ..models.models import User, Document
from ..services.subject_service import (
    add_user_to_subject,
    add_multiple_users_to_subject,
    remove_multiple_users_from_subject,
    create_subject,
    get_subject_by_id,
    get_all_subjects,
    update_subject,
    delete_subject,
    get_subject_documents,
    get_subject_users,
)
from ..services.student_analysis_service import (
    generate_student_analysis_summary,
    get_subject_analysis_statistics,
    get_most_active_students,
    get_subject_question_topics
)

subjects_routes = APIRouter()

@subjects_routes.post("/", response_model=APIResponse, status_code=201)
def create_new_subject(
    subject: SubjectCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Crea una nueva asignatura (solo administradores)"""
    subject_created = create_subject(db=db, subject=subject)
    
    # Verificar si hay error en la respuesta
    if "error" in subject_created:
        raise HTTPException(
            status_code=subject_created["status"], 
            detail=subject_created["error"]
        )
        
    return {
        "data": subject_created,
        "message": "Asignatura creada correctamente",
        "status": 201
    }

@subjects_routes.get("/{subject_id}", response_model=APIResponse)
def get_subject(
    subject_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["student", "teacher", "admin"]))
):
    """Obtiene una asignatura por su ID"""
    subject = get_subject_by_id(db=db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return {
        "data": subject,
        "message": "Asignatura obtenida correctamente",
        "status": 200
    }

@subjects_routes.get("/", response_model=APIResponse)
def list_subjects(
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["student", "teacher", "admin"]))
):
    """Lista todas las asignaturas"""
    subjects = get_all_subjects(db=db)
    return {
        "data": subjects,
        "message": "Asignaturas obtenidas correctamente",
        "status": 200
    }

@subjects_routes.put("/{subject_id}", response_model=APIResponse)
def update_subject_route(
    subject_id: int, 
    subject: SubjectCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Actualiza una asignatura (solo administradores)"""
    updated_subject = update_subject(db=db, subject_id=subject_id, subject=subject)
    if not updated_subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return {
        "data": updated_subject,
        "message": "Asignatura actualizada correctamente",
        "status": 200
    }

@subjects_routes.delete("/{subject_id}", response_model=APIResponse)
def delete_subject_route(
    subject_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Elimina una asignatura (solo administradores)"""
    if not delete_subject(db=db, subject_id=subject_id):
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return {
        "data": None,
        "message": "Asignatura eliminada correctamente",
        "status": 200
    }

@subjects_routes.post("/{subject_id}/user/{user_id}", response_model=APIResponse)
def add_user_to_subject_route(
    subject_id: int, 
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Agrega un profesor o estudiante a una asignatura (solo administradores)"""

    if not add_user_to_subject(db=db, subject_id=subject_id, user_id=user_id):
        raise HTTPException(status_code=400, detail="No se pudo agregar el usuario a la asignatura")
    
    return {
        "data": None,
        "message": "Usuario agregado a la asignatura correctamente",
        "status": 200
    }

@subjects_routes.post("/{subject_id}/users", response_model=APIResponse)
def add_multiple_users_to_subject_route(
    subject_id: int,
    users_request: UserIdsRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Agrega múltiples usuarios (profesores o estudiantes) a una asignatura (solo administradores)"""
    
    result = add_multiple_users_to_subject(
        db=db, 
        subject_id=subject_id, 
        user_ids=users_request.user_ids
    )
    
    if not result["success"]:
        status_code = 404 if result.get("error") == "Asignatura no encontrada" else 400
        raise HTTPException(status_code=status_code, detail=result.get("error", "Error al agregar usuarios"))
    
    return {
        "data": {
            "added": result["added"],
            "failed": result["failed"]
        },
        "message": f"Se añadieron {len(result['added'])} usuarios a la asignatura. {len(result['failed'])} fallaron.",
        "status": 200
    }

@subjects_routes.get("/{subject_id}/documents", response_model=APIResponse)
def get_subject_documents_route(
    subject_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["student", "teacher", "admin"]))
):
    """Obtiene todos los documentos asociados a una asignatura"""
    documents = get_subject_documents(db=db, subject_id=subject_id)
    if documents is None:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    # Convertir los documentos al esquema DocumentOut para serialización
    document_outs = [DocumentOut.model_validate(doc) for doc in documents]
    return {
        "data": document_outs,
        "message": "Documentos de la asignatura obtenidos correctamente",
        "status": 200
    }

@subjects_routes.delete("/{subject_id}/users", response_model=APIResponse)
def remove_multiple_users_from_subject_route(
    subject_id: int,
    users_request: UserIdsRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["admin"]))
):
    """Elimina múltiples usuarios (profesores o estudiantes) de una asignatura (solo administradores)"""
    
    result = remove_multiple_users_from_subject(
        db=db, 
        subject_id=subject_id, 
        user_ids=users_request.user_ids
    )
    
    if not result["success"]:
        status_code = 404 if result.get("error") == "Asignatura no encontrada" else 400
        raise HTTPException(status_code=status_code, detail=result.get("error", "Error al eliminar usuarios"))
    
    return {
        "data": {
            "removed": result["removed"],
            "failed": result["failed"]
        },
        "message": f"Se eliminaron {len(result['removed'])} usuarios de la asignatura. {len(result['failed'])} fallaron.",
        "status": 200
    }

@subjects_routes.get("/{subject_id}/users", response_model=APIResponse)
def get_subject_users_route(
    subject_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["student", "teacher", "admin"]))
):
    """Obtiene todos los usuarios asociados a una asignatura"""
    users_data = get_subject_users(db=db, subject_id=subject_id)
    if users_data is None:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    return {
        "data": users_data,
        "message": "Usuarios de la asignatura obtenidos correctamente",
        "status": 200
    }

# ----------------------------------------
# ENDPOINTS PARA ANÁLISIS DE ESTUDIANTES
# ----------------------------------------

@subjects_routes.post("/{subject_id}/analysis", response_model=APIResponse)
async def generate_subject_student_analysis(
    subject_id: int,
    analysis_request: StudentAnalysisRequest = StudentAnalysisRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Genera un análisis completo de las preguntas y participación de estudiantes en una asignatura.
    Utiliza IA para identificar deficiencias y gaps en el aprendizaje.
    Accesible solo para profesores y administradores.
    """
    try:
        # Verificar que la asignatura existe
        subject = get_subject_by_id(db=db, subject_id=subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Asignatura no encontrada")
        
        # Generar el análisis completo
        analysis_summary = await generate_student_analysis_summary(
            subject_id=subject_id,
            db=db,
            days_limit=analysis_request.days_back,
            min_participation=analysis_request.min_participation
        )
        
        if not analysis_summary:
            raise HTTPException(
                status_code=500, 
                detail="Error interno al generar el análisis de estudiantes"
            )
        
        # Crear la respuesta estructurada
        response_data = StudentAnalysisSummary(
            subject_id=subject_id,
            subject_name=subject["name"],
            analysis_summary=analysis_summary["analysis"],
            statistics=StudentAnalysisStatistics(
                total_messages=analysis_summary["statistics"]["total_messages"],
                unique_students=analysis_summary["statistics"]["unique_students"],
                participation_rate=analysis_summary["statistics"]["participation_rate"],
                most_active_students=analysis_summary["statistics"]["most_active_students"]
            ),
            sample_questions=analysis_summary.get("sample_questions", [])
        )
        
        return {
            "data": response_data.model_dump(),
            "message": "Análisis de estudiantes generado correctamente",
            "status": 200
        }
        
    except Exception as e:
        logger.error(f"Error generando análisis de estudiantes para asignatura {subject_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@subjects_routes.get("/{subject_id}/analysis/statistics", response_model=APIResponse)
def get_subject_student_statistics(
    subject_id: int,
    days_back: int = Query(default=30, description="Días hacia atrás para analizar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """
    Obtiene estadísticas de participación de estudiantes en una asignatura.
    Accesible solo para profesores y administradores.
    """
    try:
        # Verificar que la asignatura existe
        subject = get_subject_by_id(db=db, subject_id=subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Asignatura no encontrada")
        
        # Obtener estadísticas
        statistics = get_subject_analysis_statistics(
            subject_id=subject_id,
            db=db,
            days_back=days_back
        )
        
        return {
            "data": statistics,
            "message": "Estadísticas de participación obtenidas correctamente",
            "status": 200
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas para asignatura {subject_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
