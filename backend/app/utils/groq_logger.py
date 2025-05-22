"""
Servicio de logging para Groq - Capa utilitaria
Este servicio maneja el registro de las interacciones con la API de Groq.
"""
import os
import logging
import json
from datetime import datetime
from pathlib import Path

# Configuración de logging específico para contextos de Groq
logger = logging.getLogger("groq_context_logger")
logger.setLevel(logging.INFO)

# Crear directorio de logs si no existe
LOGS_DIR = Path("/home/dani/Proyectos/ChatBotTutorVirtual/backend/logs/chat/groq_contexts")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Obtener la ruta absoluta del directorio de logs
log_path = LOGS_DIR.resolve()

def setup_file_handler():
    """Configura un manejador de archivos para el logger de contextos de Groq."""
    # Crear un nuevo archivo de log cada día
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"groq_context_{current_date}.log"
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Formato simple para los logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Añadir el handler al logger
    logger.addHandler(file_handler)
    
    return file_handler

# Configurar el handler de archivo
file_handler = setup_file_handler()

def log_groq_context(user_id: str, conversation_id: int, user_question: str, context: str, conversation_history: str = "", prompt: str = None):
    """
    Registra el contexto completo enviado a la API de Groq.
    
    Args:
        user_id: ID del usuario que realiza la consulta
        conversation_id: ID de la conversación
        user_question: Pregunta realizada por el usuario
        context: Contexto extraído de los documentos
        conversation_history: Historial de la conversación
        prompt: Prompt completo enviado a Groq (opcional)
    """
    try:
        # Crear un directorio específico para la fecha actual
        current_date = datetime.now().strftime("%Y-%m-%d")
        daily_dir = log_path / current_date
        daily_dir.mkdir(exist_ok=True)
        
        # Crear un nombre de archivo único basado en timestamp y conversation_id
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"groq_context_{timestamp}_{conversation_id}.json"
        file_path = daily_dir / filename
        
        # Crear objeto con toda la información
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "conversation_id": conversation_id,
            "user_question": user_question,
            "context": context,
            "conversation_history": conversation_history,
            "prompt": prompt,
            "stats": {
                "context_length": len(context) if context else 0,
                "context_tokens": len(context.split()) if context else 0,
                "question_length": len(user_question) if user_question else 0,
                "question_tokens": len(user_question.split()) if user_question else 0,
                "history_length": len(conversation_history) if conversation_history else 0,
                "history_tokens": len(conversation_history.split()) if conversation_history else 0,
                "prompt_length": len(prompt) if prompt else 0,
                "prompt_tokens": len(prompt.split()) if prompt else 0
            }
        }
        
        # Guardar como JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        # Registrar en el log que se ha guardado el contexto
        logger.info(f"Guardado contexto para conversación {conversation_id} en {filename}")
        
        return True
    except Exception as e:
        logger.error(f"Error al guardar el contexto: {str(e)}")
        return False
