import logging # 1. Importar logging
import sys # 2. Importar sys para dirigir el output

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router


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
    "http://localhost:5050",  # pgAdmin
    "http://127.0.0.1:5050"
    
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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Puedes añadir un log al iniciar la app para confirmar que el logging funciona
logging.info("Aplicación FastAPI iniciada")