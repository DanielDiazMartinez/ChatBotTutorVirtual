from fastapi import APIRouter
from services.query_service import consultar_pinecone

router = APIRouter()

@router.get("/preguntar/")
async def preguntar(pregunta: str):
    """
    Endpoint para que un alumno haga una pregunta.
    """
    resultados = consultar_pinecone(pregunta)
    return {
        "pregunta": pregunta,
        "resultados": resultados
    }
