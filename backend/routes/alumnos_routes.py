from fastapi import APIRouter
from services.pinecone_service import consultar_pinecone
from services.query_processor import procesar_resultados, generar_respuesta

router = APIRouter()

@router.get("/preguntar/")
async def preguntar(pregunta: str):
    """
    Endpoint para que un alumno haga una pregunta.
    """
    resultados = consultar_pinecone(pregunta)
    contexto = procesar_resultados(resultados)
    respuesta = generar_respuesta(pregunta, contexto)
    return {"pregunta": pregunta, "respuesta": respuesta}