from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, literal_column
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
    """
    embedding_str = f"CAST(ARRAY[{', '.join(map(str, query_embedding))}] AS vector)"

    if similarity_metric == "cosine":
        distance_expression = CosineDistance(DocumentChunk.embedding, literal_column(embedding_str))
        convert_score = lambda x: 1.0 - x
    elif similarity_metric == "l2":
        distance_expression = EuclideanDistance(DocumentChunk.embedding, literal_column(embedding_str))
        convert_score = lambda x: 1.0 / (1.0 + x)
    else:
        distance_expression = InnerProduct(DocumentChunk.embedding, literal_column(embedding_str))
        convert_score = lambda x: -x

    query = select(
        DocumentChunk,
        distance_expression.label("distance")
    ).filter(DocumentChunk.document_id == document_id if document_id else True).\
        order_by("distance").\
        limit(limit)

    results = db.execute(query).all()

    return [(row.DocumentChunk, convert_score(row.distance)) for row in results]

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
            embedding=question_embedding 
        )
        db.add(new_message)
        db.commit()
        
        similar_chunks = search_similar_chunks(db, question_embedding, document_id)
        similarity_threshold = 0.65 
        context_chunks = [chunk.content for chunk, score in similar_chunks if score > similarity_threshold]
         # --- DEBUGGING ---
        print(f"--- Debug Info: search_similar_chunks results (before filtering) ---")
        print(similar_chunks)
        # ---------------
        context = " ".join([chunk.content for chunk, score in similar_chunks if score > 0.65])

        # --- DEBUGGING ---
        print(f"--- Debug Info: Data sent to Groq ---")
        print(f"User Question: {initial_message_text}")
        print(f"Context Chunks Found (count): {len(context_chunks)}")
        print(f"Similarity Threshold: {similarity_threshold}")
        print(f"Final Context String (first 500 chars): {context[:1000]}") # Imprime solo una parte si es muy largo
        # ---------------
        
        # Llama a Groq
        try:
            response_text = generate_groq_response(initial_message_text, context)
        # --- DEBUGGING ---
            print(f"Groq Raw Response: {response_text}")
        # ---------------
        except Exception as e:
            print(f"--- ERROR calling generate_groq_response: {e} ---")
            response_text = "Lo siento, ocurrió un error al contactar al servicio de IA." # Mensaje de error más específico

        response_embedding = generate_embedding(response_text)

        new_message = Message(
            text=response_text,
            is_bot=True,
            conversation_id=new_conversation.id,
            embedding=response_embedding
        )

        db.add(new_message)
        db.commit()

    return response_text,new_conversation 

def add_message_and_generate_response(
    db: Session,
    conversation_id: int,
    user_id: int,
    user_type: str,
    message_text: str,
    document_id: int # Añadido para buscar chunks (asumiendo que se necesita)
) -> Tuple[Message, Message]: # <--- Tipo de retorno modificado
    """
    Añade el mensaje del usuario a una conversación existente,
    genera una respuesta del bot y guarda ambos mensajes.

    Args:
        db: Sesión de SQLAlchemy
        conversation_id: ID de la conversación
        user_id: ID del usuario (profesor o estudiante)
        user_type: Tipo de usuario ("teacher" o "student")
        message_text: Texto del mensaje del usuario
        document_id: ID del documento asociado a la conversación

    Returns:
        Una tupla conteniendo el objeto Message del usuario y el objeto Message del bot.
    """
    # Verificar que la conversación existe
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # Verificar usuario y crear su mensaje
    question_embedding = generate_embedding(message_text)
    user_msg_obj: Message = None # Inicializar variable

    if user_type == "student":
        user = db.query(Student).filter(Student.id == user_id).first()
        if not user or conversation.student_id != user_id:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado o no pertenece a esta conversación")
        user_msg_obj = Message(
            text=message_text,
            is_bot=False,
            conversation_id=conversation_id,
            embedding=question_embedding
        )
    elif user_type == "teacher":
        user = db.query(Teacher).filter(Teacher.id == user_id).first()
        if not user or conversation.teacher_id != user_id:
            raise HTTPException(status_code=404, detail="Profesor no encontrado o no pertenece a esta conversación")
        user_msg_obj = Message(
            text=message_text,
            is_bot=False,
            conversation_id=conversation_id,
            embedding=question_embedding
        )
    else:
        raise HTTPException(status_code=400, detail="Tipo de usuario no válido. Debe ser 'teacher' o 'student'")

    # Guardar el mensaje del usuario PRIMERO
    db.add(user_msg_obj)
    # Hacemos flush para obtener el ID si fuera necesario, pero commit al final
    db.flush()
    db.refresh(user_msg_obj) # Para obtener cualquier valor autogenerado como el ID

    # Preparar contexto y llamar a Groq
    # (Usamos conversation.document_id que ya obtuvimos)
    similar_chunks = search_similar_chunks(db, question_embedding, conversation.document_id) # <-- Usar document_id de la conversación
    similarity_threshold = 0.65
    context_chunks = [chunk.content for chunk, score in similar_chunks if score > similarity_threshold]
    context = " ".join(context_chunks)

    # --- DEBUGGING ---
    print(f"--- Debug Info: search_similar_chunks results (before filtering) ---")
    print(similar_chunks)
    print(f"--- Debug Info: Data sent to Groq ---")
    print(f"User Question: {message_text}")
    print(f"Context Chunks Found (count): {len(context_chunks)}")
    print(f"Similarity Threshold: {similarity_threshold}")
    print(f"Final Context String (first 500 chars): {context[:1000]}")
    # ---------------

    try:
        response_text = generate_groq_response(message_text, context)
        print(f"Groq Raw Response: {response_text}") # DEBUG
    except Exception as e:
        print(f"--- ERROR calling generate_groq_response: {e} ---") # DEBUG
        # Considerar si lanzar una excepción aquí o devolver un error
        response_text = "Lo siento, ocurrió un error al generar la respuesta."

    response_embedding = generate_embedding(response_text)

    # Crear el mensaje del bot
    bot_msg_obj = Message( # <--- Guardar en variable diferente
        text=response_text,
        is_bot=True,
        conversation_id=conversation_id,
        embedding=response_embedding
    )


    db.add(bot_msg_obj)

    db.commit()


    db.refresh(bot_msg_obj)


    return user_msg_obj, bot_msg_obj