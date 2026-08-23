from langchain_core.documents import Document

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TXTLoader:
    """Loads a text document from in-memory content."""

    def __init__(self, file_content: bytes, filename: str):
        self.file_content = file_content
        self.filename = filename

    def load(self):
        """Load the text document."""

        logger.info("Loading text file: %s", self.filename)

        try:
            text = self.file_content.decode("utf-8")

            documents = [
                Document(
                    page_content=text,
                    metadata={"source": self.filename},
                )
            ]

            logger.info(
                "Successfully loaded text document '%s'.",
                self.filename,
            )

            return documents

        except Exception:
            logger.exception(
                "Failed to load text file: %s",
                self.filename,
            )
            raise