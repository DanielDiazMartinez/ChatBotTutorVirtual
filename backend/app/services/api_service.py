"""
Servicio de API - Capa superior
Este servicio maneja las interacciones con APIs externas como Groq.
Puede depender de cualquier servicio de las capas inferiores.
"""
import os
from groq import Groq, GroqError
from app.core.config import settings
import logging
from app.utils.groq_logger import log_groq_context

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicialización del cliente Groq
api_key = settings.GROQ_API_KEY
client = None

if not api_key:
    logger.error("FATAL ERROR: GROQ_API_KEY is missing or empty. Cannot create Groq client.")
else:
    try:
        logger.info("Attempting to create Groq client")
        client = Groq(api_key=api_key)
        logger.info("Groq client CREATED successfully")
    except Exception as e:
        logger.error(f"FATAL ERROR: Failed to create Groq client: {type(e).__name__} - {e}")
        client = None

def generate_ai_response(user_question: str, context: str, conversation_history: str = "", 
                      user_id: str = "unknown", conversation_id: int = None) -> str:
    """
    Genera una respuesta utilizando la API de Groq basada en la pregunta del usuario y el contexto proporcionado.

    Args:
        user_question: La pregunta realizada por el usuario.
        context: El contexto extraído de los documentos relevantes.
        conversation_history: El historial de la conversación (opcional).
        user_id: ID del usuario que realiza la consulta (opcional).
        conversation_id: ID de la conversación (opcional).

    Returns:
        La respuesta generada por el modelo de Groq.
    """
    if client is None:
        logger.error("ERROR: generate_ai_response called but Groq client is not valid!")
        return "Lo siento, la configuración del servicio de IA no es correcta."
        
    # Log de depuración - verificamos si context es None o vacío
    if context is None:
        logger.warning("Context is None en generate_ai_response")
        context = ""
    elif not context.strip():
        logger.warning("Context está vacío en generate_ai_response")
        
    # Log del tamaño del contexto
    logger.info(f"Tamaño del contexto en generar_ai_response: {len(context)} caracteres")
    
    # Verifica si hay chunks en el contexto 
    if len(context) < 10:
        logger.warning(f"¡ALERTA! Contexto muy pequeño o vacío: '{context}'")

    prompt = f"""
    ### Instrucciones:
    Eres un asistente útil y preciso. Tu objetivo es responder a las preguntas del estudiante de la manera más completa y concisa posible, utilizando la información proporcionada en el contexto. Mantén un tono profesional y objetivo.
    Debes basar tu respuesta *únicamente* en la información contenida en el 'Contexto' proporcionado. No utilices conocimientos externos ni información previa. Si la respuesta a la pregunta no se encuentra explícitamente en el contexto, responde con: 'Lo siento, no puedo responder a esa pregunta basándome en la información proporcionada.'
    Si la pregunta del estudiante es ambigua, intenta aclararla basándote en el historial de la conversación. Si la pregunta requiere inferencia, pero la inferencia se puede realizar de manera clara y directa a partir del contexto, hazlo. Sin embargo, no hagas suposiciones ni añadas información que no esté presente en el contexto. Al responder no es necesario que indiques "Segun el contexto" o "Según la información proporcionada". Simplemente responde a la pregunta de manera directa y clara.

    ### Historial de la Conversación:
    {conversation_history}

    ### Contexto:
    {context}

    ### Pregunta del Estudiante:
    {user_question}

    ### Respuesta:
    """
    
    # Registrar el contexto completo enviado a Groq
    try:
        if conversation_id:
            log_groq_context(
                user_id=user_id, 
                conversation_id=conversation_id, 
                user_question=user_question, 
                context=context, 
                conversation_history=conversation_history, 
                prompt=prompt
            )
            logger.info(f"Contexto de Groq registrado para conversación {conversation_id}")
    except Exception as log_error:
        logger.error(f"Error al registrar contexto de Groq: {str(log_error)}")
        logger.error(f"Detalles: user_id={user_id}, conversation_id={conversation_id}, context_len={len(context) if context else 0}")

    logger.info(f"Preparing to call Groq API using model: {settings.GROQ_MODEL_NAME}")
    
    try:
        logger.info("Executing Groq API call")
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL_NAME, 
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.7, 
            max_tokens=1024, 
            top_p=1,         
            stream=False,    
            stop=None,       
        )
        logger.info("Groq API call completed successfully")
        
        if completion.choices:
            response_content = completion.choices[0].message.content
            logger.info("Successfully extracted response content from Groq API")
            return response_content.strip() 
        else:
            logger.warning("WARNING: Groq response had 0 choices.")
            if hasattr(completion, 'usage') and completion.usage:
                logger.info(f"Usage info: {completion.usage}")
            return "Lo siento, no recibí una respuesta válida del modelo de IA."

    except GroqError as e:
        logger.error(f"Groq API Error - Status Code: {e.status_code}")
        if hasattr(e, 'type'): logger.error(f"Error Type: {e.type}")
        if hasattr(e, 'code'): logger.error(f"Error Code: {e.code}")
        logger.error(f"Error Message: {e.message}")
        return f"Lo siento, hubo un error con la API de Groq ({e.status_code}): {e.message}"
    except Exception as e:
        logger.error(f"Unexpected error during Groq call: {type(e).__name__} - {e}")
        return "Lo siento, ocurrió un error inesperado al procesar la solicitud de IA."
