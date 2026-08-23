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


class VectorStore:
    """
    Handles all interactions with the Qdrant vector database.
    """

    def __init__(self):
        logger.debug(
            "Initializing Qdrant client (%s:%s)",
            QDRANT_HOST,
            QDRANT_PORT,
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
            existing_names = [collection.name for collection in collections]

            if COLLECTION_NAME in existing_names:
                logger.info(
                    "Collection '%s' already exists.",
                    COLLECTION_NAME,
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
                "Collection '%s' created successfully.",
                COLLECTION_NAME,
            )

        except Exception:
            logger.exception(
                "Failed to create collection '%s'.",
                COLLECTION_NAME,
            )
            raise

    def list_collections(self):
        """
        Return all existing collections.
        """

        try:
            collections = self.client.get_collections().collections
            return [collection.name for collection in collections]

        except Exception:
            logger.exception("Failed to list collections.")
            raise

    def add_documents(self, documents):
        """
        Generate embeddings and insert documents into Qdrant.

        Args:
            documents: List of LangChain Document objects.
        """

        try:
            logger.info(
                "Generating embeddings for %d document(s).",
                len(documents),
            )

            texts = [document.page_content for document in documents]

            embeddings = self.embedding_model.embed_documents(texts)

            logger.info(
                "Generated %d embedding(s).",
                len(embeddings),
            )

            points = []

            for chunk_id, (document, embedding) in enumerate(
                zip(documents, embeddings)
            ):
                source = document.metadata.get(
                    "source",
                    "unknown",
                )

                # Store only the document name, never the
                # temporary/local filesystem path.
                source = str(source).split("/")[-1].split("\\")[-1]

                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": document.page_content,
                        "source": source,
                        "chunk_id": chunk_id,
                    },
                )

                points.append(point)

            logger.info(
                "Inserting %d vector(s) into Qdrant.",
                len(points),
            )

            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
            )

            logger.info(
                "Successfully inserted %d vector(s) into Qdrant.",
                len(points),
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
            source: Document name.

        Returns:
            True if the document exists, otherwise False.
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
                "Document '%s' exists: %s.",
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

            points, _ = self.client.scroll(
                collection_name=COLLECTION_NAME,
                with_payload=True,
                with_vectors=False,
                limit=10000,
            )

            for point in points:
                source = point.payload.get("source")

                if source:
                    documents.add(source)

            documents = sorted(documents)

            logger.info(
                "Found %d indexed document(s).",
                len(documents),
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
            source: Document name stored in the payload.
        """

        try:
            logger.info(
                "Deleting document '%s'.",
                source,
            )

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

            logger.info(
                "Document '%s' deleted successfully.",
                source,
            )

        except Exception:
            logger.exception(
                "Failed to delete document '%s'.",
                source,
            )
            raise

    def get_statistics(self):
        """
        Return collection statistics.
        """

        try:
            logger.info(
                "Collecting vector store statistics."
            )

            statistics = {
                "documents": len(self.list_documents()),
                "vectors": self.count_vectors(),
            }

            logger.info(
                "Statistics: %s",
                statistics,
            )

            return statistics

        except Exception:
            logger.exception(
                "Failed to retrieve vector store statistics."
            )
            raise