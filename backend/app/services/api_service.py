"""
Servicio de API - Capa superior
Este servicio maneja las interacciones con APIs externas como Groq y Google AI.
Puede depender de cualquier servicio de las capas inferiores.
"""
import os
from typing import Optional
from groq import Groq, GroqError
import google.generativeai as genai
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

# Inicialización del cliente Google AI
google_client = None
if settings.GOOGLE_AI_API_KEY:
    try:
        logger.info("Configurando Google AI Studio client")
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        google_client = genai.GenerativeModel(settings.GOOGLE_AI_MODEL_NAME)
        logger.info("Google AI Studio client configurado exitosamente")
    except Exception as e:
        logger.error(f"Error configurando Google AI Studio client: {type(e).__name__} - {e}")
        google_client = None
else:
    logger.warning("GOOGLE_AI_API_KEY no configurada. Cliente Google AI no disponible.")

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

def generate_google_ai_response(
    user_question: str,
    context: str,
    conversation_history: str = "",
    image_base64: Optional[str] = None,  
    image_mime_type: Optional[str] = None,  
    asignatura: Optional[str] = None,
    user_id: str = "unknown",
    conversation_id: int = None
) -> str:
    """
    Genera una respuesta utilizando la API de Google AI Studio (Gemma3) basada en la pregunta
    del usuario, el contexto proporcionado y, opcionalmente, una imagen.

    Args:
        user_question: La pregunta realizada por el usuario.
        context: El contexto extraído de los documentos relevantes.
        conversation_history: El historial de la conversación (opcional).
        image_base64: La imagen codificada en base64 (opcional).
        image_mime_type: El tipo MIME de la imagen (ej: image/jpeg) (opcional).
        asignatura: La asignatura asociada a la conversación o imagen (opcional).
        user_id: ID del usuario que realiza la consulta (opcional).
        conversation_id: ID de la conversación (opcional).

    Returns:
        La respuesta generada por el modelo de Google AI Studio.
    """
    if google_client is None:
        logger.error("ERROR: generate_google_ai_response llamado pero el cliente de Google AI no es válido!")
        return "Lo siento, la configuración del servicio de IA no es correcta."

    # Log de depuración del contexto
    if context is None:
        logger.warning("Contexto es None en generate_google_ai_response")
        context = ""
    elif not context.strip():
        logger.warning("Contexto está vacío en generate_google_ai_response")
    logger.info(f"Tamaño del contexto en generate_google_ai_response: {len(context)} caracteres")

    # Construcción del prompt basado en si hay imagen o no
    prompt = ""
    if image_base64 and image_mime_type:
        # Caso con imagen
        if user_question and user_question.strip():
            if asignatura:
                prompt = f"""
                ### Instrucciones:
                Eres un tutor virtual especializado en educación de la asignatura de {asignatura}. Analiza la siguiente imagen en relación con la pregunta del estudiante: '{user_question}'. Basándote en el contexto proporcionado y la imagen, proporciona una respuesta clara, concisa y pedagógica.

                **Contexto de la Asignatura:**
                {context}

                ### Respuesta:
                """
            else:
                prompt = f"""
                ### Instrucciones:
                Analiza la siguiente imagen en relación con la pregunta del estudiante: '{user_question}'. Basándote en el contexto proporcionado y la imagen, proporciona una respuesta clara y concisa.

                **Contexto:**
                {context}

                ### Respuesta:
                """
        else:
            # Imagen sin pregunta directa - caso de profesor o análisis general
            if asignatura:
                prompt = f"""
                ### Instrucciones:
                Eres un tutor virtual especializado en educación de la asignatura de {asignatura}. Describe y analiza el contenido de la siguiente imagen en el contexto de la asignatura. Identifica los elementos clave y explica su posible relevancia educativa.

                **Contexto de la Asignatura:**
                {context}

                ### Respuesta:
                """
            else:
                prompt = f"""
                ### Instrucciones:
                Describe y analiza el contenido de la siguiente imagen. Identifica los elementos clave y proporciona una explicación concisa.

                **Contexto:**
                {context}

                ### Respuesta:
                """
    else:
        # Caso solo con texto (tu prompt original)
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
    
    # Registrar el contexto completo enviado a Google AI
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
            logger.info(f"Contexto de Google AI registrado para conversación {conversation_id}")
    except Exception as log_error:
        logger.error(f"Error al registrar contexto de Google AI: {str(log_error)}")
        logger.error(f"Detalles: user_id={user_id}, conversation_id={conversation_id}, context_len={len(context) if context else 0}")

    logger.info(f"Preparando llamada a Google AI API con modelo: {settings.GOOGLE_AI_MODEL_NAME}")

    try:
        logger.info("Ejecutando llamada a Google AI API")
        content_parts = []
        if image_base64 and image_mime_type:
            image_part = {"mime_type": image_mime_type, "data": image_base64}
            content_parts.append(image_part)
        content_parts.append(prompt)

        response = google_client.generate_content(content_parts)

        if hasattr(response, "text") and response.text:
            logger.info("Respuesta de Google AI API recibida correctamente")
            return response.text.strip()
        else:
            logger.warning("ADVERTENCIA: La respuesta de Google AI API no contiene texto.")
            return "Lo siento, no recibí una respuesta válida del modelo de IA para la imagen."

    except Exception as e:
        logger.error(f"Error inesperado durante llamada a Google AI: {type(e).__name__} - {e}")
        return "Lo siento, ocurrió un error inesperado al procesar la solicitud de IA con la imagen."
