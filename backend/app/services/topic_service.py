from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from app.crud import crud_topic
from ..models.schemas import TopicCreate, TopicUpdate

def create_topic(db: Session, topic: TopicCreate) -> dict:
    """
    Crea un nuevo tema.
    """
    subject = crud_topic.get_subject_by_id(db, topic.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    db_topic = crud_topic.create_topic(
        db=db,
        name=topic.name,
        description=topic.description,
        subject_id=topic.subject_id
    )
    
    return {
        "id": db_topic.id,
        "name": db_topic.name,
        "description": db_topic.description,
        "subject_id": db_topic.subject_id,
        "created_at": db_topic.created_at
    }

def get_topic_by_id(db: Session, topic_id: int) -> Optional[dict]:
    """
    Obtiene un tema por su ID.
    """
    db_topic = crud_topic.get_topic_by_id(db, topic_id)
    if not db_topic:
        return None
    
    return {
        "id": db_topic.id,
        "name": db_topic.name,
        "description": db_topic.description,
        "subject_id": db_topic.subject_id,
        "created_at": db_topic.created_at
    }

def get_topics_by_subject(db: Session, subject_id: int) -> List[dict]:
    """
    Obtiene todos los temas de una asignatura específica.
    """
    topics = crud_topic.get_topics_by_subject_id(db, subject_id)
    return [
        {
            "id": topic.id,
            "name": topic.name,
            "description": topic.description,
            "subject_id": topic.subject_id,
            "created_at": topic.created_at
        }
        for topic in topics
    ]

def get_all_topics(db: Session) -> List[dict]:
    """
    Obtiene todos los temas.
    """
    topics = crud_topic.get_all_topics(db)
    return [
        {
            "id": topic.id,
            "name": topic.name,
            "description": topic.description,
            "subject_id": topic.subject_id,
            "created_at": topic.created_at
        }
        for topic in topics
    ]

def update_topic(db: Session, topic_id: int, topic_update: TopicUpdate) -> Optional[dict]:
    """
    Actualiza un tema existente.
    """
    db_topic = crud_topic.get_topic_by_id(db, topic_id)
    if not db_topic:
        return None

    if topic_update.subject_id is not None:
        subject = crud_topic.get_subject_by_id(db, topic_update.subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    update_data = topic_update.model_dump(exclude_unset=True)
    
    db_topic = crud_topic.update_topic(db, topic_id, update_data)
    if not db_topic:
        return None
    
    return {
        "id": db_topic.id,
        "name": db_topic.name,
        "description": db_topic.description,
        "subject_id": db_topic.subject_id,
        "created_at": db_topic.created_at
    }

def delete_topic(db: Session, topic_id: int) -> bool:
    """
    Elimina un tema.
    """
    return crud_topic.delete_topic(db, topic_id)