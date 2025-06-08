"""
Servicio de logging para Google AI - Capa utilitaria
Este servicio maneja el registro de las interacciones con la API de Google AI.
"""
import os
import logging
import json
import traceback
from datetime import datetime
from pathlib import Path

# Configuración de logging específico para contextos de Google AI
logger = logging.getLogger("google_ai_context_logger")
logger.setLevel(logging.INFO)

# Determinar la ruta base del proyecto
# Si estamos en Docker, usa /app, si no, usa la ruta relativa
if os.path.exists("/app"):
    BASE_DIR = Path("/app")
else:
    # Obtener la ruta del directorio actual y navegar hacia arriba hasta la raíz del proyecto
    BASE_DIR = Path(__file__).parent.parent.parent

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / "logs" / "chat" / "google_ai_contexts"
try:
    # Asegurar que toda la estructura de directorios existe
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Intentar cambiar los permisos, pero no fallar si no se puede
    try:
        os.chmod(str(LOGS_DIR), 0o777)  # Asegurar permisos completos
    except PermissionError:
        print(f"Aviso: No se pudieron cambiar los permisos del directorio {LOGS_DIR}")
    
    print(f"Directorio de logs creado en: {LOGS_DIR}")
except Exception as e:
    print(f"Error al crear directorio de logs: {str(e)}")

# Obtener la ruta absoluta del directorio de logs
log_path = LOGS_DIR.resolve()

def setup_file_handler():
    """Configura un manejador de archivos para el logger de contextos de Google AI."""
    # Crear un nuevo archivo de log cada día
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"google_ai_context_{current_date}.log"
    
    # Asegurar que el archivo existe
    with open(log_file, "a") as f:
        f.write(f"\n--- Sesión iniciada {datetime.now().isoformat()} ---\n")
    
    # Intentar cambiar los permisos, pero no fallar si no se puede
    try:
        os.chmod(str(log_file), 0o666)
    except PermissionError:
        print(f"Aviso: No se pudieron cambiar los permisos del archivo de log {log_file}")
    
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

def log_google_context(user_id: str, conversation_id: int, user_question: str, context: str, conversation_history: str = "", prompt: str = None):
    """
    Registra el contexto completo enviado a la API de Google AI.
    
    Args:
        user_id: ID del usuario que realiza la consulta
        conversation_id: ID de la conversación
        user_question: Pregunta realizada por el usuario
        context: Contexto extraído de los documentos
        conversation_history: Historial de la conversación
        prompt: Prompt completo enviado a Google AI (opcional)
    """
    try:
        # Crear un directorio específico para la fecha actual
        current_date = datetime.now().strftime("%Y-%m-%d")
        daily_dir = log_path / current_date
        
        # Asegurar que el directorio diario existe con permisos adecuados
        print(f"Creando directorio diario: {daily_dir}")
        daily_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(str(daily_dir), 0o777)  # Dar permisos amplios para debug
        
        # Crear un nombre de archivo único basado en timestamp y conversation_id
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"google_ai_context_{timestamp}_{conversation_id}.json"
        file_path = str(daily_dir / filename)
        
        # Registrar información de depuración
        print(f"Guardando en: {file_path}")
        logger.info(f"Intentando guardar en: {file_path}")
        logger.info(f"Directorio diario: {daily_dir}, existe: {os.path.exists(str(daily_dir))}")
        
        # También escribir directamente en el archivo de log general
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = log_path / f"google_ai_context_{current_date}.log"
        with open(str(log_file), 'a', encoding='utf-8') as f:
            f.write(f"\n=== CONTEXTO ENVIADO A GOOGLE AI ({datetime.now().isoformat()}) ===\n")
            f.write(f"Conversación ID: {conversation_id}, Usuario ID: {user_id}\n")
            f.write(f"Pregunta: {user_question}\n\n")
            f.write(f"Contexto completo:\n{context}\n\n")
            f.write(f"Historial de conversación:\n{conversation_history}\n\n")
            f.write("=" * 80 + "\n\n")
            f.flush()
            os.fsync(f.fileno())
        
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
            f.flush()
            os.fsync(f.fileno())  # Asegurar que se escriba a disco
        
        # También dar permisos al archivo
        os.chmod(file_path, 0o666)
        
        # Registrar en el log que se ha guardado el contexto
        logger.info(f"Guardado contexto para conversación {conversation_id} en {file_path}")
        
        # También escribir directamente a un archivo de texto simple para debug
        debug_log_path = str(log_path / "debug_log.txt")
        with open(debug_log_path, 'a', encoding='utf-8') as debug_file:
            debug_file.write(f"{datetime.now().isoformat()} - Guardado contexto para conversación {conversation_id} en {file_path}\n")
            debug_file.flush()
            os.fsync(debug_file.fileno())
        
        return True
    except Exception as e:
        # Inicializar daily_dir en caso de que la excepción ocurra antes de su creación
        daily_dir = None
        try:
            # Intentar obtener la estructura de directorios
            current_date = datetime.now().strftime("%Y-%m-%d")
            daily_dir = log_path / current_date
        except:
            pass
            
        # Escribir directamente a un archivo para debug
        try:
            error_log_path = str(log_path / "error_log.txt")
            with open(error_log_path, 'a', encoding='utf-8') as error_file:
                error_file.write(f"{datetime.now().isoformat()} - Error: {str(e)}\n")
                error_file.write(f"Detalles: Tipo={type(e).__name__}, Path={log_path}\n")
                error_file.write(f"Traceback: {traceback.format_exc()}\n\n")
                error_file.flush()
                os.fsync(error_file.fileno())
        except Exception as log_error:
            print(f"No se pudo escribir al archivo de errores: {str(log_error)}")
            
        # Intentar registrar el error mediante el logger
        logger.error(f"Error al guardar el contexto: {str(e)}")
        logger.error(f"Detalles del error: Tipo={type(e).__name__}, Path={log_path}, Daily={daily_dir}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
