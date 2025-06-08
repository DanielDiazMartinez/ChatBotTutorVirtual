from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, logger, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy import Tuple
from sqlalchemy.orm import Session

from ..models.models import  User, Document, Message
from ..services.chat_service import (
    delete_conversation, 
    get_conversation_by_id, 
    get_conversation_messages, 
    get_conversations_by_user_role, 
    get_current_user_conversations,
    add_message_and_generate_response,
    create_conversation,
)
from ..services.image_service import get_image_by_message

from ..core.database import get_db
from ..core.auth import require_role, get_current_user
from ..services.vector_service import (
    get_conversation_context,
    search_similar_chunks
)
from ..models.schemas import (
    APIResponse,
    ConversationCreate, 
    ConversationOut, 
    ConversationWithResponse, 
    DocumentChunkOut, 
    MessageCreate, 
    MessageOut, 
    MessagePairOut
)

chat_routes = APIRouter()

@chat_routes.post("/conversation", response_model=APIResponse)
async def create_conversation_route(
    conversation_data: ConversationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una nueva conversación
    
    Se puede proporcionar:
    - Solo subject_id: buscará en todos los documentos de esa asignatura
    """
    # Verificar que se proporcionó al menos  subject_id
    if conversation_data.subject_id is None:
        raise HTTPException(
            status_code=400, 
            detail="Se requiere subject_id para crear una conversación"
        )  

    conversation_obj = create_conversation(
        db=db,
        user_id=current_user.id,
        subject_id=conversation_data.subject_id
    )
    if not conversation_obj:
        raise HTTPException(
            status_code=500, 
            detail="Error al crear la conversación"
        )
    # Convertir el modelo ORM a un modelo Pydantic
    conversation_data = ConversationOut.model_validate(conversation_obj)
    
    # Crear un objeto ConversationWithResponse
    response_data = {
        "conversation": conversation_data,
    }

    return {
        "data": response_data,
        "message": "Conversación creada correctamente",
        "status": 200 
    }

@chat_routes.get("/me/conversations", response_model=APIResponse)
async def get_my_conversations(
    subject_id: Optional[int] = Query(None, description="ID de la asignatura para filtrar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todas las conversaciones del usuario actualmente autenticado, opcionalmente filtradas por asignatura"""
    conversations = get_current_user_conversations(db, current_user.id, current_user.role, subject_id)
    
    return {
        "data": conversations,
        "message": "Conversaciones obtenidas correctamente",
        "status": 200
    }

@chat_routes.get("/conversations/{user_id}", response_model=APIResponse)
async def get_user_conversations(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener conversaciones de un usuario"""
    # Verificar que el usuario actual puede acceder a estas conversaciones
    if current_user.id != user_id and current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para ver las conversaciones de este usuario"
        )
        
    conversations = get_conversations_by_user_role(user_id, current_user.role, db)
    if not conversations:
        return {
            "data": [],
            "message": "No se encontraron conversaciones para este usuario",
            "status": 200
        }
    return {
        "data": conversations,
        "message": "Conversaciones obtenidas correctamente",
        "status": 200
    }

@chat_routes.get("/conversation/{conversation_id}", response_model=APIResponse)
async def get_conversation(
    conversation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener una conversación específica"""
    conversation = get_conversation_by_id(conversation_id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    # Verificar que el usuario actual puede acceder a esta conversación
    if current_user.role == "student" and not conversation.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta conversación")
    elif current_user.role == "teacher":
        # Los profesores pueden ver las conversaciones de las asignaturas que imparten
        if not (conversation.user_id == current_user.id or 
                (conversation.subject_id and conversation.subject_id in 
                 [s.id for s in current_user.teaching_subjects])):
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta conversación")
        
    return {
        "data": conversation,
        "message": "Conversación obtenida correctamente",
        "status": 200
    }

@chat_routes.delete("/conversation/{conversation_id}", response_model=APIResponse)
async def delete_conv(
    conversation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar una conversación"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    # Verificar que el usuario actual puede eliminar esta conversación
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta conversación")
            
    delete_conversation(db, conversation_id)
    return {
        "data": None,
        "message": "Conversación eliminada correctamente",
        "status": 200
    }

@chat_routes.post("/c/{conversation_id}", response_model=APIResponse)
async def add_message_to_conversation(
    conversation_id: int,
    message_data: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Añadir mensaje a una conversación, opcionalmente con una imagen"""
    try:
    
        # Procesar la imagen si se proporcionó
        image_id = None
        if file:
            # Usar las funciones del image_service
            from app.services.image_service import upload_image
            image = await upload_image(
                file=file,
                user_id=current_user.id,
                subject_id=None,  
                db=db
            )
            image_id = image.id
        
        # Parsear el mensaje si fue enviado como string JSON
        message_text = None
        if message_data:
            try:
                import json
                message_obj = json.loads(message_data)
                message_text = message_obj.get("text")
                print(f"DEBUG - message_text después de json.loads: '{message_text}'")
            except json.JSONDecodeError:
                message_text = message_data
                print(f"DEBUG - Error JSON, usando message_data como texto: '{message_text}'")
        else:
            print("DEBUG - No se recibió message_data")
        
        # Validar que se proporcionó texto o archivo
        if not message_text and not image_id:
            raise HTTPException(
                status_code=400,
                detail="Se requiere proporcionar texto del mensaje o un archivo"
            )
        
        user_msg_obj, bot_msg_obj = add_message_and_generate_response(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            message_text=message_text,
            image_id=image_id
        )
        
        user_message_out = MessageOut.model_validate(user_msg_obj)
        bot_message_out = MessageOut.model_validate(bot_msg_obj)
        
        return {
            "data": {
                "user_message": user_message_out,
                "bot_message": bot_message_out
            },
            "message": "Mensaje añadido correctamente",
            "status": 200
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error procesando el mensaje")

@chat_routes.post("/context/{document_id}", response_model=APIResponse)
async def get_context_for_question(
    document_id: int, 
    db: Session = Depends(get_db), 
    message_data: MessageCreate = None,
    current_user: User = Depends(get_current_user)
):
    """Obtener contexto para una pregunta"""
    if message_data is None or message_data.text is None:
        raise HTTPException(status_code=400, detail="Message text is required")

    # Obtener el embedding para la consulta
    from ..services.embedding_service import get_embedding_for_query
    query_embedding = get_embedding_for_query(message_data.text)
    
    # Buscar chunks similares
    similar_chunks = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        document_id=document_id
    )

    context_out = [
        DocumentChunkOut.model_validate(chunk) for chunk, _ in similar_chunks
    ]

    return {
        "data": context_out,
        "message": "Contexto obtenido correctamente",
        "status": 200
    }

@chat_routes.post("/context/subject/{subject_id}", response_model=APIResponse)
async def get_subject_context_for_question(
    subject_id: int, 
    db: Session = Depends(get_db), 
    message_data: MessageCreate = None,
    current_user: User = Depends(get_current_user)
):
    """Obtener contexto para una pregunta buscando en todos los documentos de una asignatura"""
    if message_data is None or message_data.text is None:
        raise HTTPException(status_code=400, detail="Se requiere texto del mensaje")

    # Verificar que la asignatura existe
    subject = db.query(Document).filter(Document.subject_id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada o sin documentos")

    # Obtener el embedding para la consulta
    from ..services.embedding_service import get_embedding_for_query
    query_embedding = get_embedding_for_query(message_data.text)
    
    # Buscar chunks similares en todos los documentos de la asignatura
    similar_chunks = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        subject_id=subject_id
    )

    context_out = [
        DocumentChunkOut.model_validate(chunk) for chunk, _ in similar_chunks
    ]

    return {
        "data": context_out,
        "message": "Contexto obtenido correctamente",
        "status": 200
    }

@chat_routes.get("/conversation/{conversation_id}/messages", response_model=APIResponse)
async def get_conversation_message_history(
    conversation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todos los mensajes de una conversación específica"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    # Verificar que el usuario actual puede acceder a esta conversación
    if current_user.role == "student" and not conversation.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta conversación")
    elif current_user.role == "teacher":
        # Los profesores pueden ver las conversaciones de las asignaturas que imparten
        if not (conversation.user_id == current_user.id or 
                (conversation.subject_id and conversation.subject_id in 
                 [s.id for s in current_user.subjects])):
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta conversación")
    
    messages = get_conversation_messages(db, conversation_id)
    message_out_list = [MessageOut.model_validate(msg) for msg in messages]
    
    return {
        "data": message_out_list,
        "message": "Mensajes obtenidos correctamente",
        "status": 200
    }

@chat_routes.get("/messages", response_model=APIResponse)
async def get_user_messages(
    subject_id: Optional[int] = Query(None, description="Filtrar por ID de asignatura"),
    topic_id: Optional[int] = Query(None, description="Filtrar por ID de tema"),
    user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    limit: Optional[int] = Query(None, description="Límite de resultados"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "teacher"]))
):
    """Obtener todos los mensajes de usuarios con información del usuario
    
    Este endpoint devuelve todos los mensajes realizados por usuarios (no bot) 
    junto con información del usuario, asignatura y tema.
    Solo accesible para administradores y profesores.
    """
    from ..services.message_service import get_user_messages_with_filters
    
    try:
        messages_data = get_user_messages_with_filters(
            db=db,
            subject_id=subject_id,
            topic_id=topic_id,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "data": messages_data,
            "message": f"Se encontraron {len(messages_data)} mensajes",
            "status": 200
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mensajes: {str(e)}"
        )

@chat_routes.get("/messages/statistics", response_model=APIResponse)
async def get_messages_statistics(
    subject_id: Optional[int] = Query(None, description="Filtrar por ID de asignatura"),
    topic_id: Optional[int] = Query(None, description="Filtrar por ID de tema"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "teacher"]))
):
    """Obtener estadísticas sobre los mensajes de usuarios
    
    Devuelve información estadística como total de mensajes, usuarios únicos,
    y distribución por asignaturas.
    Solo accesible para administradores y profesores.
    """
    from ..services.message_service import get_messages_statistics
    
    try:
        statistics = get_messages_statistics(
            db=db,
            subject_id=subject_id,
            topic_id=topic_id
        )
        
        return {
            "data": statistics,
            "message": "Estadísticas obtenidas correctamente",
            "status": 200
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@chat_routes.get("/messages/{message_id}", response_model=APIResponse)
async def get_message_by_id(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "teacher"]))
):
    """Obtener un mensaje específico por su ID
    
    Solo accesible para administradores y profesores.
    """
    from ..services.message_service import get_message_by_id
    
    try:
        message = get_message_by_id(db=db, message_id=message_id)
        
        if not message:
            raise HTTPException(
                status_code=404,
                detail="Mensaje no encontrado"
            )
        
        return {
            "data": message,
            "message": "Mensaje obtenido correctamente",
            "status": 200
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el mensaje: {str(e)}"
        )

@chat_routes.get("/messages/recent/{limit}", response_model=APIResponse)
async def get_recent_messages(
    limit: int = 10,
    subject_id: Optional[int] = Query(None, description="Filtrar por ID de asignatura"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "teacher"]))
):
    """Obtener los mensajes más recientes
    
    Solo accesible para administradores y profesores.
    """
    from ..services.message_service import get_recent_messages
    
    try:
        if limit > 100:  # Limitar para evitar sobrecarga
            limit = 100
            
        recent_messages = get_recent_messages(
            db=db,
            limit=limit,
            subject_id=subject_id
        )
        
        return {
            "data": recent_messages,
            "message": f"Se obtuvieron los {len(recent_messages)} mensajes más recientes",
            "status": 200
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mensajes recientes: {str(e)}"
        )


