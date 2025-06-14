# app/api/__init__.py
from fastapi import APIRouter
from .chat_routes import chat_routes
from .documents_routes import documents_routes
from .users_routes import users_routes
from .subjects_routes import subjects_routes
from .topics_routes import topics_routes
from .auth_routes import auth_router
from .images_routes import images_routes

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"]) 
api_router.include_router(chat_routes, prefix="/chat", tags=["Chat"])
api_router.include_router(documents_routes, prefix="/documents", tags=["Documents"])
api_router.include_router(users_routes, prefix="/users", tags=["Users"])
api_router.include_router(subjects_routes, prefix="/subjects", tags=["Subjects"])
api_router.include_router(topics_routes, prefix="/topics", tags=["Topics"])
api_router.include_router(images_routes, prefix="/images", tags=["Images"])