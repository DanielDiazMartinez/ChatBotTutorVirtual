from ..core.config import settings
import requests

def generate_groq_response(question_text: str, context: str) -> str:
    prompt = f"""
    Eres un profesor virtual que responde preguntas de estudiantes sobre documentos específicos.
    
    INSTRUCCIONES IMPORTANTES:
    - Basa tu respuesta ÚNICAMENTE en el contexto proporcionado, no en tu conocimiento general.
    - Si la respuesta no está en el contexto, di "No encuentro información sobre esto en el documento."
    - No inventes información que no esté en el contexto.
    - Cita partes específicas del documento cuando sea relevante.
    
    CONTEXTO DEL DOCUMENTO:
    {context}
    
    PREGUNTA DEL ESTUDIANTE:
    {question_text}
    
    RESPUESTA (basada únicamente en el contexto):
    """

    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "groq-ai/groq-chatbot",
        "messages": [{"role": "system", "content": prompt}]
    }

    response = requests.post("https://api.groq.com/v1/chat/completions", json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Lo siento, no puedo responder en este momento."