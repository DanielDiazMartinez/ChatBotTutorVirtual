from ..core.config import settings
import requests

def generate_groq_response(question_text: str, context: str) -> str:
    """
    Usa Groq para generar una respuesta basada en contexto.
    """
    prompt = f"Contexto relevante: {context}\nPregunta del estudiante: {question_text}\nRespuesta del profesor virtual:"

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
