from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db_config import get_db
from services.user_service import registrar_usuario

router = APIRouter()

@router.post("/registrar-usuario/")
async def registrar_usuario_endpoint(
    nombre: str,
    email: str,
    password: str,
    rol: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint para registrar un usuario.
    """
    usuario = registrar_usuario(db, nombre, email, password, rol)
    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario": usuario
    }
