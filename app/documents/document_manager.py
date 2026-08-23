from app.chunking.chunker import Chunker
from app.loaders.loader_factory import LoaderFactory
from app.utils.text_cleaner import TextCleaner
from app.vector_store.vector_store import VectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentManager:
    """
    Handles the complete document ingestion pipeline.

    Pipeline:
        Document content
            ↓
        LoaderFactory
            ↓
        TextCleaner
            ↓
        Chunker
            ↓
        VectorStore
    """

    def __init__(self):
        self.chunker = Chunker()
        self.vector_store = VectorStore()

    def add_document(self, file_content: bytes, filename: str):
        """
        Load, clean, chunk and index a document.

        Args:
            file_content: Document content in bytes.
            filename: Document filename.
        """

        logger.info("Adding document: %s", filename)

        # --------------------------------
        # Validate content
        # --------------------------------

        if not file_content:
            logger.error(
                "Document '%s' is empty.",
                filename,
            )
            raise ValueError(
                f"Document '{filename}' is empty."
            )

        # --------------------------------
        # Duplicate check
        # --------------------------------

        if self.document_exists(filename):
            logger.warning(
                "Document '%s' already exists.",
                filename,
            )
            return False

        try:
            # --------------------------------
            # Load
            # --------------------------------

            loader = LoaderFactory.get_loader(
                file_content,
                filename,
            )

            documents = loader.load()

            # --------------------------------
            # Clean
            # --------------------------------

            documents = TextCleaner.clean_documents(
                documents
            )

            # --------------------------------
            # Chunk
            # --------------------------------

            chunks = self.chunker.split_documents(
                documents
            )

            # --------------------------------
            # Store
            # --------------------------------

            self.vector_store.add_documents(chunks)

            logger.info(
                "Document '%s' indexed successfully (%d chunks).",
                filename,
                len(chunks),
            )

            return True

        except Exception:
            logger.exception(
                "Failed to index document '%s'.",
                filename,
            )
            raise

    def remove_document(self, document_name: str):
        """
        Remove a document from the vector database.

        Args:
            document_name: Document filename.
        """

        logger.info(
            "Removing document '%s'.",
            document_name,
        )

        self.vector_store.delete_document(
            document_name
        )

        logger.info(
            "Document '%s' removed successfully.",
            document_name,
        )

        return True

    def document_exists(self, filename: str) -> bool:
        """
        Check whether a document is already indexed.

        Args:
            filename: Document filename.

        Returns:
            bool: True if document exists, False otherwise.
        """

        return self.vector_store.document_exists(
            filename
        )

    def list_documents(self):
        """
        Return all indexed documents.
        """

        return self.vector_store.list_documents()

    def clear_database(self):
        """
        Remove every indexed document.
        """

        self.vector_store.clear_collection()

    def get_statistics(self):
        """
        Return document database statistics.
        """

        return self.vector_store.get_statistics()

    def replace_document(
        self,
        file_content: bytes,
        filename: str,
    ):
        """
        Replace an indexed document with new content.

        The existing vectors are deleted and the new
        document is indexed.
        """

        logger.info(
            "Replacing document '%s'.",
            filename,
        )

        try:
            if self.document_exists(filename):
                self.remove_document(filename)

            result = self.add_document(
                file_content,
                filename,
            )

            if not result:
                logger.warning(
                    "Document '%s' was not replaced.",
                    filename,
                )
                return False

            logger.info(
                "Document '%s' replaced successfully.",
                filename,
            )

            return True

        except Exception:
            logger.exception(
                "Failed to replace document '%s'.",
                filename,
            )
            raise