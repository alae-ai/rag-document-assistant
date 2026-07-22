from langchain_community.document_loaders import PyPDFLoader

from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFLoader:
    """
    Loads a PDF document using LangChain's PyPDFLoader.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        """
        Load the PDF document.

        Returns:
            list[Document]: LangChain Document objects.
        """
        logger.info(f"Loading PDF file: {self.file_path}")

        try:
            loader = PyPDFLoader(self.file_path)
            documents = loader.load()

            logger.info(
                f"Successfully loaded {len(documents)} page(s) "
                f"from '{self.file_path}'."
            )

            return documents

        except Exception:
            logger.exception(
                f"Failed to load PDF file: {self.file_path}"
            )
            raise
