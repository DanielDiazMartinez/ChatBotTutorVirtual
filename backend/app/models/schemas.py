from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional

# ----------------------------------------
# SCHEMA PARA ADMINISTRADORES
# ----------------------------------------

class AdminBase(BaseModel):
    """
    Modelo base para administradores.
    """
    email: EmailStr = Field(..., example="admin@example.com")
    full_name: Optional[str] = Field(None, example="Admin User")

class AdminCreate(AdminBase):
    """
    Modelo para crear un nuevo administrador.
    """
    password: str = Field(..., min_length=6, example="SecurePassword123!")
    is_superuser: bool = Field(default=False, example=False)

class AdminOut(AdminBase):
    """
    Modelo de salida para administradores.
    """
    id: int = Field(..., example=1)
    is_superuser: bool = Field(..., example=False)
    created_at: datetime

    class Config:
        from_attributes = True

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
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None  

    class Config:
        from_attributes = True
        

class DocumentOut(DocumentBase):
    id: int
    teacher_id: int
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentChunkOut(BaseModel):
    id: int
    document_id: int
    content: str
    chunk_number: int

    model_config = ConfigDict(from_attributes=True) 

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
    text: Optional[str] = None
    topic_id: Optional[int] = None

class ConversationOut(BaseModel):
    """
    Modelo de salida para una conversación.
    """
    id: int
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    document_id: int
    topic_id: Optional[int] = None
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

# ----------------------------------------
# SCHEMA PARA ASIGNATURAS
# ----------------------------------------

class SubjectBase(BaseModel):
    """
    Modelo base para asignaturas.
    """
    name: str = Field(..., example="Matemáticas")
    code: str = Field(..., example="MAT101")
    description: Optional[str] = Field(None, example="Curso básico de matemáticas")

class SubjectCreate(SubjectBase):
    """
    Modelo para crear una nueva asignatura.
    No necesita campos adicionales.
    """
    pass

class SubjectOut(SubjectBase):
    """
    Modelo de respuesta para asignaturas.
    Incluye ID y listas de profesores y estudiantes.
    """
    id: int
    teachers: List[TeacherOut] = []
    students: List[StudentOut] = []

    class Config:
        from_attributes = True

# ----------------------------------------
# SCHEMA PARA TEMAS (TOPICS)
# ----------------------------------------

class TopicBase(BaseModel):
    """
    Modelo base para temas.
    """
    name: str = Field(..., example="Introducción a Python")
    description: Optional[str] = Field(None, example="Conceptos básicos de Python")
    subject_id: int = Field(..., example=1)

class TopicCreate(TopicBase):
    """
    Modelo para crear un nuevo tema.
    """
    pass

class TopicUpdate(BaseModel):
    """
    Modelo para actualizar un tema existente.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    subject_id: Optional[int] = None

class TopicOut(TopicBase):
    """
    Modelo de salida para temas.
    """
    id: int
    created_at: datetime
    documents: List["DocumentOut"] = []

    class Config:
        from_attributes = True

