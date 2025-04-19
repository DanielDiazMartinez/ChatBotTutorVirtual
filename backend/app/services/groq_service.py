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


def generate_groq_response(user_question: str, context: str) -> str:
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

    prompt = f"""Basándote *únicamente* en el siguiente contexto, responde la pregunta del usuario. Si la respuesta no se encuentra en el contexto, di "Lo siento, no encuentro esa información en el documento.". No inventes información.

Contexto:
{context}

Pregunta del usuario: {user_question}

Respuesta:"""

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