from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Any, Dict, List, Optional

# ----------------------------------------
# SCHEMA PARA USUARIOS
# ----------------------------------------

class UserBase(BaseModel):
    """
    Modelo base para todos los usuarios (admin, profesor, alumno).
    """
    email: EmailStr = Field(..., example="usuario@example.com")
    full_name: Optional[str] = Field(None, example="Nombre Usuario")

class UserCreate(UserBase):
    """
    Modelo para crear un nuevo usuario.
    """
    password: str = Field(..., min_length=6, example="Password123!")
    role: str = Field(..., example="student")  # 'admin', 'teacher', 'student'

class UserOut(UserBase):
    """
    Modelo de salida para usuarios.
    """
    id: int = Field(..., example=1)
    role: str = Field(..., example="student")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    """
    Modelo para actualizar un usuario existente.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_superuser: Optional[bool] = None

# ----------------------------------------
# SCHEMA PARA LA AUTENTICACIÓN
# ----------------------------------------

class Token(BaseModel):
    """
    Modelo para representar el token de acceso que se entregará al usuario.
    """
    access_token: str = Field(..., example="jwt_token_aqui")
    token_type: str = Field(default="bearer", example="bearer")

class UserLogin(BaseModel):
    """
    Modelo para datos de inicio de sesión.
    """
    email: EmailStr = Field(..., example="usuario@example.com")
    password: str = Field(..., example="password123")

class UserResponse(BaseModel):
    """
    Modelo para respuesta de datos de usuario en autenticación.
    """
    id: int
    email: str
    name: str = Field(alias="full_name") 
    role: str
    
    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """
    Modelo para la información extraída del token.
    """
    id: Optional[int] = Field(None, example=1)
    email: Optional[EmailStr] = Field(None, example="usuario@example.com")
    role: Optional[str] = Field(None, example="teacher")  # 'admin', 'teacher', 'student'

# ----------------------------------------
# SCHEMA PARA LOS DOCUMENTOS
# ----------------------------------------
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None

class DocumentCreate(DocumentBase):    
    user_id: int
    subject_id: int  # Campo obligatorio
    topic_id: Optional[int] = None  # Campo opcional

    model_config = ConfigDict(from_attributes=True)

class DocumentOut(DocumentBase):
    id: int
    user_id: int
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

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
    subject_id: Optional[int] = None

class ConversationCreate(BaseModel):
    """
    Modelo para crear una nueva conversación.
    
    Se puede proporcionar solo subject_id para buscar en todos los documentos
    de una asignatura, o especificar un document_id concreto.
    """
    text: Optional[str] = None
    subject_id: Optional[int] = None
    model_config = ConfigDict(extra="forbid")

class ConversationOut(BaseModel):
    """
    Modelo de salida para una conversación.
    """
    id: int
    user_id: int
    subject_id: Optional[int] = None
    messages: List["MessageOut"] = []

    model_config = ConfigDict(from_attributes=True)

class ConversationWithResponse(BaseModel):
    """
    Esquema que combina una conversación creada y la respuesta inicial del bot.
    """
    conversation: ConversationOut
    bot_response: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ----------------------------------------
#  SCHEMA PARA LOS MENSAJES
# ----------------------------------------
class MessageBase(BaseModel):
    text: Optional[str] = None
    is_bot: bool  

class MessageCreate(BaseModel):
    """
    Modelo para crear un nuevo mensaje.
    Puede incluir texto y/o una referencia a una imagen.
    is_bot y created_at se gestionan en el backend.
    """
    text: Optional[str] = None

class MessageOut(BaseModel):
    id: int
    text: Optional[str] = None
    is_bot: bool
    conversation_id: int
    image_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MessagePairOut(BaseModel):
    user_message: MessageOut  
    bot_message: MessageOut 

    model_config = ConfigDict(from_attributes=True)
    
    
class ImageOut(BaseModel):
    """
    Modelo de salida para las imágenes.
    """
    id: int
    file_path: str
    description: Optional[str] = None
    user_id: int
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

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
    """
    pass

class SubjectOut(SubjectBase):
    """
    Modelo de respuesta para asignaturas.
    Incluye ID, listas de profesores y estudiantes, y conteo de ambos.
    """
    id: int
    teachers: List[UserOut] = []
    students: List[UserOut] = []
    teacher_count: int = 0
    student_count: int = 0

    model_config = ConfigDict(from_attributes=True)

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
    documents: List[DocumentOut] = []

    model_config = ConfigDict(from_attributes=True)

# ----------------------------------------
# SCHEMA PARA RELACIONES ENTRE ENTIDADES
# ----------------------------------------

class UserIdsRequest(BaseModel):
    """
    Modelo para solicitar la adición de múltiples usuarios a una asignatura.
    """
    user_ids: List[int] = Field(..., example=[1, 2, 3])

class APIResponse(BaseModel):
    data: Any
    message: Optional[str] = None
    error: Optional[str] = None
    status: Optional[int] = 200

    model_config = ConfigDict(from_attributes=True)

# ----------------------------------------
# SCHEMA PARA ANÁLISIS DE ESTUDIANTES
# ----------------------------------------

class StudentAnalysisStatistics(BaseModel):
    """
    Modelo para estadísticas de participación de estudiantes en una asignatura.
    """
    total_messages: int = Field(..., example=150)
    unique_students: int = Field(..., example=25)
    participation_rate: float = Field(..., example=0.75)
    most_active_students: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

class StudentAnalysisSummary(BaseModel):
    """
    Modelo para el resumen completo del análisis de estudiantes.
    """
    subject_id: int = Field(..., example=1)
    subject_name: str = Field(..., example="Matemáticas Básicas")
    analysis_summary: str = Field(..., description="Resumen generado por IA sobre las deficiencias y gaps identificados")
    statistics: StudentAnalysisStatistics
    sample_questions: List[str] = Field(default_factory=list, description="Muestra de preguntas representativas")
    analysis_date: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(from_attributes=True)

class StudentAnalysisRequest(BaseModel):
    """
    Modelo para solicitar análisis de estudiantes con parámetros opcionales.
    """
    days_back: Optional[int] = Field(default=30, example=30, description="Días hacia atrás para analizar mensajes")
    min_participation: Optional[int] = Field(default=1, example=1, description="Mínimo de mensajes por estudiante")
    
    model_config = ConfigDict(from_attributes=True)

