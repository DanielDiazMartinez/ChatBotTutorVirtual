from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import UserDefinedType
from sqlalchemy.dialects.postgresql import dialect as postgresql_dialect

Base = declarative_base()

class Vector(UserDefinedType):
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def get_col_spec(self, **kw):
        return f"vector({self.dimensions})"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value
        return process

    def dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(self)
        else:
            return super().dialect_impl(dialect)

# Definición de funciones SQL para pgvector
class CosineDistance(expression.FunctionElement):
    type = Float() # <--- Cambia None por Float()
    name = 'cosine_distance'
    inherit_cache = True

@compiles(CosineDistance)
def _compile_cosine_distance(element, compiler, **kw):
    # Asegúrate de que los argumentos se procesen correctamente
    arg1 = compiler.process(element.clauses.clauses[0], **kw)
    arg2 = compiler.process(element.clauses.clauses[1], **kw)
    return f"{arg1} <=> {arg2}"

class EuclideanDistance(expression.FunctionElement):
    type = Float() # <--- Cambia None por Float()
    name = 'euclidean_distance'
    inherit_cache = True

@compiles(EuclideanDistance)
def _compile_euclidean_distance(element, compiler, **kw):
    # Asegúrate de que los argumentos se procesen correctamente
    arg1 = compiler.process(element.clauses.clauses[0], **kw)
    arg2 = compiler.process(element.clauses.clauses[1], **kw)
    return f"{arg1} <-> {arg2}"

class InnerProduct(expression.FunctionElement):
    type = Float() # <--- Cambia None por Float()
    name = 'inner_product'
    inherit_cache = True

@compiles(InnerProduct)
def _compile_inner_product(element, compiler, **kw):
    # Asegúrate de que los argumentos se procesen correctamente
    arg1 = compiler.process(element.clauses.clauses[0], **kw)
    arg2 = compiler.process(element.clauses.clauses[1], **kw)
    return f"{arg1} <#> {arg2}"
# --------------------------#
# Modelo para los Profesores
# --------------------------#
class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    documents = relationship("Document", back_populates="teacher", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="teacher", cascade="all, delete-orphan")  # Añade esta línea
    
    def __repr__(self):
        return f"<Teacher(id={self.id}, email='{self.email}')>"

# --------------------------#
# Modelo para los Alumnos
# --------------------------#
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversations = relationship("Conversation", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(id={self.id}, email='{self.email}')>"

# ----------------------------------#
# Modelo para los Documentos (PDFs)
# ----------------------------------#
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    description = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

    teacher = relationship("Teacher", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"

# ----------------------------------#
# Modelo para Chunks de Documento
# ----------------------------------#
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1024))  # Ajustar dimensión según el modelo que uses
    chunk_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_number={self.chunk_number})>"

# ------------------------------#
# Modelo de Conversación
# ------------------------------#
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)  # Ahora puede ser NULL
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)  # Nuevo campo
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    student = relationship("Student", back_populates="conversations")
    teacher = relationship("Teacher", back_populates="conversations")  # Nueva relación
    document = relationship("Document", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Validación para asegurar que solo uno de student_id o teacher_id esté presente
    @validates('student_id', 'teacher_id')
    def validate_owner(self, key, value):
        if key == 'student_id' and value is not None:
            assert self.teacher_id is None, "Una conversación no puede pertenecer a un estudiante y un profesor al mismo tiempo"
        if key == 'teacher_id' and value is not None:
            assert self.student_id is None, "Una conversación no puede pertenecer a un estudiante y un profesor al mismo tiempo"
        return value
# ------------------------------#
# Modelo de Mensajes
# ------------------------------#
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    embedding = Column(Vector(1024), nullable=True)  

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, is_bot={self.is_bot})>"