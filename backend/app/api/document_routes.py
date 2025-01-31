from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from db_config import get_db
from services.temario_service import registrar_temario, procesar_pdf_y_subir, eliminar_temario

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
    ruta_archivo = f"uploads/{archivo.filename}"
    with open(ruta_archivo, "wb") as f:
        f.write(await archivo.read())

    # Registrar temario en PostgreSQL
    temario = registrar_temario(db, titulo, descripcion, ruta_archivo, profesor_id)

    # Procesar el archivo PDF y subir embeddings a Pinecone
    metadatos = {"titulo": titulo, "documento_id": temario.id}
    procesar_pdf_y_subir(ruta_archivo, metadatos)

    return {"mensaje": "Temario registrado y procesado correctamente", "temario": temario}

@router.delete("/eliminar-temario/{temario_id}")
async def eliminar_temario_endpoint(
    temario_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint para eliminar un temario y sus embeddings.
    """
    temario = await eliminar_temario(db, temario_id)
    if not temario:
        raise HTTPException(status_code=404, detail="Temario no encontrado")
    
    return {"mensaje": f"Temario '{temario.titulo}' eliminado correctamente"}
