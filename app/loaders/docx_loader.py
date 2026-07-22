from langchain_community.document_loaders import Docx2txtLoader

from app.utils.logger import get_logger

logger = get_logger(__name__)


class DOCXLoader:
    """
    Loads a Microsoft Word document using LangChain's Docx2txtLoader.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        """
        Load the Word document.

        Returns:
            list[Document]: LangChain Document objects.
        """
        logger.info(f"Loading Word document: {self.file_path}")

        try:
            loader = Docx2txtLoader(self.file_path)
            documents = loader.load()

            logger.info(
                f"Successfully loaded {len(documents)} document(s) "
                f"from '{self.file_path}'."
            )

            return documents

        except Exception:
            logger.exception(
                f"Failed to load Word document: {self.file_path}"
            )
            raise
