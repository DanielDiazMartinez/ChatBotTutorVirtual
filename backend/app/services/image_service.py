import logging
import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from PIL import Image as PILImage
import imghdr
import base64
import mimetypes
from app.models.models import Image
from app.core.database import get_db
from app.crud import crud_image
from sqlalchemy.orm import Session

"""Servicio para manejar operaciones con imágenes, incluyendo la preparación para Google AI"""

# Configuración para tamaños y formatos permitidos
ALLOWED_FORMATS = ["jpeg", "jpg", "png"]
MAX_SIZE_MB = 5  # Tamaño máximo en MB
UPLOAD_DIR = "data/uploads/images"

# Clase para mantener compatibilidad con las pruebas
class ImageService:
    """
    Clase de servicio para operaciones con imágenes.
    Esta clase envuelve las funciones individuales para mantener compatibilidad con las pruebas.
    """
    @staticmethod
    async def upload_image(
        file: UploadFile,
        user_id: int,
        subject_id: Optional[int] = None,
        topic_id: Optional[int] = None,
        db: Session = None
    ) -> Image:
        """
        Maneja la subida de una imagen.
        Envuelve la función global upload_image.
        """
        return await upload_image(file, user_id, subject_id, topic_id, db)
    
    @staticmethod
    async def _validate_image(file: UploadFile) -> bool:
        """
        Valida el formato y tamaño de la imagen.
        Envuelve la función global _validate_image.
        """
        return await _validate_image(file)
    
    @staticmethod
    async def _save_image(file: UploadFile) -> str:
        """
        Guarda la imagen en el sistema de archivos.
        Envuelve la función global _save_image.
        """
        return await _save_image(file)
    
    @staticmethod
    def get_image_by_id(image_id: int, db: Session) -> Optional[Image]:
        """
        Obtiene una imagen por su ID.
        Envuelve la función global get_image_by_id.
        """
        return get_image_by_id(image_id, db)
    
    @staticmethod
    def get_image_by_message(message_id: int, db: Session) -> Optional[Image]:
        """
        Obtiene una imagen asociada a un mensaje por su ID.
        Envuelve la función global get_image_by_message.
        """
        return get_image_by_message(message_id, db)
    
    @staticmethod
    def prepare_image_for_google_ai(image: Image) -> Optional[tuple[str, str]]:
        """
        Prepara una imagen para ser enviada a la API de Google AI Studio.
        Envuelve la función global prepare_image_for_google_ai.
        """
        return prepare_image_for_google_ai(image)

async def upload_image(
    file: UploadFile,
    user_id: int,
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    db: Session = None
) -> Image:
    """
    Maneja la subida de una imagen:
    1. Valida el formato y tamaño
    2. Almacena en el sistema de archivos
    3. Registra en la base de datos

    Args:
        file: Archivo de imagen subido
        user_id: ID del usuario que sube la imagen
        subject_id: ID de la asignatura (opcional)
        topic_id: ID del tema (opcional)
        db: Sesión de base de datos

    Returns:
        Objeto Image con la información registrada en la base de datos
    """
    if db is None:
        db = next(get_db())
        close_db = True
    else:
        close_db = False

    try:
        await _validate_image(file)
        file_path = await _save_image(file)
        
        image_data = {
            'file_path': file_path,
            'user_id': user_id,
            'subject_id': subject_id,
            'topic_id': topic_id
        }

        # Usar CRUD para crear la imagen
        image = crud_image.create_image(db, image_data)
        return image

    except Exception as e:
        db.rollback()
        raise e
    finally:
        if close_db:
            db.close()

async def _validate_image(file: UploadFile) -> bool:
    """
    Valida el formato y tamaño de la imagen.
    Lanza una excepción si la validación falla.

    Args:
        file: Archivo a validar

    Returns:
        True si la validación es exitosa
    """

    content = await file.read()
    await file.seek(0)  # Reposicionar el cursor al inicio

    img_format = imghdr.what(None, h=content)
    if not img_format or img_format.lower() not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de imagen no válido. Debe ser uno de: {', '.join(ALLOWED_FORMATS)}"
        )

    # Verificar el tamaño
    size_in_mb = len(content) / (1024 * 1024)  # Convertir bytes a MB
    if size_in_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"El tamaño de la imagen excede el límite permitido de {MAX_SIZE_MB}MB"
        )
    await file.seek(0)

    return True

async def _save_image(file: UploadFile) -> str:
    """
    Guarda la imagen en el sistema de archivos

    Args:
        file: Archivo a guardar

    Returns:
        Ruta del archivo guardado
    """
    # Crear directorio si no existe
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Generar nombre único para el archivo
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Guardar archivo
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Reposicionamos el cursor por si se necesita leer de nuevo
    await file.seek(0)

    return file_path

def get_image_by_id(image_id: int, db: Session) -> Optional[Image]:
    """
    Obtiene una imagen por su ID

    Args:
        image_id: ID de la imagen
        db: Sesión de base de datos

    Returns:
        Objeto Image o None si no se encuentra
    """
    return crud_image.get_image_by_id(db, image_id)

def get_image_by_message(message_id: int, db: Session) -> Optional[Image]:
    """
    Obtiene una imagen asociada a un mensaje por su ID

    Args:
        message_id: ID del mensaje
        db: Sesión de base de datos

    Returns:
        Objeto Image o None si no se encuentra
    """
    return crud_image.get_image_by_message(db, message_id)

def prepare_image_for_google_ai(image: Image) -> Optional[tuple[str, str]]:
    """
    Prepara una imagen para ser enviada a la API de Google AI Studio,
    codificándola en base64 y obteniendo su tipo MIME.

    Args:
        image: Objeto Image de la base de datos.

    Returns:
        Una tupla con (base64_encoded_image, mime_type) si la imagen existe,
        None en caso contrario o si hay un error al leer el archivo.
    """
    if not image or not os.path.exists(image.file_path):
        return None

    try:
        with open(image.file_path, "rb") as image_file:
            image_content = image_file.read()
            base64_encoded = base64.b64encode(image_content).decode("utf-8")
            mime_type = mimetypes.guess_type(image.file_path)[0]
            return base64_encoded, mime_type
    except Exception as e:
        logging.error(f"Error al preparar la imagen {image.id} para Google AI: {e}")
        return None