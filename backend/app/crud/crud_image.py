from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import Image

def create_image(db: Session, image_data: dict) -> Image:
    """
    Crea una nueva imagen en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        image_data: Diccionario con los datos de la imagen
        
    Returns:
        Objeto Image creado
    """
    image = Image(**image_data)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def get_image_by_id(db: Session, image_id: int) -> Optional[Image]:
    """
    Obtiene una imagen por su ID desde la BD.
    
    Args:
        db: Sesión de SQLAlchemy
        image_id: ID de la imagen
        
    Returns:
        Objeto Image o None si no se encuentra
    """
    return db.query(Image).filter(Image.id == image_id).first()

def get_image_by_message(db: Session, message_id: int) -> Optional[Image]:
    """
    Obtiene una imagen asociada a un mensaje por su ID desde la BD.
    
    Args:
        db: Sesión de SQLAlchemy
        message_id: ID del mensaje
        
    Returns:
        Objeto Image o None si no se encuentra
    """
    return db.query(Image).filter(Image.message_id == message_id).first()
