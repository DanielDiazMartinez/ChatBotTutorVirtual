import requests
import os

API_URL = "https://api.groq.com/endpoint"
API_KEY = os.getenv("API_KEY")

def llamar_api_groq():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Error al contactar con Groq"}
