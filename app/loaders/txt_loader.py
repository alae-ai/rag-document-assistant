from langchain_community.document_loaders import TextLoader

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TXTLoader:
    """
    Loads a text document using LangChain's TextLoader.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        """
        Load the text document.

        Returns:
            list[Document]: LangChain Document objects.
        """
        logger.info(f"Loading text file: {self.file_path}")

        try:
            loader = TextLoader(self.file_path)
            documents = loader.load()

            logger.info(
                f"Successfully loaded {len(documents)} document(s) "
                f"from '{self.file_path}'."
            )

            return documents

        except Exception:
            logger.exception(
                f"Failed to load text file: {self.file_path}"
            )
            raise
