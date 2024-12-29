from sqlalchemy import Column, Integer, String, ForeignKey
from db_config import Base

class Temario(Base):
    __tablename__ = "temarios"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String)
    archivo = Column(String, nullable=False)  # Ruta al archivo subido
    profesor_id = Column(Integer, ForeignKey("usuarios.id"))
