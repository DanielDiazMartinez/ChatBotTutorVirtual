from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# ----------------------------------------
# SCHEMA PARA PROFESORES
# ----------------------------------------

class TeacherBase(BaseModel):
    """
    Modelo base para los profesores.
    """
    email: EmailStr = Field(..., example="profesor@example.com")
    full_name: Optional[str] = Field(None, example="Juan Pérez")


class TeacherCreate(TeacherBase):
    """
    Modelo para el registro de un profesor.
    Se requiere la contraseña para la creación.
    """
    password: str = Field(..., min_length=6, example="Password123!")


class TeacherOut(TeacherBase):
    """
    Modelo de salida para un profesor, sin la contraseña.
    Se puede incluir el identificador u otros campos de solo lectura.
    """
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True  # Permite trabajar con objetos ORM (por ejemplo, SQLAlchemy)

class TeacherUpdate(TeacherBase):
    """
    Modelo para la actualización de un profesor.
    Se pueden actualizar el email y el nombre completo.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
                                      
# ----------------------------------------
# SCHEMA PARA ALUMNOS
# ----------------------------------------

class StudentBase(BaseModel):
    """
    Modelo base para los alumnos.
    """
    email: EmailStr = Field(..., example="alumno@example.com")
    full_name: Optional[str] = Field(None, example="María Gómez")


class StudentCreate(StudentBase):
    """
    Modelo para el registro de un alumno.
    Se requiere la contraseña para la creación.
    """
    password: str = Field(..., min_length=6, example="Password123!")


class StudentOut(StudentBase):
    """
    Modelo de salida para un alumno, sin la contraseña.
    """
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True


# ----------------------------------------
# SCHEMA PARA LA AUTENTICACIÓN
# ----------------------------------------

class Token(BaseModel):
    """
    Modelo para representar el token de acceso que se entregará al usuario.
    """
    access_token: str = Field(..., example="jwt_token_aqui")
    token_type: str = Field(default="bearer", example="bearer")


class TokenData(BaseModel):
    """
    Modelo para la información extraída del token.
    Permite almacenar datos mínimos como el id, email y rol del usuario (profesor o alumno).
    """
    id: Optional[int] = Field(None, example=1)
    email: Optional[EmailStr] = Field(None, example="usuario@example.com")
    role: Optional[str] = Field(None, example="teacher")  # Alternativamente "student"

# ----------------------------------------
# SCHEMA PARA LOS DOCUMENTOS
# ----------------------------------------
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None


class DocumentCreate(DocumentBase):    
    teacher_id: int  

    class Config:
        from_attributes = True
        

class DocumentOut(DocumentBase):
    id: int

    class Config:
        from_attributes = True

# ----------------------------------------
#  SCHEMA PARA LAS CONVERSACIONES
# ----------------------------------------
class ConversationBase(BaseModel):
    """
    Modelo base para conversaciones.
    """
    document_id: int

class ConversationCreate(BaseModel):
    """
    Modelo para crear una nueva conversación.
    """
    document_id: int
    text: Optional[str] = None  # Mensaje inicial opcional

class ConversationOut(BaseModel):
    """
    Modelo de salida para una conversación.
    """
    id: int
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    document_id: int
    messages: List["MessageOut"] = []

    class Config:
        from_attributes = True

class ConversationWithResponse(BaseModel):
    """
    Esquema que combina una conversación creada y la respuesta inicial del bot.
    """
    conversation: ConversationOut
    bot_response: Optional[str] = None
    
    class Config:
        from_attributes = True

# ----------------------------------------
#  SCHEMA PARA LOS MENSAJES
# ----------------------------------------
class MessageBase(BaseModel):
    text: str
    is_bot: bool  

class MessageCreate(MessageBase):
    """
    Modelo para crear un nuevo mensaje.
    """
    created_at: Optional[datetime] = None
    pass

class MessageOut(MessageBase):
    id: int
    conversation_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessagePairOut(BaseModel):
    user_message: MessageOut  
    bot_message: MessageOut 

    class Config:
        from_attributes = True 

class ConversationCreateRequest(BaseModel):
    """
    Esquema Pydantic para la solicitud de creación de una nueva conversación.
    Solo requiere el ID del documento al que estará asociada la conversación.
    El usuario se determinará a través de la autenticación en el endpoint.
    """
    document_id: int = Field(...,
                             description="El ID único del documento sobre el cual se creará la conversación.",
                             gt=0) 

  
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": 42
            }
        }