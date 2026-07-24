from pathlib import Path

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
        File
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

    def add_document(self, file_path: str):
        """
        Load, clean, chunk and index a document.

        Args:
            file_path (str): Path to the document.
        """

        logger.info("Adding document: %s", file_path)

        file_path = Path(file_path)

        if not file_path.exists():
            logger.error("Document not found: %s", file_path)
            raise FileNotFoundError(file_path)

        # -----------------------------
        # Load
        # -----------------------------

        loader = LoaderFactory.get_loader(str(file_path))
        documents = loader.load()

        # -----------------------------
        # Clean
        # -----------------------------

        documents = TextCleaner.clean_documents(documents)

        # -----------------------------
        # Chunk
        # -----------------------------

        chunks = self.chunker.split_documents(documents)

        # -----------------------------
        # Store
        # -----------------------------

        self.vector_store.add_documents(chunks)

        logger.info(
            "Document '%s' indexed successfully (%d chunks).",
            file_path.name,
            len(chunks),
        )

    def remove_document(self, document_name: str):
        """
        Remove a document from the vector database.

        Args:
            document_name (str): File name
                                (e.g. "company_policy.txt")
        """

        self.vector_store.delete_document(document_name)

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

    def replace_document(self, file_path: str):
        """
        Replace an indexed document with a new version.

        If a document with the same filename already exists,
        it is removed before indexing the new one.

        Parameters
        ----------
        file_path : str
            Path to the new document.
        """

        filename = Path(file_path).name

        logger.info(
            f"Replacing document '{filename}'."
        )

        if self.document_exists(filename):

            self.delete_document(filename)

        self.add_document(file_path)

        logger.info(
            f"Document '{filename}' replaced successfully."
        )