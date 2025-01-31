from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from models.mensaje_model import TipoMensaje

class ConversacionBase(BaseModel):
    titulo: str
    documento_id: int

class ConversacionCreate(ConversacionBase):
    pass

class ConversacionResponse(ConversacionBase):
    id: int
    fecha_creacion: datetime
    alumno_id: int

    class Config:
        from_attributes = True

class MensajeBase(BaseModel):
    contenido: str

class MensajeCreate(MensajeBase):
    pass

class MensajeResponse(MensajeBase):
    id: int
    tipo: TipoMensaje
    fecha: datetime
    conversacion_id: int

    class Config:
        from_attributes = True
