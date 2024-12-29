from fastapi import APIRouter, Depends, UploadFile, Form
from sqlalchemy.orm import Session
from db_config import get_db
from services.temario_service import registrar_temario, procesar_pdf_y_subir

router = APIRouter()

@router.post("/registrar-temario/")
async def registrar_temario_endpoint(
    titulo: str = Form(...),
    descripcion: str = Form(...),
    profesor_id: int = Form(...),
    archivo: UploadFile = Form(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint para registrar un temario en la base de datos y procesar el PDF.
    """
    # Guardar el archivo localmente
    ruta_archivo = f"archivos/{archivo.filename}"
    with open(ruta_archivo, "wb") as f:
        f.write(await archivo.read())

    # Registrar temario en PostgreSQL
    temario = registrar_temario(db, titulo, descripcion, ruta_archivo, profesor_id)

    # Procesar el archivo PDF y subir embeddings a Pinecone
    metadatos = {"titulo": titulo, "documento_id": temario.id}
    procesar_pdf_y_subir(ruta_archivo, metadatos)

    return {"mensaje": "Temario registrado y procesado correctamente", "temario": temario}
