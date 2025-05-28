import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from fastapi import UploadFile, HTTPException
import os
import uuid
from io import BytesIO

from app.services.image_service import ImageService
from app.models.models import Image


class TestImageServiceAdditional:
    
    @pytest.fixture
    def mock_db(self):
        """Fixture que proporciona una sesión de base de datos simulada."""
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        db.query = MagicMock()
        db.rollback = MagicMock()
        db.close = MagicMock()
        return db
    
    @pytest.fixture
    def mock_file(self):
        """Fixture que proporciona un archivo simulado."""
        file = AsyncMock(spec=UploadFile)
        file.filename = "test_image.jpg"
        file.content_type = "image/jpeg"
        file.file = MagicMock()
        file.read = AsyncMock(return_value=b"test_image_content")
        file.seek = AsyncMock()
        return file
    
    @pytest.fixture
    def mock_png_file(self):
        """Fixture que proporciona un archivo PNG simulado."""
        file = AsyncMock(spec=UploadFile)
        file.filename = "test_image.png"
        file.content_type = "image/png"
        file.file = MagicMock()
        file.read = AsyncMock(return_value=b"test_png_content")
        file.seek = AsyncMock()
        return file
    
    @pytest.fixture
    def mock_get_db(self):
        """Fixture que simula el generador get_db."""
        mock_db = self.mock_db()
        
        def mock_generator():
            yield mock_db
            
        return mock_generator()
    
    @patch("app.services.image_service.imghdr.what", return_value="jpeg")
    @patch("app.services.image_service.uuid.uuid4", return_value="test-uuid")
    @patch("app.services.image_service.os.makedirs")
    @patch("app.services.image_service.open", new_callable=mock_open)
    @patch("app.services.image_service.get_db")
    async def test_upload_image_with_auto_db_session(
        self, mock_get_db, mock_file_open, mock_makedirs, mock_uuid, mock_imghdr, mock_file
    ):
        """Prueba la carga de una imagen cuando no se proporciona una sesión de DB."""
        # Configurar el mock del generador get_db
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_db.close = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Ejecutar la función
        result = await ImageService.upload_image(
            file=mock_file,
            user_id=1
        )
        
        # Verificar que se cerró la sesión automáticamente
        mock_db.close.assert_called_once()
    
    @patch("app.services.image_service.imghdr.what", return_value="png")
    @patch("app.services.image_service.uuid.uuid4")
    @patch("app.services.image_service.os.makedirs")
    @patch("app.services.image_service.open", new_callable=mock_open)
    async def test_different_image_formats(
        self, mock_file_open, mock_makedirs, mock_uuid, mock_imghdr, mock_png_file, mock_db
    ):
        """Prueba la carga de diferentes formatos de imagen."""
        # Configurar mocks
        mock_uuid.return_value = "test-uuid"
        
        # Ejecutar la función
        result = await ImageService.upload_image(
            file=mock_png_file,
            user_id=1,
            db=mock_db
        )
        
        # Verificar que la extensión es correcta
        assert result.file_path.endswith('.png')
    
    @patch("app.services.image_service.imghdr.what", return_value=None)
    async def test_validate_undetectable_format(self, mock_imghdr, mock_file):
        """Prueba el caso donde el formato de imagen no se puede detectar."""
        # Verificar que se lance la excepción correspondiente
        with pytest.raises(HTTPException) as excinfo:
            await ImageService._validate_image(mock_file)
        
        assert excinfo.value.status_code == 400
        assert "Formato de imagen no válido" in excinfo.value.detail
    
    @patch("app.services.image_service.imghdr.what", return_value="jpeg")
    @patch("app.services.image_service.open", side_effect=PermissionError("Permission denied"))
    async def test_save_image_permission_error(self, mock_open, mock_imghdr, mock_file):
        """Prueba el caso donde no se tiene permiso para guardar la imagen."""
        # Configurar para que la validación pase
        
        # Verificar que se lance la excepción
        with pytest.raises(Exception) as excinfo:
            await ImageService._save_image(mock_file)
        
        assert "Permission denied" in str(excinfo.value)
    
    @patch("app.services.image_service.imghdr.what", return_value="jpeg")
    @patch("app.services.image_service.os.makedirs")
    @patch("app.services.image_service.open", new_callable=mock_open)
    @patch("app.services.image_service.uuid.uuid4")
    async def test_save_image_filename_without_extension(self, mock_uuid, mock_file_open, mock_makedirs, mock_imghdr):
        """Prueba guardar una imagen con un nombre de archivo sin extensión."""
        # Configurar mocks
        mock_uuid.return_value = "test-uuid"
        file = AsyncMock(spec=UploadFile)
        file.filename = "image_without_extension"
        file.read = AsyncMock(return_value=b"image_content")
        file.seek = AsyncMock()
        
        # Ejecutar la función
        file_path = await ImageService._save_image(file)
        
        # Verificar que se generó un nombre con la extensión vacía
        assert file_path.endswith('test-uuid.')
    
    @patch("app.services.image_service.imghdr.what", return_value="jpeg")
    @patch("app.services.image_service.uuid.uuid4", return_value="test-uuid")
    @patch("app.services.image_service.os.makedirs")
    @patch("app.services.image_service.open", new_callable=mock_open)
    async def test_upload_image_with_metadata(
        self, mock_file_open, mock_makedirs, mock_uuid, mock_imghdr, mock_file, mock_db
    ):
        """Prueba la carga de una imagen con metadatos adicionales."""
        # Ejecutar la función con metadatos adicionales
        result = await ImageService.upload_image(
            file=mock_file,
            user_id=1,
            subject_id=10,
            topic_id=20,
            db=mock_db
        )
        
        # Verificar que los metadatos se pasaron correctamente
        # Capturar el objeto Image que se pasó a db.add
        image_model, = mock_db.add.call_args[0]
        assert image_model.user_id == 1
        assert image_model.subject_id == 10
        assert image_model.topic_id == 20
    
    @patch("app.services.image_service.imghdr.what", return_value="jpeg")
    @patch("app.services.image_service.uuid.uuid4", return_value="test-uuid")
    @patch("app.services.image_service.os.makedirs", side_effect=OSError("Directory creation failed"))
    async def test_directory_creation_failure(self, mock_makedirs, mock_uuid, mock_imghdr, mock_file, mock_db):
        """Prueba el caso donde falla la creación del directorio de imágenes."""
        # Verificar que se lance la excepción apropiada
        with pytest.raises(OSError) as excinfo:
            await ImageService.upload_image(
                file=mock_file,
                user_id=1,
                db=mock_db
            )
        
        assert "Directory creation failed" in str(excinfo.value)
        
        # Verificar que se hizo rollback en la base de datos
        mock_db.rollback.assert_called_once()
    
    def test_get_image_by_id_with_filter(self, mock_db):
        """Prueba la recuperación de imágenes con filtros específicos."""
        # Configurar el comportamiento del mock
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Ejecutar la función
        result = ImageService.get_image_by_id(999, mock_db)
        
        # Verificar que se usó el filtro correcto
        mock_db.query.assert_called_once()
        mock_query.filter.assert_called_once()
