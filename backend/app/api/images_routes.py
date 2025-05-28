from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.auth import get_current_user, require_role
from ..models.models import User, Image
from ..models.schemas import APIResponse, ImageOut
from ..services.image_service import  get_image_by_id, upload_image

images_routes = APIRouter()

@images_routes.get("/{image_id}", response_model=APIResponse)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener información de una imagen por su ID"""
    image = get_image_by_id(image_id, db)
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    # Verificar permisos (el propietario o un profesor/admin pueden acceder)
    if (current_user.id != image.user_id and 
        current_user.role not in ["admin", "teacher"]):
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta imagen")
    
    image_out = ImageOut.model_validate(image)
    
    return {
        "data": image_out,
        "message": "Imagen obtenida correctamente",
        "status": 200
    }

@images_routes.get("/{image_id}/file")
async def get_image_file(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Servir el archivo de imagen directamente por su ID"""
    image = get_image_by_id(image_id, db)
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    # Verificar que el archivo existe
    import os
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="Archivo de imagen no encontrado")
    
    return FileResponse(image.file_path)

@images_routes.post("/", response_model=APIResponse, status_code=201)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    subject_id: Optional[int] = Form(None),
    topic_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: dict = Depends(require_role(["teacher", "admin"]))
):
    """Subir una nueva imagen"""
    try:
        # Guardar la imagen
        image = await upload_image(
            file=file,
            user_id=current_user.id,
            subject_id=subject_id,
            topic_id=topic_id,
            db=db
        )
        
 
        if description:
            image.description = description
            db.commit()
            db.refresh(image)
        
        image_out = ImageOut.model_validate(image)
        
        return {
            "data": image_out,
            "message": "Imagen subida correctamente",
            "status": 201
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al subir imagen: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la imagen"
        )
