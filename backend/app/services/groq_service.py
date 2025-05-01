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


def generate_groq_response(user_question: str, document_context: str, conversation_history: str) -> str:
    """
    Genera una respuesta utilizando la API de Groq basada en la pregunta del usuario,
    el contexto del documento y el historial de la conversación.

    Args:
        user_question: La pregunta realizada por el usuario.
        document_context: El contexto extraído de los documentos relevantes para la pregunta actual.
        conversation_history: Una cadena que representa el historial de la conversación (p.ej., turnos user/assistant).

    Returns:
        La respuesta generada por el modelo de Groq.
    """
    if client is None:
        print("--- ERROR: generate_groq_response called but Groq client is not valid! ---")
        return "Lo siento, la configuración del servicio de IA no es correcta."



    prompt = f"""Eres un asistente que responde preguntas. Sigue estas reglas estrictamente:

1.  **Prioridad al Documento:** Tu objetivo principal es responder la `Pregunta del usuario` basándote PRIMERO y PRINCIPALMENTE en la información contenida en el `Contexto del Documento`. Si la respuesta se encuentra ahí, basa tu respuesta *solo* en ese contexto.
2.  **Considera la Conversación:** Si la `Pregunta del usuario` parece referirse a información o temas tratados previamente en el `Historial de Conversación` (por ejemplo, usa pronombres como "eso", "él", "ella", o pregunta sobre algo discutido antes) Y la respuesta *no* está claramente en el `Contexto del Documento` actual, entonces puedes usar el `Historial de Conversación` para entender la pregunta y responderla.
3.  **Respuesta Específica si no hay Información:** Si la respuesta a la `Pregunta del usuario` NO se encuentra en el `Contexto del Documento` Y TAMPOCO es una pregunta que pueda responderse razonablemente usando el `Historial de Conversación`, responde EXACTAMENTE: "Lo siento, no encuentro información sobre eso en el documento ni en nuestra conversación reciente."
4.  **No Inventes:** No añadas información que no provenga del `Contexto del Documento` o del `Historial de Conversación`. No utilices conocimiento externo.

---
Historial de Conversación:
'''
{conversation_history}
'''
---
Contexto del Documento:
'''
{document_context}
'''
---
Pregunta del usuario: {user_question}
---
Respuesta:"""
   

    print(f"--- Debug Info: Preparing to call Groq API (client seems valid) ---")
    print(f"Model Used: {settings.GROQ_MODEL_NAME}")

    print(f"Prompt (first 500 chars): {prompt[:500]}")
    if len(prompt) > 500: print("...") 

    try:
        print("--- Debug Info: Executing client.chat.completions.create(...) ---")
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL_NAME,
            messages=[
                {
                    "role": "system", # Usar rol "system" para las instrucciones puede ser beneficioso
                    "content": prompt, # El prompt completo ahora actúa como instrucción de sistema
                }
        
            ],
            temperature=0.7, # Puedes ajustar esto según necesites más creatividad o más precisión
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        print("--- Debug Info: client.chat.completions.create(...) FINISHED ---")

        print(f"--- Debug Info: Groq API Raw Completion Object ---")

        if completion.choices:
            response_content = completion.choices[0].message.content
            print(f"--- Debug Info: Groq Response Content ---")
            print(response_content)
            #
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
