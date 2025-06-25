"""
Servicio para generar resúmenes de documentos usando IA.
"""
import asyncio
import time
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import Document, DocumentChunk, Subject
from app.services.api_service import generate_google_ai_simple

async def generate_document_summary(
    document: Document, 
    db: Session, 
    max_summary_length: int = 1000
) -> str:
    """Genera un resumen completo del documento"""
    try:
        # Obtener todos los chunks del documento (ya divididos semánticamente)
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).order_by(DocumentChunk.chunk_number).all()
        
        if not chunks:
            return "No se encontraron fragmentos del documento para resumir."
        
        # Combinar contenido de los chunks semánticos
        full_content = " ".join([chunk.content for chunk in chunks])
        
        # Truncar el contenido para evitar exceso de tokens
        max_chars = 8000  # Límite para evitar problemas de contexto
        truncated_content = full_content[:max_chars] + "..." if len(full_content) > max_chars else full_content
        
        # Generar resumen directo
        prompt = f"Resume este documento en máximo 300 palabras en texto plano, sin usar guiones, asteriscos, puntos de párrafo ni marcas de formato:\n{truncated_content}"
        
        response = generate_google_ai_simple(prompt)
        return response.strip()
        
    except Exception as e:
        print(f"Error generando resumen del documento {document.id}: {e}")
        return f"Error al generar resumen: {str(e)}"


async def generate_document_summary_by_id(db: Session, document_id: int) -> str:
    """Genera un resumen completo del documento por ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"Documento {document_id} no encontrado")
    
    return await generate_document_summary(document, db)


async def update_document_summary(document_id: int, db: Session) -> bool:
    """Actualiza el resumen de un documento específico"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            print(f"Documento {document_id} no encontrado")
            return False
        
        # Generar el resumen
        summary = await generate_document_summary(document, db)
        
        # Actualizar el documento
        document.summary = summary
        db.commit()
        
        print(f"Resumen actualizado para documento {document.title}")
        return True
        
    except Exception as e:
        print(f"Error actualizando resumen del documento {document_id}: {e}")
        db.rollback()
        return False


async def generate_subject_summary(subject_id: int, db: Session) -> str:
    """Genera un resumen general de la asignatura basado en todos sus documentos"""
    try:
        # Obtener la asignatura
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return "Asignatura no encontrada."
        
        # Siempre generar un nuevo resumen, independientemente de si ya existe uno
        documents = db.query(Document).filter(
            Document.subject_id == subject_id,
        ).all()
        
        if not documents:
            return "No hay documentos disponibles para esta asignatura."
        
        # Limitar drásticamente los documentos procesados
        document_summaries = []
        max_docs = 3  # Solo procesar 3 documentos máximo
        
        for i, doc in enumerate(documents[:max_docs]):
            if doc.summary:
                # Truncar mucho más agresivamente
                summary = doc.summary[:150] + "..." if len(doc.summary) > 150 else doc.summary
                document_summaries.append(f"{doc.title}: {summary}")
        
        if not document_summaries:
            return "No hay resúmenes disponibles para esta asignatura."
        
        combined = " | ".join(document_summaries)
        
        # Prompt ultra-conciso
        prompt = f"Genera un resumen general de la asignatura '{subject.name}' basado en el siguiente contenido de sus documentos. El resumen debe explicar los temas principales que se cubren en esta materia. Máximo 200 palabras en texto plano, sin guiones ni puntos de párrafo: {combined[:2000]}"
        
        response = generate_google_ai_simple(prompt)
        generated_summary = response.strip()
        
        # Guardar el resumen en la base de datos
        subject.summary = generated_summary
        db.commit()
        
        return generated_summary
        
    except Exception as e:
        print(f"Error generando resumen de asignatura {subject_id}: {e}")
        return f"Error al generar resumen de asignatura: {str(e)}"


def update_subject_summary(subject_id: int, db: Session, new_summary: str = None) -> bool:
    """Actualiza el resumen de una asignatura específica"""
    try:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            print(f"Asignatura {subject_id} no encontrada")
            return False
        
        # Si se proporciona un nuevo resumen, usarlo; si no, generar uno
        if new_summary:
            summary = new_summary
        else:
            summary = generate_subject_summary(db, subject_id)
        
        # Actualizar la asignatura
        subject.summary = summary
        db.commit()
        
        print(f"Resumen actualizado para asignatura {subject.name}")
        return True
        
    except Exception as e:
        print(f"Error actualizando resumen de la asignatura {subject_id}: {e}")
        db.rollback()
        return False
