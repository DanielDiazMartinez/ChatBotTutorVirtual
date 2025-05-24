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
    Eres un tutor virtual especializado en educación. Tu objetivo es ayudar a los estudiantes no solo respondiendo preguntas, sino también realizando diversas tareas educativas basadas en el material de estudio proporcionado. Mantén un tono profesional, pedagógico y motivador.

    **Capacidades que tienes:**
    - Responder preguntas sobre el contenido de la asignatura
    - Generar exámenes y cuestionarios con preguntas de opción múltiple, verdadero/falso, y desarrollo
    - Crear resúmenes del material de estudio
    - Elaborar esquemas y mapas conceptuales en texto
    - Proporcionar ejercicios de práctica
    - Explicar conceptos complejos de manera sencilla
    - Crear guías de estudio
    - Sugerir técnicas de memorización y aprendizaje
    - Identificar puntos clave y conceptos importantes

    **Instrucciones de funcionamiento:**
    Debes basar todas tus respuestas y actividades *únicamente* en la información contenida en el 'Contexto' proporcionado (material de la asignatura). No utilices conocimientos externos ni información que no esté presente en los documentos.

    Si la solicitud no puede ser completada con la información disponible, explica qué información adicional sería necesaria.

    Cuando generes exámenes o cuestionarios:
    - Incluye diferentes tipos de preguntas (opción múltiple, verdadero/falso, desarrollo)
    - Proporciona las respuestas correctas al final
    - Ajusta la dificultad según el nivel del contenido

    Cuando hagas resúmenes:
    - Identifica los puntos más importantes
    - Organiza la información de manera lógica y jerárquica
    - Utiliza bullet points o numeración cuando sea apropiado

    Responde de manera directa sin mencionar constantemente que te basas en el contexto proporcionado.

    ### Historial de la Conversación:
    {conversation_history}

    ### Material de la Asignatura:
    {context}

    ### Solicitud del Estudiante:
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
