from fastapi import APIRouter
from .chat_routes import chat_routes
from .documents_routes import documents_routes
from .users_routes import users_routes
from .subjects_routes import subjects_routes
from .topics_routes import topics_routes

# Crear el router principal
api_router = APIRouter()

# Incluir las rutas individuales con prefijos
api_router.include_router(chat_routes, prefix="/chat", tags=["Chat"])
api_router.include_router(documents_routes, prefix="/documents", tags=["Documents"])
api_router.include_router(users_routes, prefix="/users", tags=["Users"])
api_router.include_router(subjects_routes, prefix="/subjects", tags=["Subjects"])
api_router.include_router(topics_routes, prefix="/topics", tags=["Topics"])