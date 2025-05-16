from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.core.config import settings
from app.core.auth import authenticate_user 
from app.core.security import create_access_token
from app.models.schemas import APIResponse, Token, UserLogin, UserResponse
from app.models.models import User

auth_router = APIRouter()

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para que los usuarios (Admin, Teacher, Student) obtengan un token JWT.
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token con el ID y el ROL del usuario
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login", response_model=APIResponse)
async def login_api(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Endpoint para login de la API. Devuelve el token JWT y los datos del usuario.
    """
    user = authenticate_user(db, email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token con el ID y el ROL del usuario
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
     
    # Devolver tanto el token como los datos del usuario
    return {
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.full_name,
                "role": user.role
            }
        },
        "message": "Login successful",
        "status": 200
    }