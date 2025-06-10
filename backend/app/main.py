import logging # 1. Importar logging
import sys # 2. Importar sys para dirigir el output

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router
from app.services.embedding_service import load_sentence_transformer_model_singleton


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) 
    ]
)
# ------------------------------------------

# Crear la instancia de la app DESPUÉS de configurar el logging
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Ampliar los origins permitidos
origins = [
    "http://localhost:8000",  # FastAPI
    "http://127.0.0.1:8000",  
    "http://127.0.0.1:5050",
    "http://localhost:4200",  # Angular dev server
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Añadir el router con prefix
app.include_router(api_router, prefix="/api/v1")

# Precargar el modelo de embedding al inicio
@app.on_event("startup")
async def startup_event():
    """Precargar modelos y configuraciones necesarias al iniciar la aplicación"""
    logging.info("Iniciando precarga de modelos...")
    try:
        # Precargar el modelo de embedding para acelerar el primer mensaje
        model = load_sentence_transformer_model_singleton()
        logging.info(f"Modelo de embedding precargado exitosamente: {type(model).__name__}")
    except Exception as e:
        logging.error(f"Error al precargar el modelo de embedding: {e}")
        # No falla la aplicación, solo registra el error
    logging.info("Precarga de modelos completada")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/warmup")
async def warmup_models():
    """Endpoint para calentar los modelos del sistema"""
    try:
        from app.services.embedding_service import get_embedding_for_query
        
        # Generar un embedding de prueba para asegurar que el modelo esté cargado
        test_embedding = get_embedding_for_query("test")
        
        return {
            "status": "success",
            "message": "Modelos calentados exitosamente",
            "embedding_dimensions": len(test_embedding) if test_embedding else 0
        }
    except Exception as e:
        logging.error(f"Error durante warmup: {e}")
        return {
            "status": "error", 
            "message": f"Error durante warmup: {str(e)}"
        }

# Puedes añadir un log al iniciar la app para confirmar que el logging funciona
logging.info("Aplicación FastAPI iniciada con precarga de modelos")