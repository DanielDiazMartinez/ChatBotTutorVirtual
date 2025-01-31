from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db_config import Base

class Pregunta(Base):
    __tablename__ = "preguntas"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"))
    documento_id = Column(Integer, ForeignKey("documentos.id"))
    alumno = relationship("Alumno", back_populates="preguntas")
    documento = relationship("Documento", back_populates="preguntas")
    respuesta = Column(String)  # La respuesta generada por el sistema
