from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    FilterSelector,
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

from pathlib import Path


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

        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]

        except Exception:
            logger.exception("Failed to list collections.")
            raise

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
                        "source": Path(doc.metadata.get("source", "")).name,
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
        try:
            return self.client.count(
                collection_name=COLLECTION_NAME
            ).count

        except Exception:
            logger.exception(
                "Failed to count vectors."
            )
            raise

    def document_exists(self, source: str) -> bool:
        """
        Check whether a document is already indexed.

        Args:
            source (str): Document filename.

        Returns:
            bool: True if the document exists, False otherwise.
        """

        try:
            records, _ = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source",
                            match=MatchValue(value=source),
                        )
                    ]
                ),
                limit=1,
                with_payload=False,
                with_vectors=False,
            )

            exists = len(records) > 0

            logger.info(
                "Document '%s' exists: %s",
                source,
                exists,
            )

            return exists

        except Exception:
            logger.exception(
                "Failed to check if document '%s' exists.",
                source,
            )
            raise
        
    def clear_collection(self):
        """
        Remove all vectors from the collection while keeping
        the collection itself.
        """

        try:
            logger.warning(
                "Removing all vectors from collection '%s'.",
                COLLECTION_NAME,
            )

            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=FilterSelector(
                    filter=Filter()
                ),
            )

            logger.info(
                "Collection '%s' has been cleared.",
                COLLECTION_NAME,
            )

        except Exception:
            logger.exception(
                "Failed to clear collection '%s'.",
                COLLECTION_NAME,
            )
            raise

    def list_documents(self):
        """
        Return a sorted list of indexed document sources.
        """
        try:
            logger.info("Listing indexed documents.")

            documents = set()

            scroll_result = self.client.scroll(
                collection_name=COLLECTION_NAME,
                with_payload=True,
                with_vectors=False,
                limit=10000,
            )

            points = scroll_result[0]

            for point in points:
                source = point.payload.get("source")

                if source:
                    documents.add(source)

            documents = sorted(documents)

            logger.info(
                f"Found {len(documents)} indexed document(s)."
            )

            return documents

        except Exception:
            logger.exception(
                "Failed to list indexed documents."
            )
            raise

    def delete_document(self, source: str):
        """
        Delete all vectors belonging to a document.

        Args:
            source (str): Document name stored in the payload
                        (e.g. "company_policy.txt").
        """
        try:
            logger.info(f"Deleting document '{source}'.")

            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="source",
                                match=MatchValue(value=source),
                            )
                        ]
                    )
                ),
            )

            logger.info(f"Document '{source}' deleted successfully.")

        except Exception:
            logger.exception(
                f"Failed to delete document '{source}'."
            )
            raise
        
    def get_statistics(self):
        """
        Return collection statistics.
        """
        try:
            logger.info("Collecting vector store statistics.")

            statistics = {
                "documents": len(self.list_documents()),
                "vectors": self.count_vectors(),
            }

            logger.info(
                f"Statistics: {statistics}"
            )

            return statistics

        except Exception:
            logger.exception(
                "Failed to retrieve vector store statistics."
            )
            raise