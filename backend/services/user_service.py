from sqlalchemy.orm import Session
from models.user_models import Usuario

def registrar_usuario(db: Session, nombre: str, email: str, password: str, rol: str):
    """
    Registra un nuevo usuario en la base de datos.
    """
    nuevo_usuario = Usuario(nombre=nombre, email=email, password=password, rol=rol)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
