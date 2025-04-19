from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router

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
    expose_headers=["*"]  # Añadido para exponer headers
)
# Añadir el router con prefix
app.include_router(api_router, prefix="/api/v1")

# Añadir ruta de health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}