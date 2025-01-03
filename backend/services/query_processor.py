
from groq_config import get_groq_client

def procesar_resultados(resultados):
    
    if not resultados["matches"]:
        raise ValueError("No se encontraron coincidencias en los resultados.")

    textos_relevantes = [
        match["metadata"].get("contenido", "No hay contenido disponible")
        for match in resultados["matches"]
    ]
    return " ".join(textos_relevantes)


def generar_respuesta(pregunta, contexto):
    """
    Genera una respuesta utilizando el cliente Groq.
    """
    client = get_groq_client()
    print(f"Contexto: {contexto}")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "Debes responder exclusivamente con información"
                    "que esté incluida en el contexto proporcionado. Si la pregunta no puede "
                    "ser respondida con la información del contexto, indica claramente: "
                    "'La información proporcionada no es suficiente para responder la pregunta.'"
                ),
            },
            {"role": "user", "content": f"Contexto: {contexto}"},
            {"role": "user", "content": f"Pregunta: {pregunta}"}
        ],
        model="llama-3.3-70b-versatile",
    )
 
    return chat_completion.choices[0].message.content