from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.alumno_model import Alumno
from app.models.documento_model import Documento
from app.models.pregunta_model import Pregunta
from app.services.pinecone_service import consultar_pinecone
from app.services.query_processor import procesar_resultados, generar_respuesta

router = APIRouter()

@router.post("/preguntar/")
async def preguntar(
    pregunta: str,
    documento_id: int,
    current_user: Alumno = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para que un alumno haga una pregunta y la guarde en la base de datos.
    """
    if not isinstance(current_user, Alumno):
        raise HTTPException(status_code=403, detail="Solo los alumnos pueden hacer preguntas")
    
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    # Procesar la pregunta
    resultados = consultar_pinecone(pregunta)
    contexto = procesar_resultados(resultados)
    respuesta = generar_respuesta(pregunta, contexto)
    
    # Guardar la pregunta y respuesta en la base de datos
    nueva_pregunta = Pregunta(
        texto=pregunta,
        alumno_id=current_user.id,
        documento_id=documento_id,
        respuesta=respuesta
    )
    db.add(nueva_pregunta)
    db.commit()
    db.refresh(nueva_pregunta)
    
    return {
        "id": nueva_pregunta.id,
        "pregunta": pregunta,
        "respuesta": respuesta,
        "contexto": contexto,
        "fecha": nueva_pregunta.fecha
    }