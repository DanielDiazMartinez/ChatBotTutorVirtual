import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.images_routes import get_image, upload_image
from app.models.models import Image, User
from app.services.image_service import ImageService


class TestImagesRoutes:
    
    @pytest.fixture
    def mock_db(self):
        """Fixture que proporciona una sesión de base de datos simulada."""
        db = MagicMock(spec=Session)
        return db
    
    @pytest.fixture
    def mock_current_user(self):
        """Fixture que proporciona un usuario autenticado simulado."""
        user = MagicMock(spec=User)
        user.id = 1
        user.role = "student"
        return user
    
    @pytest.fixture
    def mock_image(self):
        """Fixture que proporciona una imagen simulada."""
        image = MagicMock(spec=Image)
        image.id = 1
        image.file_path = "data/uploads/images/test-image.jpg"
        image.description = "Test image description"
        image.user_id = 1
        image.subject_id = 2
        image.topic_id = 3
        return image
    
    @patch.object(ImageService, "get_image_by_id")
    async def test_get_image_success(self, mock_get_image, mock_db, mock_current_user, mock_image):
        """Prueba la obtención exitosa de una imagen."""
        # Configurar el mock para devolver una imagen
        mock_get_image.return_value = mock_image
        
        # Ejecutar la función a probar
        response = await get_image(1, mock_db, mock_current_user)
        
        # Verificaciones
        assert response["data"] is not None
        assert response["status"] == 200
        assert response["message"] == "Imagen obtenida correctamente"
        mock_get_image.assert_called_once_with(1, mock_db)
    
    @patch.object(ImageService, "get_image_by_id")
    async def test_get_image_not_found(self, mock_get_image, mock_db, mock_current_user):
        """Prueba el caso en que la imagen no se encuentra."""
        # Configurar el mock para devolver None (imagen no encontrada)
        mock_get_image.return_value = None
        
        # Verificar que se lance la excepción correspondiente
        with pytest.raises(HTTPException) as excinfo:
            await get_image(999, mock_db, mock_current_user)
        
        assert excinfo.value.status_code == 404
        assert "Imagen no encontrada" in excinfo.value.detail
    
    @patch.object(ImageService, "get_image_by_id")
    async def test_get_image_unauthorized(self, mock_get_image, mock_db, mock_current_user, mock_image):
        """Prueba el caso en que el usuario no tiene permiso para acceder a la imagen."""
        # Configurar el mock para devolver una imagen con otro propietario
        mock_image.user_id = 999  # ID diferente al del usuario actual
        mock_get_image.return_value = mock_image
        
        # Verificar que se lance la excepción correspondiente
        with pytest.raises(HTTPException) as excinfo:
            await get_image(1, mock_db, mock_current_user)
        
        assert excinfo.value.status_code == 403
        assert "No tienes permiso para acceder a esta imagen" in excinfo.value.detail
    
    @patch.object(ImageService, "upload_image")
    async def test_upload_image_success(self, mock_upload_image, mock_db, mock_current_user, mock_image):
        """Prueba la carga exitosa de una imagen."""
        # Crear un archivo simulado
        file = AsyncMock(spec=UploadFile)
        file.filename = "test_upload.jpg"
        
        # Configurar el mock para devolver una imagen
        mock_upload_image.return_value = mock_image
        
        # Ejecutar la función a probar
        response = await upload_image(
            file=file,
            description="Test upload",
            subject_id=2,
            topic_id=3,
            db=mock_db,
            current_user=mock_current_user
        )
        
        # Verificaciones
        assert response["data"] is not None
        assert response["status"] == 201
        assert response["message"] == "Imagen subida correctamente"
        mock_upload_image.assert_called_once_with(
            file=file,
            user_id=mock_current_user.id,
            subject_id=2,
            topic_id=3,
            db=mock_db
        )
    
    @patch.object(ImageService, "upload_image")
    async def test_upload_image_error(self, mock_upload_image, mock_db, mock_current_user):
        """Prueba el manejo de errores al subir una imagen."""
        # Crear un archivo simulado
        file = AsyncMock(spec=UploadFile)
        file.filename = "test_upload_error.jpg"
        
        # Configurar el mock para lanzar una excepción
        mock_upload_image.side_effect = Exception("Error de prueba")
        
        # Verificar que se lance la excepción correspondiente
        with pytest.raises(HTTPException) as excinfo:
            await upload_image(
                file=file,
                db=mock_db,
                current_user=mock_current_user
            )
        
        assert excinfo.value.status_code == 500
        assert "Error al procesar la imagen" in excinfo.value.detail
