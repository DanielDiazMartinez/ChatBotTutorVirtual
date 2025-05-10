from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, literal_column
from ..models.models import Document, DocumentChunk,CosineDistance, EuclideanDistance, InnerProduct, Conversation, Message, Student, Teacher
from ..utils.document_utils import get_embedding_for_query
from typing import List, Tuple, Optional
from ..services.groq_service import generate_groq_response
from ..utils.document_utils import process_document_and_embed_chunks_semantic

def insert_document_chunks(
    db: Session,
    document_id: int,
    text: str,
) -> List[DocumentChunk]:
    """
    Divide el texto de un documento en semanticos, genera embeddings para cada uno
    y los inserta en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento al que pertenecen los chunks
        text: Texto completo del documento
        chunk_size: Ya no se usa (el divisor semántico determina el tamaño)
        overlap: Ya no se usa (el divisor semántico maneja la superposición)
        
    Returns:
        Lista de objetos DocumentChunk creados
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"No existe un documento con ID {document_id}")
    
    created_chunks = process_document_and_embed_chunks_semantic(
        document_id=document_id,
        text=text,
        db=db
    )
    db.commit()
    db.refresh(document)
    print(f"Se insertaron {len(created_chunks)} chunks semánticos para el documento ID {document_id}")
    
    return created_chunks

def search_similar_chunks(db: Session,
                          query_embedding: List[float],
                          document_id: Optional[int] = None,
                          limit: int = 3,
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

def create_conversation(
    db: Session,
    document_id: int,
    user_id: int,
    user_type: str,  # "teacher" o "student"
) -> Conversation:
    """
    Crea una nueva conversación asociada a un profesor o estudiante y un documento.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento sobre el que trata la conversación
        user_id: ID del usuario (profesor o estudiante)
        user_type: Tipo de usuario ("teacher" o "student")
        
    Returns:
        Objeto Conversation creado
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if user_type == "student":
        user = db.query(Student).filter(Student.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        new_conversation = Conversation(
            student_id=user_id,
            teacher_id=None,
            document_id=document_id
        )
    elif user_type == "teacher":
        user = db.query(Teacher).filter(Teacher.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Profesor no encontrado")
        
        new_conversation = Conversation(
            student_id=None,
            teacher_id=user_id,
            document_id=document_id
        )
    else:
        raise HTTPException(status_code=400, detail="Tipo de usuario no válido. Debe ser 'teacher' o 'student'")
   
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation

def generate_conversation(
    db: Session,
    document_id: int,
    user_id: int,
    user_type: str,
    initial_message_text: str = None
) -> Tuple[str, Conversation]:
    """
    Crea una nueva conversación y opcionalmente añade el primer mensaje con su respuesta.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento sobre el que trata la conversación
        user_id: ID del usuario (profesor o estudiante)
        user_type: Tipo de usuario ("teacher" o "student")
        initial_message_text: Texto del primer mensaje (opcional)
        
    Returns:
        Tupla con (texto de respuesta, objeto Conversation creado)
    """
    new_conversation = create_conversation(db, document_id, user_id, user_type)
    
    if initial_message_text:
        user_msg, bot_msg = add_message_and_generate_response(
            db=db,
            conversation_id=new_conversation.id,
            user_id=user_id,
            user_type=user_type,
            message_text=initial_message_text
        )
        return bot_msg.text, new_conversation
    
    return "", new_conversation

def add_message_and_generate_response(
    db: Session,
    conversation_id: int,
    user_id: int,
    user_type: str,
    message_text: str,
) -> Tuple[Message, Message]:
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
    print(f"--- Debug Info: add_message_and_generate_response ---")
    # Verificar que la conversación existe
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # Verificar usuario y crear su mensaje
    question_embedding = get_embedding_for_query(message_text)
    user_msg_obj: Message = None 

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

   
    db.add(user_msg_obj)
    db.flush()
    db.refresh(user_msg_obj) 

    
    similar_chunks = search_similar_chunks(db, question_embedding, conversation.document_id) 
    similarity_threshold = 0.65
    context_chunks = [chunk.content for chunk, score in similar_chunks if score > similarity_threshold]
    context = " ".join(context_chunks)

    try:
        message_history_db = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).limit(6).all()
        message_history_db.reverse() # Orden cronológico
        conversation_history = "\n".join(
            [f"{'Usuario' if not msg.is_bot else 'Bot'}: {msg.text}" for msg in message_history_db]
        )
        response_text = generate_groq_response(message_text, context, conversation_history)
        print(f"Groq Raw Response: {response_text}") # DEBUG
    except Exception as e:
        print(f"--- ERROR calling generate_groq_response: {e} ---") # DEBUG
        
        response_text = "Lo siento, ocurrió un error al generar la respuesta."

    response_embedding = get_embedding_for_query(response_text)

    
    bot_msg_obj = Message( 
        text=response_text,
        is_bot=True,
        conversation_id=conversation_id,
        embedding=response_embedding
    )


    db.add(bot_msg_obj)

    db.commit()


    db.refresh(bot_msg_obj)


    return user_msg_obj, bot_msg_obj

def get_context(
    db: Session,
    document_id: int,
    message_text: str,
    limit: int = 5,
    similarity_metric: str = "cosine"
) -> List[Tuple[DocumentChunk, float]]:
    """
    Obtiene el contexto de un documento específico.
    
    Args:
        db: Sesión de SQLAlchemy
        document_id: ID del documento
        message_text: Texto del mensaje del usuario
        limit: Número máximo de chunks a devolver
        similarity_metric: Métrica de similitud a usar ("cosine", "l2", "inner_product")
        
    Returns:
        Lista de tuplas (DocumentChunk, score)
    """
    
    query_embedding = get_embedding_for_query(message_text)
    
    
    similar_chunks = search_similar_chunks(db, query_embedding, document_id, limit, similarity_metric)
    
    return similar_chunks