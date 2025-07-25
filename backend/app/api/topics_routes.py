from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import require_role
from ..models.schemas import APIResponse, TopicCreate, TopicUpdate, TopicOut
from ..services.topic_service import (
    create_topic,
    get_topic_by_id,
    get_topics_by_subject,
    get_all_topics,
    update_topic,
    delete_topic
)

topics_routes = APIRouter()

@topics_routes.post("/", response_model=APIResponse, status_code=201)
def create_new_topic(
    topic: TopicCreate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Crea un nuevo tema (profesores y administradores)"""
    topic_created = create_topic(db=db, topic=topic)
    return {
        "data": topic_created,
        "message": "Tema creado correctamente",
        "status": 201
    }

@topics_routes.get("/{topic_id}", response_model=APIResponse)
def get_topic(
    topic_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Obtiene un tema por su ID (profesores, estudiantes y administradores)"""
    topic = get_topic_by_id(db=db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return {
        "data": topic,
        "message": "Tema obtenido correctamente",
        "status": 200
    }

@topics_routes.get("/subject/{subject_id}", response_model=APIResponse)
def list_topics_by_subject(
    subject_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Lista todos los temas de una asignatura específica (profesores, estudiantes y administradores)"""
    topics = get_topics_by_subject(db=db, subject_id=subject_id)
    return {
        "data": topics,
        "message": "Temas obtenidos correctamente",
        "status": 200
    }

@topics_routes.get("/", response_model=APIResponse)
def list_topics(
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "student", "admin"]))
):
    """Lista todos los temas (profesores, estudiantes y administradores)"""
    topics = get_all_topics(db=db)
    return {
        "data": topics,
        "message": "Temas obtenidos correctamente",
        "status": 200
    }

@topics_routes.put("/{topic_id}", response_model=APIResponse)
def update_topic_route(
    topic_id: int, 
    topic: TopicUpdate, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Actualiza un tema (profesores y administradores)"""
    updated_topic = update_topic(db=db, topic_id=topic_id, topic_update=topic)
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return {
        "data": updated_topic,
        "message": "Tema actualizado correctamente",
        "status": 200
    }

@topics_routes.delete("/{topic_id}", response_model=APIResponse)
def delete_topic_route(
    topic_id: int, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Elimina un tema (profesores y administradores)"""
    if not delete_topic(db=db, topic_id=topic_id):
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return {
        "data": None,
        "message": "Tema eliminado correctamente",
        "status": 200
    }
    return {"message": "Tema eliminado correctamente"}