import os
from groq import Groq

def get_groq_client():
    """
    Inicializa y devuelve una instancia del cliente Groq.
    """

    return Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
