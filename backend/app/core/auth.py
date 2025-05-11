from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import List, Optional

from app.models.models import User
from app.models.schemas import TokenData
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") 

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Busca un usuario por email y verifica su contraseña.
    Devuelve el objeto de usuario si es válido, o None si no lo es.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependencia para obtener el usuario actual a partir del token JWT.
    Verifica el token, extrae el ID y el rol, y obtiene el usuario de la BD.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        if user_id is None or user_role is None:
            raise credentials_exception
        token_data = TokenData(id=int(user_id), role=user_role)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(
        User.id == token_data.id,
        User.role == token_data.role
    ).first()

    if user is None:
        raise credentials_exception

    return user

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted for admin role only")
    return current_user

async def get_current_active_teacher(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "teacher":
         raise HTTPException(status_code=403, detail="Operation not permitted for teacher role only")
    return current_user

async def get_current_active_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "student":
         raise HTTPException(status_code=403, detail="Operation not permitted for student role only")
    return current_user

def require_role(required_roles: List[str]):    
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {', '.join(required_roles)}. User role: {current_user.role}"
            )
        return current_user
    return role_checker 