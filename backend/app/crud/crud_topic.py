from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Topic, Subject

def get_topic_by_id(db: Session, topic_id: int) -> Optional[Topic]:
    """
    Obtiene un tema por su ID desde la BD.
    """
    return db.query(Topic).filter(Topic.id == topic_id).first()

def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    """
    Obtiene una asignatura por su ID desde la BD.
    """
    return db.query(Subject).filter(Subject.id == subject_id).first()

def create_topic(db: Session, name: str, description: str, subject_id: int) -> Topic:
    """
    Crea un nuevo tema en la BD.
    """
    db_topic = Topic(
        name=name,
        description=description,
        subject_id=subject_id
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def get_topics_by_subject_id(db: Session, subject_id: int) -> List[Topic]:
    """
    Obtiene todos los temas de una asignatura desde la BD.
    """
    return db.query(Topic).filter(Topic.subject_id == subject_id).all()

def get_all_topics(db: Session) -> List[Topic]:
    """
    Obtiene todos los temas desde la BD.
    """
    return db.query(Topic).all()

def update_topic(db: Session, topic_id: int, update_data: dict) -> Optional[Topic]:
    """
    Actualiza un tema en la BD.
    """
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        return None

    for field, value in update_data.items():
        setattr(db_topic, field, value)

    db.commit()
    db.refresh(db_topic)
    return db_topic

def delete_topic(db: Session, topic_id: int) -> bool:
    """
    Elimina un tema de la BD.
    """
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        return False
    
    db.delete(db_topic)
    db.commit()
    return True
