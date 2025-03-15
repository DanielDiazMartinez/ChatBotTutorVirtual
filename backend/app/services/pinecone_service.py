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
    Elimina todos los vectores asociados a un documento específico.
    """

    result = index.delete(filter={"document_id": document_id}, namespace="documents")
    
    print(f"Se eliminaron {result['num_deleted']} embeddings asociados al documento {document_id}")

def get_all_vector_ids(document_id: int, namespace="documents"):
    """
    Obtiene todos los IDs de vectores asociados a un document_id en Pinecone usando paginación.
    """
    vector_ids = []
    VECTOR_DIMENSION = 384  # Ajusta esto según la dimensión de tu índice
    batch_size = 1000  # Número máximo de vectores por consulta (top_k)

    while True:
        response = index.query(
            vector=[0.0] * VECTOR_DIMENSION,  # Vector vacío con la dimensión correcta
            top_k=batch_size,  
            include_values=False,
            include_metadata=True,
            filter={"document_id": document_id},
            namespace=namespace
        )
        print(response)
        batch_ids = [match["id"] for match in response["matches"]]
        

        if not batch_ids:
            break  

        vector_ids.extend(batch_ids)

        print(f"Obtenidos {len(batch_ids)} vectores, total acumulado: {len(vector_ids)}")

        # Si la cantidad de resultados obtenidos es menor que batch_size, terminamos
        if len(batch_ids) < batch_size:
            break  

    return vector_ids

