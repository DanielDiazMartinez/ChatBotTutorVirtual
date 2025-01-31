from fastapi import APIRouter
from .auth_routes import router as auth_router
from .chat_routes import router as chat_router
from .document_routes import router as document_router
from .user_routes import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(document_router, prefix="/documents", tags=["Documentos"])
api_router.include_router(user_router, prefix="/users", tags=["Usuarios"])
