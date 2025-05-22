from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, ForeignKey, Text, func, Table
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import UserDefinedType

from app.core.database import Base

# --- Clases de Vectores y Funciones SQL para pgvector ---

class Vector(UserDefinedType):
    cache_ok = True # Añadido para SQLAlchemy 1.4+

    def __init__(self, dimensions):
        super(Vector, self).__init__()
        self.dimensions = dimensions

    def get_col_spec(self, **kw):
        return f"vector({self.dimensions})"

    def bind_processor(self, dialect):
        def process(value):
          
            if value is None:
                return None
            if isinstance(value, list):
                return f"[{','.join(map(str, value))}]"
            return value 
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            # Convierte el string PostgreSQL '[1,2,3]' a lista Python de floats
            if value is None:
                return None
            if isinstance(value, str):
                try:
                   
                    return [float(x) for x in value.strip('[]').split(',')]
                except ValueError:
                  
                    return None
            return value 
        return process

   
    def dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            
            return dialect.type_descriptor(self)
        else:
           
            return super().dialect_impl(dialect)


class CosineDistance(expression.FunctionElement):
    type = Float()
    name = 'cosine_distance'
    inherit_cache = True # Para SQLAlchemy 1.4+

@compiles(CosineDistance, 'postgresql')
def _compile_cosine_distance_postgresql(element, compiler, **kw):
    arg1 = compiler.process(element.clauses.clauses[0], **kw)
    arg2 = compiler.process(element.clauses.clauses[1], **kw)
    return f"{arg1} <=> {arg2}"

class EuclideanDistance(expression.FunctionElement):
    type = Float()
    name = 'euclidean_distance'
    inherit_cache = True

@compiles(EuclideanDistance, 'postgresql')
def _compile_euclidean_distance_postgresql(element, compiler, **kw):
    arg1 = compiler.process(element.clauses.clauses[0], **kw)
    arg2 = compiler.process(element.clauses.clauses[1], **kw)
    return f"{arg1} <-> {arg2}"

class InnerProduct(expression.FunctionElement):
    type = Float()
    name = 'inner_product'
    inherit_cache = True

@compiles(InnerProduct, 'postgresql')
def _compile_inner_product_postgresql(element, compiler, **kw):
    arg1 = compiler.process(element.clauses.clauses[0], **kw)
    arg2 = compiler.process(element.clauses.clauses[1], **kw)
    return f"{arg1} <#> {arg2}"

# --- Modelo de Usuario Unificado ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'teacher', 'student'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documents = relationship("Document", 
                          back_populates="user", 
                          cascade="all, delete-orphan")
    
    subjects = relationship("Subject", 
                          secondary='user_subject',
                          back_populates="users",
                          foreign_keys="[user_subject.c.user_id, user_subject.c.subject_id]")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

# --- Modelos de Documentos y Chunks ---

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="documents")
    subject = relationship("Subject", back_populates="documents")
    topic = relationship("Topic", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    chunk_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_number={self.chunk_number})>"


# --- Modelos de Conversaciones y Mensajes ---

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_role = Column(String, nullable=False)  # 'teacher', 'student', etc.
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], backref="conversations")
    document = relationship("Document", back_populates="conversations")
    subject = relationship("Subject", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    @validates('user_role')
    def validate_role(self, key, value):
        assert value in ['admin', 'teacher', 'student'], "El rol debe ser 'admin', 'teacher' o 'student'"
        return value

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_role={self.user_role}, user_id={self.user_id}, document_id={self.document_id})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    embedding = Column(Vector(768), nullable=True) 

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, is_bot={self.is_bot})>"


# --- Modelos de Asignaturas y Tablas Intermedias ---

user_subject = Table('user_subject', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship(
        "User", 
        secondary=user_subject, 
        back_populates="subjects",
        foreign_keys=[user_subject.c.subject_id, user_subject.c.user_id]
    )
    documents = relationship("Document", back_populates="subject")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', code='{self.code}')>"

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="topics")
    documents = relationship("Document", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', subject_id={self.subject_id})>"


