from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from usuario_model import Usuario

class Alumno(Usuario):
    __tablename__ = "alumnos"
    id = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)
    curso = Column(String, nullable=True)
    grupo = Column(String, nullable=True)
    preguntas = relationship("Pregunta", back_populates="alumno")
    conversaciones = relationship("Conversacion", back_populates="alumno", cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'alumno',
    }
