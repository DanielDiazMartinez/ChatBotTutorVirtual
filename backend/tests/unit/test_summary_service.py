"""
Tests para el servicio de resúmenes de documentos.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from app.services.summary_service import (
    summarize_chunk,
    generate_document_summary,
    update_document_summary,
    generate_subject_summary,
    get_documents_without_summary
)
from app.models.models import Document, DocumentChunk


class TestSummaryService:
    """Test suite para el servicio de resúmenes."""
    
    @pytest.mark.asyncio
    async def test_summarize_chunk(self):
        """Test para resumir un fragmento de texto."""
        # Mock del servicio de IA
        with patch('app.services.summary_service.generate_google_ai_response') as mock_generate:
            mock_generate.return_value = "Este es un resumen de prueba del fragmento."
            
            chunk_content = "Este es un texto de prueba muy largo que necesita ser resumido para ser más conciso y útil."
            result = await summarize_chunk(chunk_content)
            
            assert result == "Este es un resumen de prueba del fragmento."
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_summarize_chunk_error(self):
        """Test para manejar errores al resumir un fragmento."""
        with patch('app.services.summary_service.generate_google_ai_response') as mock_generate:
            mock_generate.side_effect = Exception("Error de IA")
            
            chunk_content = "Texto de prueba"
            result = await summarize_chunk(chunk_content)
            
            assert result == ""
    
    @pytest.mark.asyncio
    async def test_generate_document_summary_small_document(self):
        """Test para generar resumen de documento pequeño."""
        # Mock de la base de datos
        mock_db = MagicMock(spec=Session)
        mock_document = MagicMock(spec=Document)
        mock_document.id = 1
        mock_document.title = "Documento de prueba"
        
        # Mock de chunks
        mock_chunk = MagicMock(spec=DocumentChunk)
        mock_chunk.content = "Contenido del documento de prueba."
        mock_db.query().filter().order_by().all.return_value = [mock_chunk]
        
        # Mock del servicio de IA
        with patch('app.services.summary_service.generate_google_ai_response') as mock_generate:
            mock_generate.return_value = "Resumen del documento de prueba."
            
            result = await generate_document_summary(mock_document, mock_db)
            
            assert result == "Resumen del documento de prueba."
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_document_summary_no_chunks(self):
        """Test para documento sin chunks."""
        mock_db = MagicMock(spec=Session)
        mock_document = MagicMock(spec=Document)
        mock_document.id = 1
        
        # Sin chunks
        mock_db.query().filter().order_by().all.return_value = []
        
        result = await generate_document_summary(mock_document, mock_db)
        
        assert result == "No se encontraron fragmentos del documento para resumir."
    
    @pytest.mark.asyncio
    async def test_generate_document_summary_large_document(self):
        """Test para generar resumen de documento grande."""
        mock_db = MagicMock(spec=Session)
        mock_document = MagicMock(spec=Document)
        mock_document.id = 1
        mock_document.title = "Documento grande"
        
        # Mock de chunks con contenido largo
        mock_chunk1 = MagicMock(spec=DocumentChunk)
        mock_chunk1.content = "A" * 2000  # Contenido largo
        mock_chunk2 = MagicMock(spec=DocumentChunk)
        mock_chunk2.content = "B" * 2000  # Contenido largo
        
        mock_db.query().filter().order_by().all.return_value = [mock_chunk1, mock_chunk2]
        
        with patch('app.services.summary_service.generate_google_ai_response') as mock_generate:
            mock_generate.side_effect = [
                "Resumen del chunk 1",
                "Resumen del chunk 2"
            ]
            
            # Mock de asyncio.sleep
            with patch('asyncio.sleep'):
                result = await generate_document_summary(mock_document, mock_db, chunk_size=1000)
            
            assert "Resumen del chunk 1 Resumen del chunk 2" == result
            assert mock_generate.call_count == 2
    
    @pytest.mark.asyncio
    async def test_update_document_summary_success(self):
        """Test para actualizar resumen de documento exitosamente."""
        mock_db = MagicMock(spec=Session)
        mock_document = MagicMock(spec=Document)
        mock_document.id = 1
        mock_document.title = "Documento"
        
        # Mock de query
        mock_db.query().filter().first.return_value = mock_document
        
        # Mock de chunks
        mock_chunk = MagicMock(spec=DocumentChunk)
        mock_chunk.content = "Contenido de prueba"
        mock_db.query().filter().order_by().all.return_value = [mock_chunk]
        
        with patch('app.services.summary_service.generate_google_ai_response') as mock_generate:
            mock_generate.return_value = "Resumen generado"
            
            result = await update_document_summary(1, mock_db)
            
            assert result is True
            assert mock_document.summary == "Resumen generado"
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_document_summary_not_found(self):
        """Test para documento no encontrado."""
        mock_db = MagicMock(spec=Session)
        mock_db.query().filter().first.return_value = None
        
        result = await update_document_summary(999, mock_db)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_generate_subject_summary(self):
        """Test para generar resumen de asignatura."""
        mock_db = MagicMock(spec=Session)
        
        # Mock de documentos con resúmenes
        mock_doc1 = MagicMock(spec=Document)
        mock_doc1.title = "Documento 1"
        mock_doc1.summary = "Resumen del documento 1"
        
        mock_doc2 = MagicMock(spec=Document)
        mock_doc2.title = "Documento 2"
        mock_doc2.summary = "Resumen del documento 2"
        
        mock_db.query().filter().all.return_value = [mock_doc1, mock_doc2]
        
        with patch('app.services.summary_service.generate_google_ai_response') as mock_generate:
            mock_generate.return_value = "Resumen general de la asignatura"
            
            result = await generate_subject_summary(1, mock_db)
            
            assert result == "Resumen general de la asignatura"
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_subject_summary_no_documents(self):
        """Test para asignatura sin documentos con resúmenes."""
        mock_db = MagicMock(spec=Session)
        mock_db.query().filter().all.return_value = []
        
        result = await generate_subject_summary(1, mock_db)
        
        assert result == "No hay documentos con resúmenes disponibles para esta asignatura."
    
    def test_get_documents_without_summary(self):
        """Test para obtener documentos sin resumen."""
        mock_db = MagicMock(spec=Session)
        
        # Mock de documentos sin resumen
        mock_doc1 = MagicMock(spec=Document)
        mock_doc1.summary = None
        mock_doc2 = MagicMock(spec=Document)
        mock_doc2.summary = ""
        
        mock_db.query().filter().limit().all.return_value = [mock_doc1, mock_doc2]
        
        result = get_documents_without_summary(mock_db, limit=5)
        
        assert len(result) == 2
        mock_db.query().filter().limit.assert_called_with(5)


@pytest.mark.asyncio
async def test_integration_document_summary_workflow():
    """Test de integración para el flujo completo de resúmenes."""
    mock_db = MagicMock(spec=Session)
    
    # Crear documento mock
    mock_document = MagicMock(spec=Document)
    mock_document.id = 1
    mock_document.title = "Manual de Python"
    mock_document.summary = None
    
    # Crear chunks mock
    chunk1 = MagicMock(spec=DocumentChunk)
    chunk1.content = "Python es un lenguaje de programación interpretado."
    chunk2 = MagicMock(spec=DocumentChunk)
    chunk2.content = "Variables en Python se declaran dinámicamente."
    
    # Configurar mocks de DB
    mock_db.query().filter().first.return_value = mock_document
    mock_db.query().filter().order_by().all.return_value = [chunk1, chunk2]
    
    with patch('app.services.summary_service.generate_response') as mock_generate:
        mock_generate.return_value = "Python es un lenguaje interpretado con variables dinámicas."
        
        # Ejecutar actualización de resumen
        success = await update_document_summary(1, mock_db)
        
        # Verificar resultado
        assert success is True
        assert mock_document.summary == "Python es un lenguaje interpretado con variables dinámicas."
        mock_db.commit.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
