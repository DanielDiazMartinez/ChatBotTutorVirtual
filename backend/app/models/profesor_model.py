from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from usuario_model import Usuario

class Profesor(Usuario):
    __tablename__ = "profesores"
    id = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)
    departamento = Column(String, nullable=True)
    especialidad = Column(String, nullable=True)
    documentos = relationship("Documento", back_populates="profesor")

    __mapper_args__ = {
        'polymorphic_identity': 'profesor',
    }
