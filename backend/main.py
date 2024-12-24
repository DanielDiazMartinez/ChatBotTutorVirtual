from fastapi import FastAPI
from routes import groq_routes

app = FastAPI()

# Incluir rutas
app.include_router(groq_routes.router)

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}
from fastapi import FastAPI
from routes import groq_routes

app = FastAPI()

# Incluir rutas
app.include_router(groq_routes.router)

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
