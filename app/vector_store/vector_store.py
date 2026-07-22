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
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Handles all interactions with the Qdrant vector database.
    """

    def __init__(self):
        logger.debug(
            f"Initializing Qdrant client ({QDRANT_HOST}:{QDRANT_PORT})"
        )

        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        self.embedding_model = EmbeddingModel()

    def create_collection(self):
        """
        Create the collection if it does not already exist.
        """
        try:
            collections = self.client.get_collections().collections
            existing_names = [c.name for c in collections]

            if COLLECTION_NAME in existing_names:
                logger.info(
                    f"Collection '{COLLECTION_NAME}' already exists."
                )
                return

            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(
                f"Collection '{COLLECTION_NAME}' created successfully."
            )

        except Exception:
            logger.exception(
                f"Failed to create collection '{COLLECTION_NAME}'."
            )
            raise

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
        try:
            logger.info(
                f"Generating embeddings for {len(documents)} document(s)."
            )

            texts = [doc.page_content for doc in documents]

            embeddings = self.embedding_model.embed_documents(texts)

            logger.info(
                f"Generated {len(embeddings)} embedding(s)."
            )

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

            logger.info(
                f"Inserting {len(points)} vector(s) into Qdrant."
            )

            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
            )

            logger.info(
                f"Successfully inserted {len(points)} vector(s) into Qdrant."
            )

        except Exception:
            logger.exception(
                "Failed to insert documents into Qdrant."
            )
            raise

    def count_vectors(self):
        """
        Return the number of vectors stored in the collection.
        """
        return self.client.count(
            collection_name=COLLECTION_NAME
        ).count
