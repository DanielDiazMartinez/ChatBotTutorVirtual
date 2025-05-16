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

    # Relaciones específicas de profesores
    documents = relationship("Document", 
                           back_populates="teacher", 
                           cascade="all, delete-orphan",
                           primaryjoin="and_(User.id==Document.teacher_id, User.role=='teacher')")
    
    teacher_conversations = relationship("Conversation", 
                                      foreign_keys="[Conversation.teacher_id]",
                                      back_populates="teacher", 
                                      cascade="all, delete-orphan",
                                      primaryjoin="and_(User.id==Conversation.teacher_id, User.role=='teacher')")
    
    teaching_subjects = relationship("Subject", 
                                   secondary='teacher_subject',
                                   back_populates="teachers",
                                   primaryjoin="and_(User.id==teacher_subject.c.teacher_id, User.role=='teacher')",
                                   secondaryjoin="Subject.id==teacher_subject.c.subject_id",
                                   foreign_keys="[teacher_subject.c.teacher_id, teacher_subject.c.subject_id]")

    # Relaciones específicas de estudiantes
    student_conversations = relationship("Conversation", 
                                       foreign_keys="[Conversation.student_id]",
                                       back_populates="student", 
                                       cascade="all, delete-orphan",
                                       primaryjoin="and_(User.id==Conversation.student_id, User.role=='student')")
    
    enrolled_subjects = relationship("Subject", 
                                   secondary='student_subject',
                                   back_populates="students",
                                   primaryjoin="and_(User.id==student_subject.c.student_id, User.role=='student')",
                                   secondaryjoin="Subject.id==student_subject.c.subject_id",
                                   foreign_keys="[student_subject.c.student_id, student_subject.c.subject_id]")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

# --- Modelos de Documentos y Chunks ---

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    description = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teacher = relationship("User", back_populates="documents", primaryjoin="and_(User.id==Document.teacher_id, User.role=='teacher')")
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
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="student_conversations", primaryjoin="and_(User.id==Conversation.student_id, User.role=='student')")
    teacher = relationship("User", back_populates="teacher_conversations", primaryjoin="and_(User.id==Conversation.teacher_id, User.role=='teacher')")
    document = relationship("Document", back_populates="conversations")
    topic = relationship("Topic", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    @validates('student_id', 'teacher_id')
    def validate_owner(self, key, value):
        if key == 'student_id' and value is not None:
            assert self.teacher_id is None, "Una conversación no puede pertenecer a un estudiante y un profesor al mismo tiempo."
        if key == 'teacher_id' and value is not None:
            assert self.student_id is None, "Una conversación no puede pertenecer a un estudiante y un profesor al mismo tiempo."
        return value

    def __repr__(self):
         owner_id = self.student_id or self.teacher_id
         owner_type = "Student" if self.student_id else "Teacher"
         return f"<Conversation(id={self.id}, owner_type={owner_type}, owner_id={owner_id}, document_id={self.document_id})>"


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

teacher_subject = Table('teacher_subject', Base.metadata,
    Column('teacher_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

student_subject = Table('student_subject', Base.metadata,
    Column('student_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
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

    teachers = relationship(
        "User", 
        secondary=teacher_subject, 
        back_populates="teaching_subjects",
        primaryjoin="Subject.id==teacher_subject.c.subject_id",
        secondaryjoin="and_(User.id==teacher_subject.c.teacher_id, User.role=='teacher')",
        foreign_keys=[teacher_subject.c.subject_id, teacher_subject.c.teacher_id]
    )
    students = relationship(
        "User", 
        secondary=student_subject, 
        back_populates="enrolled_subjects",
        primaryjoin="Subject.id==student_subject.c.subject_id",
        secondaryjoin="and_(User.id==student_subject.c.student_id, User.role=='student')",
        foreign_keys=[student_subject.c.subject_id, student_subject.c.student_id]
    )
    documents = relationship("Document", back_populates="subject")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")

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
    conversations = relationship("Conversation", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', subject_id={self.subject_id})>"


