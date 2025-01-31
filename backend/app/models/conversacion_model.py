from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db_config import Base

class Conversacion(Base):
    __tablename__ = "conversaciones"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"))
    documento_id = Column(Integer, ForeignKey("documentos.id"))
    
    # Relaciones
    alumno = relationship("Alumno", back_populates="conversaciones")
    documento = relationship("Documento", back_populates="conversaciones")
    mensajes = relationship("Mensaje", back_populates="conversacion", cascade="all, delete-orphan")
