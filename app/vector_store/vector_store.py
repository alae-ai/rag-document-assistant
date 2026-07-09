from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from app.embeddings.embedding_model import EmbeddingModel
from app.vector_store.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    VECTOR_SIZE,
)


class VectorStore:
    """
    Handles all interactions with the Qdrant vector database.
    """

    def __init__(self):
        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        self.embedding_model = EmbeddingModel()

    def create_collection(self):
        """
        Create the collection if it does not already exist.
        """

        collections = self.client.get_collections().collections
        existing_names = [c.name for c in collections]

        if COLLECTION_NAME in existing_names:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
            return

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        print(f"Collection '{COLLECTION_NAME}' created successfully.")

    def list_collections(self):
        """
        Return all existing collections.
        """

        collections = self.client.get_collections().collections

        return [c.name for c in collections]

    def add_documents(self, documents):
        """
        Generate embeddings and insert documents into Qdrant.

        Args:
            documents (list[Document]): LangChain documents.
        """

        texts = [doc.page_content for doc in documents]

        embeddings = self.embedding_model.embed_documents(texts)

        points = []

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):

            point = PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", ""),
                    "chunk_id": i,
                },
            )

            points.append(point)

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        print(f"Inserted {len(points)} chunks into Qdrant.")

    def count_vectors(self):
        """
        Return the number of vectors stored in the collection.
        """

        result = self.client.count(
            collection_name=COLLECTION_NAME
        )

        return result.count

    def count_vectors(self):
        """
        Return the number of vectors stored in the collection.
        
        """
        
        result = self.client.count(
            collection_name=COLLECTION_NAME
        )
        
        return result.count
