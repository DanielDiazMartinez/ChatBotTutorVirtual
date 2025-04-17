from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.models import Document, DocumentChunk,CosineDistance, EuclideanDistance, InnerProduct, Conversation, Message, Student, Teacher
from ..utils.document_utils import  chunk_text,generate_embedding
from typing import List, Tuple, Optional
from ..services.groq_service import generate_groq_response

def insert_document_chunks(
    db: Session,
    document_id: int,
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[DocumentChunk]:
    """
    Divide el texto de un documento en chunks, genera embeddings para cada uno
    y los inserta en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento al que pertenecen los chunks
        text: Texto completo del documento
        chunk_size: Tamaño de cada chunk en caracteres
        overlap: Cantidad de caracteres de superposición entre chunks
        
    Returns:
        Lista de objetos DocumentChunk creados
    """
    # Recuperar el documento para asegurarse de que existe
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"No existe un documento con ID {document_id}")
    
    # Dividir el texto en chunks
    chunks = chunk_text(text, chunk_size=chunk_size)
    
    created_chunks = []
    
    
    for i, chunk_content in enumerate(chunks):
        
        embedding = generate_embedding(chunk_content)
        
        
        chunk = DocumentChunk(
            document_id=document_id,
            content=chunk_content,
            embedding=embedding,
            chunk_number=i
        )
        
        # Añadirlo a la sesión
        db.add(chunk)
        created_chunks.append(chunk)
    
    # Guardar todos los chunks en la base de datos
    db.commit()
    
    print(f"Se insertaron {len(created_chunks)} chunks para el documento ID {document_id}")
    
    return created_chunks

def search_similar_chunks(db: Session, 
                          query_embedding: List[float], 
                          document_id: Optional[int] = None, 
                          limit: int = 5,
                          similarity_metric: str = "cosine") -> List[Tuple[DocumentChunk, float]]:
    """
    Busca chunks similares a un embedding de consulta usando pgvector
    
    Args:
        db: Sesión de SQLAlchemy
        query_embedding: Vector de embedding de la consulta
        document_id: ID del documento para filtrar (opcional)
        limit: Número máximo de resultados
        similarity_metric: Métrica de similitud ("cosine", "l2", o "dot")
        
    Returns:
        Lista de tuplas (chunk, score de similitud)
    """
    from sqlalchemy import select
    
    
    if similarity_metric == "cosine":
        distance_func = CosineDistance
        # Para coseno, menor distancia = mayor similitud
        convert_score = lambda x: 1.0 - x  # Convertir distancia a similitud
    elif similarity_metric == "l2":
        distance_func = EuclideanDistance
        # Para L2, menor distancia = mayor similitud, pero no tiene límite superior
        convert_score = lambda x: 1.0 / (1.0 + x)
    else:  
        distance_func = InnerProduct
        # Para producto escalar, mayor valor = mayor similitud
        convert_score = lambda x: -x
    
    # Construir la consulta
    query = select(
        DocumentChunk,
        distance_func(DocumentChunk.embedding, query_embedding).label("distance")
    )
    
    # Filtrar por documento si se especifica
    if document_id:
        query = query.filter(DocumentChunk.document_id == document_id)
    
    # Ordenar por similitud
    query = query.order_by(distance_func(DocumentChunk.embedding, query_embedding))
    
    # Limitar resultados
    query = query.limit(limit)
    
    # Ejecutar la consulta
    results = db.execute(query).all()
    
    # Convertir resultados
    return [(chunk, convert_score(distance)) for chunk, distance in results]

def generate_conversation(
    db: Session,
    document_id: int,
    user_id: int,
    user_type: str,  # "teacher" o "student"
    initial_message_text: str = None
) -> Conversation:
    """
    Crea una nueva conversación asociada a un profesor o estudiante y un documento.
    Opcionalmente incluye el primer mensaje.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento sobre el que trata la conversación
        user_id: ID del usuario (profesor o estudiante)
        user_type: Tipo de usuario ("teacher" o "student")
        initial_message_text: Texto del primer mensaje (opcional)
        
    Returns:
        Objeto Conversation creado
    """
    # Verificar que el documento existe
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Verificar que el usuario existe
    if user_type == "student":
        user = db.query(Student).filter(Student.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        # Crear la conversación para estudiante
        new_conversation = Conversation(
            student_id=user_id,
            teacher_id=None,
            document_id=document_id
        )
    elif user_type == "teacher":
        user = db.query(Teacher).filter(Teacher.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Profesor no encontrado")
        
        # Crear la conversación para profesor
        new_conversation = Conversation(
            student_id=None,
            teacher_id=user_id,
            document_id=document_id
        )
    else:
        raise HTTPException(status_code=400, detail="Tipo de usuario no válido. Debe ser 'teacher' o 'student'")
    
    # Guardar la conversación
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    # Si se proporciona un mensaje inicial, añadirlo
    if initial_message_text:
        question_embedding = generate_embedding(initial_message_text)

        new_message = Message(
            text=initial_message_text,
            is_bot=False,
            conversation_id=new_conversation.id,
            emmbedding=question_embedding 
        )
        db.add(new_message)
        db.commit()
        
        similar_chunks = search_similar_chunks(db, question_embedding, document_id)
        context = " ".join([chunk.content for chunk, score in similar_chunks if score > 0.65])

        response_text = generate_groq_response(initial_message_text, context)
        response_embedding = generate_embedding(response_text)

        new_message = Message(
            text=response_text,
            is_bot=True,
            conversation_id=new_conversation.id,
            emmbedding=response_embedding
        )

        db.add(new_message)
        db.commit()

    return response_text,new_conversation 