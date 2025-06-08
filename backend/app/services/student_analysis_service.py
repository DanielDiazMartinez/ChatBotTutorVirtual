"""
Servicio de Análisis de Estudiantes - Analiza preguntas y genera resúmenes para profesores
Este servicio analiza las preguntas de los estudiantes en una asignatura y genera insights
sobre las carencias y áreas de mejora detectadas.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import logging
import re
from datetime import datetime, timedelta

from ..models.models import Message, Conversation, User, Subject, Topic, Document
from ..services.api_service import generate_google_ai_simple
from ..services.subject_service import get_subject_documents
from ..services.topic_service import get_topics_by_subject

# Configuración de logging
logger = logging.getLogger(__name__)


def clean_and_format_analysis_text(raw_text: str, subject_name: str) -> str:
    """
    Limpia y formatea el texto del análisis generado por IA.
    
    Args:
        raw_text: Texto crudo generado por la IA
        subject_name: Nombre de la asignatura
        
    Returns:
        Texto formateado en HTML limpio
    """
    try:
        # Limpiar caracteres extraños al inicio y final
        text = raw_text.strip()
        
        # Remover ``` html al inicio y ``` al final si existen
        if text.startswith('```html'):
            text = text[7:].strip()
        elif text.startswith('```'):
            text = text[3:].strip()
        
        if text.endswith('```'):
            text = text[:-3].strip()
        
        # Si el texto no está en formato HTML, convertirlo
        if not text.startswith('<div'):
            text = convert_plain_text_to_html(text, subject_name)
        
        # Asegurar que esté envuelto en div con clase
        if not text.startswith('<div class="analysis-content">'):
            if text.startswith('<div>'):
                text = text.replace('<div>', '<div class="analysis-content">', 1)
            else:
                text = f'<div class="analysis-content">\n{text}\n</div>'
        
        return text
        
    except Exception as e:
        logger.error(f"Error al limpiar análisis: {str(e)}")
        # Retornar un formato básico en caso de error
        return f'<div class="analysis-content"><h4>Análisis - {subject_name}</h4><p>{raw_text}</p></div>'


def convert_plain_text_to_html(text: str, subject_name: str) -> str:
    """
    Convierte texto plano a formato HTML estructurado.
    
    Args:
        text: Texto en formato plano
        subject_name: Nombre de la asignatura
        
    Returns:
        Texto convertido a HTML
    """
    try:
        # Dividir el texto en secciones
        lines = text.split('\n')
        html_lines = [f'<h3>Análisis de Estudiantes - {subject_name}</h3>']
        
        current_section = ""
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detectar títulos de sección
            if any(keyword in line.lower() for keyword in [
                'resumen general', 'carencias detectadas', 'patrones comunes', 
                'nivel de comprensión', 'recomendaciones', 'próximos pasos'
            ]):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                    
                # Limpiar el título y añadirlo como h4
                title = line.rstrip(':').strip()
                html_lines.append(f'<h4>{title}:</h4>')
                current_section = title.lower()
                continue
            
            # Detectar elementos de lista (que empiecen con números o guiones)
            if re.match(r'^[\d\-\•\*]\s*\.?\s*', line):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                
                # Limpiar el texto del elemento de lista
                item_text = re.sub(r'^[\d\-\•\*]\s*\.?\s*', '', line)
                # Convertir texto en negrita
                item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
                html_lines.append(f'<li>{item_text}</li>')
                continue
            
            # Líneas normales de párrafo
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            
            # Convertir texto en negrita
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            html_lines.append(f'<p>{line}</p>')
        
        # Cerrar lista si quedó abierta
        if in_list:
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
        
    except Exception as e:
        logger.error(f"Error al convertir texto a HTML: {str(e)}")
        return f'<p>{text}</p>'


def get_subject_context_info(db: Session, subject_id: int) -> Dict[str, Any]:
    """
    Obtiene información contextual de la asignatura para el análisis.
    
    Args:
        db: Sesión de SQLAlchemy
        subject_id: ID de la asignatura
        
    Returns:
        Diccionario con información contextual de la asignatura
    """
    try:
        # Obtener información de la asignatura
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return {}
        
        # Obtener documentos de la asignatura
        documents = get_subject_documents(db=db, subject_id=subject_id)
        document_info = []
        if documents:
            for doc in documents[:10]:  # Limitar a 10 documentos principales
                doc_summary = doc.summary[:150] if doc.summary else "Sin resumen disponible"
                document_info.append({
                    "title": doc.title,
                    "description": doc.description or "Sin descripción",
                    "summary": doc_summary
                })
        
        # Obtener temas de la asignatura
        topics = get_topics_by_subject(db=db, subject_id=subject_id)
        topic_info = []
        if topics:
            for topic_dict in topics[:8]:  
                topic_info.append({
                    "name": topic_dict["name"],
                    "description": topic_dict.get("description", "Sin descripción")
                })
        
        return {
            "subject_name": subject.name,
            "subject_description": subject.description or "Sin descripción",
            "subject_summary": subject.summary[:200] if subject.summary else None,
            "documents": document_info,
            "topics": topic_info,
            "total_documents": len(documents) if documents else 0,
            "total_topics": len(topics) if topics else 0
        }
        
    except Exception as e:
        logger.error(f"Error al obtener contexto de asignatura {subject_id}: {str(e)}")
        return {}


def get_student_messages_by_subject(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = 30,
    limit: Optional[int] = 100
) -> List[Dict[str, Any]]:
    """
    Obtiene los mensajes de estudiantes en una asignatura específica.
    
    Args:
        db: Sesión de SQLAlchemy
        subject_id: ID de la asignatura
        days_limit: Limitar mensajes a los últimos X días (por defecto 30)
        limit: Número máximo de mensajes a obtener (por defecto 100)
        
    Returns:
        Lista de diccionarios con información de los mensajes de estudiantes
    """
    try:
        # Query base para mensajes de estudiantes (no bot) con texto
        query = db.query(Message).filter(
            Message.is_bot == False,
            Message.text.isnot(None),
            Message.text != ""
        )
        
        # Joins necesarios
        query = query.join(Conversation, Message.conversation_id == Conversation.id)
        query = query.join(User, Conversation.user_id == User.id)
        
        # Filtrar por asignatura y rol de estudiante
        query = query.filter(
            Conversation.subject_id == subject_id,
            User.role == "student"
        )
        
        # Filtrar por fecha si se especifica
        if days_limit:
            date_threshold = datetime.utcnow() - timedelta(days=days_limit)
            query = query.filter(Message.created_at >= date_threshold)
        
        # Ordenar por fecha descendente y aplicar límite
        query = query.order_by(Message.created_at.desc())
        if limit:
            query = query.limit(limit)
        
        messages = query.all()
        
        # Formatear los resultados
        messages_data = []
        for message in messages:
            conversation = message.conversation
            user = conversation.user
            
            message_data = {
                "id": message.id,
                "text": message.text,
                "user_id": user.id,
                "user_name": user.full_name or "Usuario sin nombre",
                "user_email": user.email,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "conversation_id": conversation.id
            }
            messages_data.append(message_data)
        
        logger.info(f"Se obtuvieron {len(messages_data)} mensajes de estudiantes para la asignatura {subject_id}")
        return messages_data
        
    except Exception as e:
        logger.error(f"Error al obtener mensajes de estudiantes: {str(e)}")
        return []


def get_subject_analysis_statistics(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = 30
) -> Dict[str, Any]:
    """
    Obtiene estadísticas básicas sobre la participación de estudiantes en una asignatura.
    
    Args:
        db: Sesión de SQLAlchemy
        subject_id: ID de la asignatura
        days_limit: Limitar estadísticas a los últimos X días
        
    Returns:
        Diccionario con estadísticas de participación
    """
    try:
        # Query base
        query = db.query(Message).filter(
            Message.is_bot == False,
            Message.text.isnot(None),
            Message.text != ""
        )
        
        query = query.join(Conversation, Message.conversation_id == Conversation.id)
        query = query.join(User, Conversation.user_id == User.id)
        query = query.filter(
            Conversation.subject_id == subject_id,
            User.role == "student"
        )
        
        # Filtrar por fecha si se especifica
        if days_limit:
            date_threshold = datetime.utcnow() - timedelta(days=days_limit)
            query = query.filter(Message.created_at >= date_threshold)
        
        # Obtener estadísticas
        total_messages = query.count()
        
        # Número de estudiantes únicos que han participado
        unique_students = query.with_entities(distinct(User.id)).count()
        
        # Total de estudiantes en la asignatura
        total_students_in_subject = db.query(User).join(
            User.subjects
        ).filter(
            Subject.id == subject_id,
            User.role == "student"
        ).count()
        
        # Calcular tasa de participación
        participation_rate = (unique_students / total_students_in_subject * 100) if total_students_in_subject > 0 else 0
        
        # Promedio de mensajes por estudiante activo
        avg_messages_per_student = (total_messages / unique_students) if unique_students > 0 else 0
        
        return {
            "total_messages": total_messages,
            "unique_students": unique_students,
            "total_students_in_subject": total_students_in_subject,
            "participation_rate": round(participation_rate, 2),
            "avg_messages_per_student": round(avg_messages_per_student, 2),
            "analysis_period_days": days_limit
        }
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de análisis: {str(e)}")
        return {}


async def generate_student_analysis_summary(
    subject_id: int,
    db: Session,
    days_limit: Optional[int] = 30,
    min_participation: Optional[int] = 1
) -> Dict[str, Any]:
    """
    Genera un resumen analizando las preguntas de los estudiantes y detectando carencias.
    
    Args:
        subject_id: ID de la asignatura
        db: Sesión de SQLAlchemy
        days_limit: Limitar análisis a los últimos X días
        min_participation: Mínimo número de mensajes por estudiante para incluir en análisis
        
    Returns:
        Diccionario con análisis completo y estadísticas
    """
    try:
        # Obtener la información de la asignatura
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return None
        
        # Obtener los mensajes de estudiantes
        messages = get_student_messages_by_subject(
            db=db,
            subject_id=subject_id,
            days_limit=days_limit,
            limit=50  # Límite para el análisis
        )
        
        # Obtener información contextual de la asignatura
        context_info = get_subject_context_info(db=db, subject_id=subject_id)
        
        # Obtener estadísticas básicas incluso si no hay mensajes
        stats = get_subject_analysis_statistics(db=db, subject_id=subject_id, days_limit=days_limit)
        
        if not messages:
            # Retornar análisis básico cuando no hay mensajes
            logger.info(f"No se encontraron mensajes para la asignatura {subject.name}, generando análisis básico")
            
            # Crear contenido contextual para el análisis sin mensajes
            documents_summary = ""
            if context_info.get("documents"):
                documents_summary = f"""
<h4>Materiales Disponibles:</h4>
<ul>
{"".join([f'<li><strong>{doc["title"]}</strong>: {doc["description"]}</li>' for doc in context_info["documents"][:5]])}
</ul>
<p><em>Se recomienda revisar si los estudiantes conocen estos materiales y cómo utilizarlos.</em></p>"""
            
            topics_summary = ""
            if context_info.get("topics"):
                topics_summary = f"""
<h4>Temas de la Asignatura:</h4>
<ul>
{"".join([f'<li><strong>{topic["name"]}</strong>: {topic["description"]}</li>' for topic in context_info["topics"][:5]])}
</ul>
<p><em>Considerar crear consultas específicas sobre estos temas para incentivar la participación.</em></p>"""
            
            analysis_text = f"""<div class="analysis-content">
<h3>Análisis de Participación - {subject.name}</h3>

<h4>Resumen General:</h4>
<p>No se encontraron preguntas de estudiantes en el período de análisis de los últimos {days_limit or 'todos los'} días. Esto puede indicar:</p>

<h4>Observaciones:</h4>
<ul>
<li>Baja participación estudiantil en el chat/consultas</li>
<li>Los estudiantes pueden estar utilizando otros canales de comunicación</li>
<li>Posible necesidad de incentivar la participación digital</li>
</ul>

{documents_summary}

{topics_summary}

<h4>Recomendaciones:</h4>
<ol>
<li><strong>Fomentar la Participación:</strong> Crear actividades que incentiven el uso del chat para consultas</li>
<li><strong>Clarificar el Propósito:</strong> Asegurar que los estudiantes comprendan cómo usar la herramienta</li>
<li><strong>Establecer Horarios:</strong> Definir horarios específicos para atención de consultas</li>
<li><strong>Ejemplos de Uso:</strong> Proporcionar ejemplos de cómo realizar consultas efectivas</li>
<li><strong>Seguimiento Personalizado:</strong> Contactar directamente con estudiantes para conocer sus necesidades</li>
</ol>

<h4>Próximos Pasos:</h4>
<ul>
<li>Verificar si los estudiantes conocen la herramienta de chat</li>
<li>Considerar enviar recordatorios sobre la disponibilidad del sistema</li>
<li>Evaluar métodos alternativos para recibir consultas de estudiantes</li>
</ul>
</div>"""

            return {
                "analysis": analysis_text,
                "statistics": {
                    "total_messages": 0,
                    "unique_students": 0,
                    "participation_rate": 0.0,
                    "most_active_students": []
                },
                "sample_questions": []
            }
        
        # Obtener estadísticas
        stats = get_subject_analysis_statistics(db=db, subject_id=subject_id, days_limit=days_limit)
        
        # Obtener estudiantes más activos
        most_active_students = get_most_active_students(
            db=db, 
            subject_id=subject_id, 
            days_limit=days_limit,
            limit=5
        )
        
        # Filtrar estudiantes por participación mínima si se especifica
        if min_participation and min_participation > 1:
            most_active_students = [
                student for student in most_active_students 
                if student["message_count"] >= min_participation
            ]
        
        # Obtener preguntas de muestra
        sample_questions = get_subject_question_topics(
            db=db,
            subject_id=subject_id,
            days_limit=days_limit
        )[:10]  # Máximo 10 preguntas de muestra
        
        # Preparar el contexto para el análisis
        questions_text = "\n".join([f"- {msg['text']}" for msg in messages[:30]])
        
        # Obtener información sobre la asignatura (descripción y resumen si existe)
        subject_context = f"Asignatura: {subject.name}\n"
        if subject.description:
            subject_context += f"Descripción: {subject.description}\n"
        if subject.summary:
            subject_context += f"Contexto de la asignatura: {subject.summary}\n"
        
        # Agregar información de documentos disponibles
        documents_context = ""
        if context_info.get("documents"):
            documents_context = "DOCUMENTOS Y MATERIALES DISPONIBLES:\n"
            for doc in context_info["documents"]:
                documents_context += f"- {doc['title']}: {doc['description']}\n  Resumen: {doc['summary']}\n"
        
        # Agregar información de temas de la asignatura
        topics_context = ""
        if context_info.get("topics"):
            topics_context = "TEMAS DE LA ASIGNATURA:\n"
            for topic in context_info["topics"]:
                topics_context += f"- {topic['name']}: {topic['description']}\n"
        
        # Crear el prompt para el análisis
        prompt = f"""Analiza las siguientes preguntas de estudiantes y genera un resumen ejecutivo profesional que incluya referencias específicas a los materiales y temas de la asignatura.

CONTEXTO DE LA ASIGNATURA:
{subject_context}

{documents_context}

{topics_context}

ESTADÍSTICAS:
- Preguntas analizadas: {len(messages)}
- Estudiantes participantes: {stats.get('unique_students', 0)}
- Total estudiantes: {stats.get('total_students_in_subject', 0)}
- Participación: {stats.get('participation_rate', 0)}%
- Período: últimos {days_limit or 'todos los'} días

PREGUNTAS DE ESTUDIANTES:
{questions_text}

GENERA UN ANÁLISIS CON LAS SIGUIENTES SECCIONES:

1. Resumen General
2. Carencias Detectadas (especifica qué documentos o temas específicos requieren mayor atención)
3. Patrones Comunes (relaciona las preguntas con los materiales y temas disponibles)
4. Nivel de Comprensión (identifica qué temas de los documentos causan más dificultades)
5. Recomendaciones (incluye sugerencias específicas sobre qué materiales revisar o enfatizar)

IMPORTANTE: 
- Haz referencias específicas a los documentos y temas cuando sea relevante
- Identifica si las preguntas están relacionadas con materiales específicos
- Sugiere qué documentos o temas necesitan mayor énfasis
- Responde SOLO con texto plano, SIN formato markdown, SIN etiquetas HTML, SIN caracteres especiales como ``` o **
- Usa títulos simples seguidos de dos puntos y párrafos normales
- Máximo 500 palabras

Ejemplo del formato esperado:
Resumen General:
Descripción de la participación y tipos de preguntas relacionadas con [documento específico]...

Carencias Detectadas:
Los estudiantes muestran dificultades con [tema específico] del documento [nombre del documento]...
"""

        # Generar el análisis usando IA
        analysis_text_raw = generate_google_ai_simple(prompt)
        
        # Limpiar y formatear el texto del análisis
        analysis_text = clean_and_format_analysis_text(analysis_text_raw, subject.name)
        
        # Preparar las estadísticas con estudiantes más activos
        statistics = {
            "total_messages": stats.get("total_messages", 0),
            "unique_students": stats.get("unique_students", 0),
            "participation_rate": stats.get("participation_rate", 0) / 100,  # Convertir a decimal
            "most_active_students": [
                {
                    "student_id": student["user_id"],
                    "student_name": student["name"],
                    "message_count": student["message_count"]
                }
                for student in most_active_students
            ]
        }
        
        # Preparar la respuesta estructurada
        result = {
            "analysis": analysis_text.strip(),
            "statistics": statistics,
            "sample_questions": sample_questions
        }
        
        logger.info(f"Análisis generado exitosamente para la asignatura {subject.name}")
        return result
        
    except Exception as e:
        logger.error(f"Error al generar análisis de estudiantes: {str(e)}")
        return None


def get_most_active_students(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = 30,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Obtiene los estudiantes más activos en una asignatura por número de preguntas.
    
    Args:
        db: Sesión de SQLAlchemy
        subject_id: ID de la asignatura
        days_limit: Limitar a los últimos X días
        limit: Número máximo de estudiantes a retornar
        
    Returns:
        Lista de estudiantes ordenados por actividad
    """
    try:
        query = db.query(
            User.id,
            User.full_name,
            User.email,
            func.count(Message.id).label('message_count')
        ).select_from(User)
        
        query = query.join(Conversation, User.id == Conversation.user_id)
        query = query.join(Message, Conversation.id == Message.conversation_id)
        
        query = query.filter(
            Conversation.subject_id == subject_id,
            User.role == "student",
            Message.is_bot == False,
            Message.text.isnot(None),
            Message.text != ""
        )
        
        # Filtrar por fecha si se especifica
        if days_limit:
            date_threshold = datetime.utcnow() - timedelta(days=days_limit)
            query = query.filter(Message.created_at >= date_threshold)
        
        # Agrupar y ordenar
        query = query.group_by(User.id, User.full_name, User.email)
        query = query.order_by(func.count(Message.id).desc())
        query = query.limit(limit)
        
        results = query.all()
        
        students = []
        for result in results:
            students.append({
                "user_id": result.id,
                "name": result.full_name or "Usuario sin nombre",
                "email": result.email,
                "message_count": result.message_count
            })
        
        return students
        
    except Exception as e:
        logger.error(f"Error al obtener estudiantes más activos: {str(e)}")
        return []


def get_subject_question_topics(
    db: Session,
    subject_id: int,
    days_limit: Optional[int] = 30
) -> List[str]:
    """
    Extrae una muestra de preguntas para identificar temas comunes.
    
    Args:
        db: Sesión de SQLAlchemy
        subject_id: ID de la asignatura
        days_limit: Limitar a los últimos X días
        
    Returns:
        Lista de preguntas representativas
    """
    try:
        messages = get_student_messages_by_subject(
            db=db,
            subject_id=subject_id,
            days_limit=days_limit,
            limit=20  # Muestra representativa
        )
        
        return [msg['text'] for msg in messages if len(msg['text']) > 10]  # Filtrar preguntas muy cortas
        
    except Exception as e:
        logger.error(f"Error al obtener temas de preguntas: {str(e)}")
        return []
