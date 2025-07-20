import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, UploadFile, Request, status
from sqlalchemy.orm import Session

from app.api.images_routes import get_image, upload_image_endpoint
from app.models.models import Image, User
from app.services.image_service import ImageService


class TestImagesRoutesAdditional:
    
    @pytest.fixture
    def mock_db(self):
        """Fixture que proporciona una sesión de base de datos simulada."""
        db = MagicMock(spec=Session)
        return db
    
    @pytest.fixture
    def mock_admin_user(self):
        """Fixture que proporciona un usuario administrador simulado."""
        user = MagicMock(spec=User)
        user.id = 5
        user.role = "admin"
        return user
    
    @pytest.fixture
    def mock_teacher_user(self):
        """Fixture que proporciona un usuario profesor simulado."""
        user = MagicMock(spec=User)
        user.id = 10
        user.role = "teacher"
        return user
    
    @pytest.fixture
    def mock_student_user(self):
        """Fixture que proporciona un usuario estudiante simulado."""
        user = MagicMock(spec=User)
        user.id = 15
        user.role = "student"
        return user
    
    @pytest.fixture
    def mock_image(self):
        """Fixture que proporciona una imagen simulada."""
        image = MagicMock(spec=Image)
        image.id = 100
        image.file_path = "data/uploads/images/test-additional.jpg"
        image.description = None  # Cambiar a None por defecto
        image.user_id = 15
        image.subject_id = 20
        image.topic_id = None
        image.created_at = "2025-06-26T10:00:00"
        return image
    
    @pytest.mark.asyncio
    @patch('app.api.images_routes.get_image_by_id')
    async def test_admin_can_access_any_image(self, mock_get_image, mock_db, mock_admin_user, mock_image):
        """Prueba que un administrador puede acceder a cualquier imagen."""
        # Configurar el mock para devolver una imagen con diferente propietario
        mock_image.user_id = 999  # ID diferente al del administrador
        mock_image.file_path = "data/uploads/images/test-admin.jpg"
        mock_image.description = "Imagen de otro usuario"
        mock_get_image.return_value = mock_image
        
        # Un administrador debería poder acceder
        response = await get_image(1, mock_db, mock_admin_user)
        
        # Verificar que se pudo acceder sin problemas
        assert response["status"] == 200
        assert response["message"] == "Imagen obtenida correctamente"
        assert response["data"] is not None
    
    @pytest.mark.asyncio
    @patch('app.api.images_routes.get_image_by_id')
    async def test_teacher_can_access_student_image(self, mock_get_image, mock_db, mock_teacher_user, mock_image):
        """Prueba que un profesor puede acceder a las imágenes de sus estudiantes."""
        # La imagen pertenece a un estudiante
        mock_image.user_id = 15  # ID de un estudiante
        mock_image.file_path = "data/uploads/images/test-student.jpg"
        mock_image.description = "Imagen de estudiante"
        mock_get_image.return_value = mock_image
        
        # Un profesor debería poder acceder
        response = await get_image(1, mock_db, mock_teacher_user)
        
        # Verificar que se pudo acceder sin problemas
        assert response["status"] == 200
        assert response["data"] is not None
    
    @pytest.mark.asyncio
    @patch('app.api.images_routes.get_image_by_id')
    async def test_student_cannot_access_other_student_image(self, mock_get_image, mock_db, mock_student_user, mock_image):
        """Prueba que un estudiante no puede acceder a las imágenes de otro estudiante."""
        # La imagen pertenece a otro estudiante
        mock_image.user_id = 999  # ID diferente al del estudiante actual
        mock_image.file_path = "data/uploads/images/test-other-student.jpg"
        mock_image.description = "Imagen de otro estudiante"
        mock_get_image.return_value = mock_image
        
        # Verificar que se lance la excepción correspondiente
        with pytest.raises(HTTPException) as excinfo:
            await get_image(1, mock_db, mock_student_user)
        
        assert excinfo.value.status_code == 403
        assert "No tienes permiso para acceder a esta imagen" in excinfo.value.detail
    
    @pytest.mark.asyncio
    @patch('app.api.images_routes.upload_image')
    async def test_upload_image_with_description(
        self, mock_upload_image, mock_db, mock_student_user, mock_image
    ):
        """Prueba la carga de una imagen con descripción."""
        # Configurar el mock para devolver una imagen
        mock_image.description = "Descripción inicial"  # Asegurar que description es string
        mock_upload_image.return_value = mock_image
        
        # Crear archivo de prueba
        file = AsyncMock(spec=UploadFile)
        file.filename = "test_with_description.jpg"
        
        # Ejecutar la función
        response = await upload_image_endpoint(
            file=file,
            description="Esta es una descripción de prueba",
            db=mock_db,
            current_user=mock_student_user
        )
        
        # Verificar que se actualizó la descripción
        assert mock_image.description == "Esta es una descripción de prueba"
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called_with(mock_image)
    
    @pytest.mark.asyncio
    @patch('app.api.images_routes.upload_image')
    async def test_upload_image_with_subject_topic(
        self, mock_upload_image, mock_db, mock_teacher_user, mock_image
    ):
        """Prueba la carga de una imagen con asignatura y tema."""
        # Configurar el mock para devolver una imagen
        mock_image.description = None  # Asegurar que description es None, no Form(None)
        mock_upload_image.return_value = mock_image
        
        # Crear archivo de prueba
        file = AsyncMock(spec=UploadFile)
        file.filename = "test_with_metadata.jpg"
        
        # Ejecutar la función
        response = await upload_image_endpoint(
            file=file,
            description=None,  # Pasar explícitamente None
            subject_id=30,
            topic_id=40,
            db=mock_db,
            current_user=mock_teacher_user
        )
        
        # Verificar que se pasaron los metadatos correctamente
        mock_upload_image.assert_called_once_with(
            file=file,
            user_id=mock_teacher_user.id,
            subject_id=30,
            topic_id=40,
            db=mock_db
        )
    
    @pytest.mark.asyncio
    @patch('app.api.images_routes.upload_image')
    async def test_upload_image_http_exception(
        self, mock_upload_image, mock_db, mock_student_user
    ):
        """Prueba que las excepciones HTTP se propagan correctamente."""
        # Configurar el mock para lanzar una excepción HTTP
        mock_upload_image.side_effect = HTTPException(
            status_code=400,
            detail="Error de validación simulado"
        )
        
        # Crear archivo de prueba
        file = AsyncMock(spec=UploadFile)
        
        # Verificar que la excepción se propaga
        with pytest.raises(HTTPException) as excinfo:
            await upload_image_endpoint(
                file=file,
                description=None,  # Pasar explícitamente None
                db=mock_db,
                current_user=mock_student_user
            )
        
        assert excinfo.value.status_code == 400
        assert "Error de validación simulado" in excinfo.value.detail
