from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.schemas import TopicCreate, TopicUpdate, TopicOut
from ..services.topic_service import (
    create_topic,
    get_topic_by_id,
    get_topics_by_subject,
    get_all_topics,
    update_topic,
    delete_topic
)

topics_routes = APIRouter()

@topics_routes.post("/", response_model=TopicOut)
def create_new_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    """Crea un nuevo tema"""
    return create_topic(db=db, topic=topic)

@topics_routes.get("/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Obtiene un tema por su ID"""
    topic = get_topic_by_id(db=db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return topic

@topics_routes.get("/subject/{subject_id}", response_model=List[TopicOut])
def list_topics_by_subject(subject_id: int, db: Session = Depends(get_db)):
    """Lista todos los temas de una asignatura específica"""
    return get_topics_by_subject(db=db, subject_id=subject_id)

@topics_routes.get("/", response_model=List[TopicOut])
def list_topics(db: Session = Depends(get_db)):
    """Lista todos los temas"""
    return get_all_topics(db=db)

@topics_routes.put("/{topic_id}", response_model=TopicOut)
def update_topic_route(topic_id: int, topic: TopicUpdate, db: Session = Depends(get_db)):
    """Actualiza un tema"""
    updated_topic = update_topic(db=db, topic_id=topic_id, topic_update=topic)
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return updated_topic

@topics_routes.delete("/{topic_id}")
def delete_topic_route(topic_id: int, db: Session = Depends(get_db)):
    """Elimina un tema"""
    if not delete_topic(db=db, topic_id=topic_id):
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    return {"message": "Tema eliminado correctamente"}