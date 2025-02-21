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
