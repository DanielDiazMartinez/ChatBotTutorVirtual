# models.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func


Base = declarative_base()

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


    questions = relationship("Question", back_populates="student", cascade="all, delete-orphan")


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

 
    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"

# ------------------------------#
# Modelo de Preguntas y Respuestas
# ------------------------------#
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)  
    answer = Column(Text, nullable=True)  
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True)  
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    
    student = relationship("Student", back_populates="questions")
    document = relationship("Document", back_populates="questions")

    def __repr__(self):
        return f"<Question(id={self.id}, text='{self.text[:20]}...')>"

# ------------------------------#
# Modelo de Conversación
# ------------------------------#
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    
    student = relationship("Student", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation(id={self.id}, student_id={self.student_id})>"

# ------------------------------#
# Modelo de Mensajes en Conversación
# ------------------------------#
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False)  # "student" o "bot"
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, sender={self.sender})>"
