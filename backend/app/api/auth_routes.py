from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db_config import get_db
from services.user_service import registrar_usuario
from models import Usuario, Temario
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

@router.get("/usuarios", summary="Listar todos los usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    """
    Devuelve una lista de todos los usuarios registrados en el sistema.
    """
    usuarios = db.query(Usuario).all()
    return usuarios

@router.get("/temarios", summary="Listar todos los temas")
def listar_temarios(db: Session = Depends(get_db)):
    """
    Devuelve una lista de todos los temas registrados en el sistema.
    """
    temarios = db.query(Temario).all()
    return temarios