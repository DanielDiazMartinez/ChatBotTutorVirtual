from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from ..models.models import Topic, Subject
from ..models.schemas import TopicCreate, TopicUpdate

def create_topic(db: Session, topic: TopicCreate) -> Topic:
    """
    Crea un nuevo tema.
    """
    # Verificar que la asignatura existe
    subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    # Crear el tema
    db_topic = Topic(
        name=topic.name,
        description=topic.description,
        subject_id=topic.subject_id
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def get_topic_by_id(db: Session, topic_id: int) -> Optional[Topic]:
    """
    Obtiene un tema por su ID.
    """
    return db.query(Topic).filter(Topic.id == topic_id).first()

def get_topics_by_subject(db: Session, subject_id: int) -> List[Topic]:
    """
    Obtiene todos los temas de una asignatura específica.
    """
    return db.query(Topic).filter(Topic.subject_id == subject_id).all()

def get_all_topics(db: Session) -> List[Topic]:
    """
    Obtiene todos los temas.
    """
    return db.query(Topic).all()

def update_topic(db: Session, topic_id: int, topic_update: TopicUpdate) -> Optional[Topic]:
    """
    Actualiza un tema existente.
    """
    db_topic = get_topic_by_id(db, topic_id)
    if not db_topic:
        return None

    # Si se va a cambiar la asignatura, verificar que existe
    if topic_update.subject_id is not None:
        subject = db.query(Subject).filter(Subject.id == topic_update.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    # Actualizar solo los campos proporcionados
    update_data = topic_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_topic, field, value)

    db.commit()
    db.refresh(db_topic)
    return db_topic

def delete_topic(db: Session, topic_id: int) -> bool:
    """
    Elimina un tema.
    Retorna True si el tema fue eliminado, False si no se encontró.
    """
    db_topic = get_topic_by_id(db, topic_id)
    if not db_topic:
        return False
    
    db.delete(db_topic)
    db.commit()
    return True