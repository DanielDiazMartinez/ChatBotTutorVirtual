import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.services.image_service import ImageService
from app.models.models import Image


class TestImageService:
    
    @pytest.fixture
    def mock_db(self):
        """Fixture que proporciona una sesión de base de datos simulada."""
        db = MagicMock(spec=Session)
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        db.query = MagicMock()
        return db
    
    @pytest.fixture
    def mock_file(self):
        """Fixture que proporciona un archivo simulado."""
        file = AsyncMock(spec=UploadFile)
        file.filename = "test_image.jpg"
        file.read = AsyncMock(return_value=b"imagen_de_prueba")
        file.seek = AsyncMock()
        return file
    
    @patch("app.services.image_service.os.makedirs")
    @patch("app.services.image_service.open", new_callable=mock_open)
    @patch("app.services.image_service.imghdr.what")
    @patch("app.services.image_service.uuid.uuid4")
    async def test_upload_image_success(self, mock_uuid, mock_imghdr, mock_file_open, mock_makedirs, mock_file, mock_db):
        """Prueba la carga exitosa de una imagen."""
        # Configurar mocks
        mock_imghdr.return_value = "jpeg"
        mock_uuid.return_value = "test-uuid"
        
        # Crear una imagen simulada para el retorno
        mock_image = MagicMock(spec=Image)
        mock_image.id = 1
        mock_image.file_path = "data/uploads/images/test-uuid.jpg"
        
        # Configurar el comportamiento del mock de la base de datos
        mock_db.add.side_effect = lambda img: setattr(img, "id", 1)
        mock_db.refresh.side_effect = lambda img: None
        
        # Ejecutar la función a probar
        result = await ImageService.upload_image(
            file=mock_file,
            user_id=1,
            subject_id=2,
            topic_id=3,
            db=mock_db
        )
        
        # Verificaciones
        assert result is not None
        assert result.file_path.endswith('.jpg')
        mock_makedirs.assert_called_once_with(ImageService.UPLOAD_DIR, exist_ok=True)
        mock_file_open.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @patch("app.services.image_service.imghdr.what")
    async def test_validate_image_invalid_format(self, mock_imghdr, mock_file):
        """Prueba la validación de una imagen con formato inválido."""
        # Configurar el mock para devolver un formato no permitido
        mock_imghdr.return_value = "bmp"
        
        # Verificar que se lance la excepción correspondiente
        with pytest.raises(HTTPException) as excinfo:
            await ImageService._validate_image(mock_file)
        
        assert excinfo.value.status_code == 400
        assert "Formato de imagen no válido" in excinfo.value.detail
    
    @patch("app.services.image_service.imghdr.what")
    async def test_validate_image_too_large(self, mock_imghdr, mock_file):
        """Prueba la validación de una imagen demasiado grande."""
        # Configurar el mock para un formato válido pero tamaño excesivo
        mock_imghdr.return_value = "jpeg"
        mock_file.read.return_value = b"X" * (ImageService.MAX_SIZE_MB * 1024 * 1024 + 1)
        
        # Verificar que se lance la excepción correspondiente
        with pytest.raises(HTTPException) as excinfo:
            await ImageService._validate_image(mock_file)
        
        assert excinfo.value.status_code == 400
        assert "El tamaño de la imagen excede el límite permitido" in excinfo.value.detail
    
    def test_get_image_by_id_found(self, mock_db):
        """Prueba la recuperación de una imagen existente por ID."""
        # Configurar una imagen simulada para el retorno
        mock_image = MagicMock(spec=Image)
        mock_image.id = 1
        mock_image.file_path = "data/uploads/images/test.jpg"
        
        # Configurar el mock de query para devolver la imagen
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_image
        mock_db.query.return_value = mock_query
        
        # Ejecutar la función a probar
        result = ImageService.get_image_by_id(1, mock_db)
        
        # Verificaciones
        assert result is not None
        assert result.id == 1
        assert result.file_path == "data/uploads/images/test.jpg"
        mock_db.query.assert_called_once_with(Image)
        mock_query.filter.assert_called_once()
    
    def test_get_image_by_id_not_found(self, mock_db):
        """Prueba la recuperación de una imagen inexistente por ID."""
        # Configurar el mock de query para devolver None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Ejecutar la función a probar
        result = ImageService.get_image_by_id(999, mock_db)
        
        # Verificaciones
        assert result is None
        mock_db.query.assert_called_once_with(Image)
        mock_query.filter.assert_called_once()
