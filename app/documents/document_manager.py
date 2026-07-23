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
