from app.core.pinecone import get_pinecone_index
from app.utils.document_utils import generate_embedding

index = get_pinecone_index()

def store_message_embedding(message_id: int, text: str, conversation_id: int, document_id: int, student_id: int, is_bot: bool):
    """
    Convierte un mensaje en un embedding y lo almacena en Pinecone con metadatos.
    """
    embedding = generate_embedding(text)

    metadata = {
        "conversation_id": conversation_id,
        "document_id": document_id,
        "student_id": student_id,
        "is_bot": is_bot
    }

    index.upsert(vectors=[(str(message_id), embedding, metadata)])

    print(f"Mensaje {message_id} almacenado en Pinecone con metadatos: {metadata}")

def retrieve_context(conversation_id: int, document_id: int, query_text: str, top_k=5):
    """
    Busca en Pinecone los mensajes más relevantes de una conversación y un documento.
    """
    try:
        query_embedding = generate_embedding(query_text)

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            filter={"conversation_id": conversation_id, "document_id": document_id},
            include_metadata=True
        )

        # Extraer fragmentos de texto relevantes
        context = [match["metadata"]["text"] for match in results["matches"] if "text" in match["metadata"]]

        return " ".join(context) if context else "No encontré información relevante en esta conversación."

    except Exception as e:
        print(f"Error al consultar Pinecone: {e}")
        return "Ocurrió un error al recuperar el contexto."


def delete_document_bbdd_vector(document_id: int):
    """
    Elimina todos los embeddings asociados a un documento específico.
    """
    
    # Construye el filtro para encontrar todos los vectores del documento
    filter_condition = {
        "document_id": document_id
    }
    
    # Elimina los vectores que coinciden con el filtro
    result = index.delete(filter=filter_condition)

    print(f"Se eliminaron {result['num_deleted']} embeddings asociados al documento {document_id}")
