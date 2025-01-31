from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from db_config import Base

class TipoMensaje(enum.Enum):
    PREGUNTA = "pregunta"
    RESPUESTA = "respuesta"

class Mensaje(Base):
    __tablename__ = "mensajes"
    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(String, nullable=False)
    tipo = Column(Enum(TipoMensaje), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    conversacion_id = Column(Integer, ForeignKey("conversaciones.id"))
    
    # Relación
    conversacion = relationship("Conversacion", back_populates="mensajes")
