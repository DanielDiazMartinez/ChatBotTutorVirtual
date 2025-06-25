from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from ..models.models import Topic, Subject
from ..models.schemas import TopicCreate, TopicUpdate

def create_topic(db: Session, topic: TopicCreate) -> dict:
    """
    Crea un nuevo tema.
    """
    subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    db_topic = Topic(
        name=topic.name,
        description=topic.description,
        subject_id=topic.subject_id
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
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
    from ..models.models import Document
    
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        return None
    
    return {
        "id": db_topic.id,
        "name": db_topic.name,
        "description": db_topic.description,
        "subject_id": db_topic.subject_id,
        "created_at": db_topic.created_at,
        "documentCount": db.query(Document).filter(Document.topic_id == topic_id).count()
    }

def get_topics_by_subject(db: Session, subject_id: int) -> List[dict]:
    """
    Obtiene todos los temas de una asignatura específica.
    """
    from ..models.models import Document
    
    topics = db.query(Topic).filter(Topic.subject_id == subject_id).all()
    return [
        {
            "id": topic.id,
            "name": topic.name,
            "description": topic.description,
            "subject_id": topic.subject_id,
            "created_at": topic.created_at,
            "documentCount": db.query(Document).filter(Document.topic_id == topic.id).count()
        }
        for topic in topics
    ]

def get_all_topics(db: Session) -> List[dict]:
    """
    Obtiene todos los temas.
    """
    from ..models.models import Document
    
    topics = db.query(Topic).all()
    return [
        {
            "id": topic.id,
            "name": topic.name,
            "description": topic.description,
            "subject_id": topic.subject_id,
            "created_at": topic.created_at,
            "documentCount": db.query(Document).filter(Document.topic_id == topic.id).count()
        }
        for topic in topics
    ]

def update_topic(db: Session, topic_id: int, topic_update: TopicUpdate) -> Optional[dict]:
    """
    Actualiza un tema existente.
    """
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        return None

    if topic_update.subject_id is not None:
        subject = db.query(Subject).filter(Subject.id == topic_update.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    update_data = topic_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_topic, field, value)

    db.commit()
    db.refresh(db_topic)
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
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        return False
    
    db.delete(db_topic)
    db.commit()
    return True