from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db_config import Base

class Documento(Base):
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String)
    ruta_archivo = Column(String, nullable=False)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    profesor_id = Column(Integer, ForeignKey("profesores.id"))
    
    # Relaciones
    profesor = relationship("Profesor", back_populates="documentos")
    conversaciones = relationship("Conversacion", back_populates="documento", cascade="all, delete-orphan")
    preguntas = relationship("Pregunta", back_populates="documento")
