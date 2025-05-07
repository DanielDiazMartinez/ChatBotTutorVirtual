# app/services/groq_service.py

import os
from groq import Groq, GroqError  # Asegúrate de importar GroqError
from app.core.config import settings

api_key = settings.GROQ_API_KEY


client: Groq | None = None # Inicializa client a None

if not api_key:
    print("--- FATAL ERROR: GROQ_API_KEY is missing or empty. Cannot create Groq client. ---")
    
else:
    try:
        print("--- Debug Info: Attempting to create Groq client ---")
        client = Groq(api_key=api_key)
        print("--- Debug Info: Groq client CREATED successfully ---")
    except Exception as e:
        print(f"--- FATAL ERROR: Failed to create Groq client: {type(e).__name__} - {e} ---")
        client = None 


def generate_groq_response(user_question: str, context: str,conversation_history: str) -> str:
    """
    Genera una respuesta utilizando la API de Groq basada en la pregunta del usuario y el contexto proporcionado.

    Args:
        user_question: La pregunta realizada por el usuario.
        context: El contexto extraído de los documentos relevantes.

    Returns:
        La respuesta generada por el modelo de Groq.
    """
   
    if client is None:
        print("--- ERROR: generate_groq_response called but Groq client is not valid! ---")
        return "Lo siento, la configuración del servicio de IA no es correcta."
    # ---------------
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

    print(f"--- Debug Info: Preparing to call Groq API (client seems valid) ---")
 
    print(f"Model Used: {settings.GROQ_MODEL_NAME}")
    print(f"Prompt (first 500 chars): {prompt[:500]}") 
 
    try:
        print("--- Debug Info: Executing client.chat.completions.create(...) ---") 
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
        print("--- Debug Info: client.chat.completions.create(...) FINISHED ---") # Justo después
        
    
        print(f"--- Debug Info: Groq API Raw Completion Object ---")
        print(completion)
        # ---------------

        if completion.choices:
            response_content = completion.choices[0].message.content
            print(f"--- Debug Info: Groq Response Content ---")
            print(response_content)
            return response_content.strip() 
        else:
          
            print("--- WARNING: Groq response tuvo 0 choices. ---")
           
            if hasattr(completion, 'usage') and completion.usage:
                 print(f"Usage info: {completion.usage}")
            return "Lo siento, no recibí una respuesta válida del modelo de IA."

    except GroqError as e:
        
        print(f"--- ERROR: Groq API Error (call was attempted) ---")
        print(f"Status Code: {e.status_code}")
       
        if hasattr(e, 'type'): print(f"Error Type: {e.type}")
        if hasattr(e, 'code'): print(f"Error Code: {e.code}")
        print(f"Error Message: {e.message}")
       
        return f"Lo siento, hubo un error con la API de Groq ({e.status_code}): {e.message}"
    except Exception as e:
       
        print(f"--- ERROR: Unexpected error DURING Groq call: {type(e).__name__} - {e} ---")
      
        return "Lo siento, ocurrió un error inesperado al procesar la solicitud de IA."