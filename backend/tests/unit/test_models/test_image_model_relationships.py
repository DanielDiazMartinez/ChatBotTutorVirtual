import pytest
from sqlalchemy.orm import Session
from app.models.models import Image, Subject, User, Topic

class TestImageModelRelationships:
    """Pruebas para verificar las relaciones del modelo Image"""
    
    def test_image_subject_relationship(self, db_session_test: Session):
        """Verifica la relación bidireccional entre Image y Subject"""
        # Crear un subject de prueba
        subject = Subject(name="Matemáticas", code="MATH101", description="Descripción de prueba")
        db_session_test.add(subject)
        db_session_test.commit()
        
        # Crear un usuario de prueba
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_pwd",
            role="student"
        )
        db_session_test.add(user)
        db_session_test.commit()
        
        # Crear una imagen asociada al subject
        image = Image(
            file_path="test/path/image.jpg",
            description="Imagen de prueba",
            user_id=user.id,
            subject_id=subject.id
        )
        db_session_test.add(image)
        db_session_test.commit()
        
        # Verificar que la imagen está asociada al subject
        assert image.subject_id == subject.id
        assert image.subject.id == subject.id
        
        # Verificar que el subject tiene la imagen en su lista de imágenes
        assert len(subject.images) == 1
        assert subject.images[0].id == image.id
        
    def test_image_user_relationship(self, db_session_test: Session):
        """Verifica la relación bidireccional entre Image y User"""
        # Crear un usuario de prueba
        user = User(
            email="test2@example.com",
            full_name="Test User 2",
            hashed_password="hashed_pwd",
            role="student"
        )
        db_session_test.add(user)
        db_session_test.commit()
        
        # Crear una imagen asociada al usuario
        image = Image(
            file_path="test/path/user_image.jpg",
            description="Imagen de usuario",
            user_id=user.id
        )
        db_session_test.add(image)
        db_session_test.commit()
        
        # Verificar que la imagen está asociada al usuario
        assert image.user_id == user.id
        assert image.user.id == user.id
        
        # Verificar que el usuario tiene la imagen en su lista de imágenes
        assert len(user.images) > 0
        assert any(img.id == image.id for img in user.images)
        
    def test_image_topic_relationship(self, db_session_test: Session):
        """Verifica la relación entre Image y Topic"""
        # Crear un subject de prueba
        subject = Subject(name="Física", code="PHY101", description="Física básica")
        db_session_test.add(subject)
        db_session_test.commit()
        
        # Crear un topic asociado al subject
        topic = Topic(
            name="Mecánica",
            description="Leyes de Newton",
            subject_id=subject.id
        )
        db_session_test.add(topic)
        db_session_test.commit()
        
        # Crear un usuario de prueba
        user = User(
            email="test3@example.com",
            full_name="Test User 3",
            hashed_password="hashed_pwd",
            role="student"
        )
        db_session_test.add(user)
        db_session_test.commit()
        
        # Crear una imagen asociada al topic
        image = Image(
            file_path="test/path/topic_image.jpg",
            description="Imagen de tema",
            user_id=user.id,
            subject_id=subject.id,
            topic_id=topic.id
        )
        db_session_test.add(image)
        db_session_test.commit()
        
        # Verificar que la imagen está asociada al topic
        assert image.topic_id == topic.id
        assert image.topic.id == topic.id
        
        # Verificar que el topic tiene la imagen en su lista de imágenes
        assert len(topic.images) == 1
        assert topic.images[0].id == image.id
        
    def test_image_message_relationship(self, db_session_test: Session):
        """Verifica la relación entre Image y Message"""
        from app.models.models import Conversation, Message
        
        # Crear un usuario de prueba
        user = User(
            email="test4@example.com",
            full_name="Test User 4",
            hashed_password="hashed_pwd",
            role="student"
        )
        db_session_test.add(user)
        db_session_test.commit()
        
        # Crear una conversación para el usuario
        conversation = Conversation(user_id=user.id)
        db_session_test.add(conversation)
        db_session_test.commit()
        
        # Crear una imagen
        image = Image(
            file_path="test/path/message_image.jpg",
            description="Imagen para mensaje",
            user_id=user.id
        )
        db_session_test.add(image)
        db_session_test.commit()
        
        # Crear un mensaje con referencia a la imagen
        message = Message(
            conversation_id=conversation.id,
            is_bot=False,
            text="Mensaje con imagen",
            image_id=image.id
        )
        db_session_test.add(message)
        db_session_test.commit()
        
        # Verificar que el mensaje está asociado a la imagen
        assert message.image_id == image.id
        assert message.image.id == image.id
        
        # Verificar que la imagen tiene el mensaje asociado
        assert len(image.messages) == 1
        assert image.messages[0].id == message.id
