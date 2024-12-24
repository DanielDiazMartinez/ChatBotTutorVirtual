from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db_config import SessionLocal
from services.groq_service import llamar_api_groq

router = APIRouter()

# Dependencia para la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/groq/")
def contactar_con_groq(db: Session = Depends(get_db)):
    resultado = llamar_api_groq()
    return {"respuesta": resultado}
