from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import List, Optional, Union

from app.models.models import Admin, Teacher, Student
from app.models.schemas import TokenData
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") 

def authenticate_user(db: Session, email: str, password: str) -> Optional[Union[Admin, Teacher, Student]]:
    """
    Busca un usuario por email en las tablas Admin, Teacher y Student,
    y verifica su contraseña. Devuelve el objeto de usuario si es válido,
    o None si no lo es.
    """
    user = db.query(Admin).filter(Admin.email == email).first()
    user_type = "admin"
    if not user:
        user = db.query(Teacher).filter(Teacher.email == email).first()
        user_type = "teacher"
    if not user:
        user = db.query(Student).filter(Student.email == email).first()
        user_type = "student"

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Añadir el rol al objeto usuario para facilitar las comprobaciones
    user.role = user_type
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Union[Admin, Teacher, Student]:
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

    user = None
    if token_data.role == "admin":
        user = db.query(Admin).filter(Admin.id == token_data.id).first()
    elif token_data.role == "teacher":
        user = db.query(Teacher).filter(Teacher.id == token_data.id).first()
    elif token_data.role == "student":
        user = db.query(Student).filter(Student.id == token_data.id).first()

    if user is None:
        raise credentials_exception


    # Añadir el rol al objeto usuario para facilitar las comprobaciones
    user.role = token_data.role
    return user

async def get_current_active_admin(current_user: Admin = Depends(get_current_user)) -> Admin:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted for this user role")
    return current_user

async def get_current_active_teacher(current_user: Teacher = Depends(get_current_user)) -> Teacher:
    if current_user.role != "teacher":
         raise HTTPException(status_code=403, detail="Operation not permitted for this user role")
    return current_user

async def get_current_active_student(current_user: Student = Depends(get_current_user)) -> Student:
    if current_user.role != "student":
         raise HTTPException(status_code=403, detail="Operation not permitted for this user role")
    return current_user

def require_role(required_roles: List[str]): 
   
    async def role_checker(current_user: Union[Admin, Teacher, Student] = Depends(get_current_user)) -> Union[Admin, Teacher, Student]:
        if not hasattr(current_user, 'role') or current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of a Mismatched role. User role: {getattr(current_user, 'role', 'N/A')}. Required: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker 