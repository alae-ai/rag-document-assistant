import re

from langchain_core.documents import Document

from app.utils.logger import get_logger

logger = get_logger(__name__)

class TextCleaner:
    """
    Cleans extracted document text while preserving its meaning.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean raw extracted text while preserving its semantic content.

        Args:
            text (str): Raw extracted text.

        Returns:
            str: Cleaned text.
        """

        original_length = len(text)

        # --------------------------------------------------
        # Normalize line endings
        # --------------------------------------------------

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # --------------------------------------------------
        # Replace tabs and non-breaking spaces
        # --------------------------------------------------

        text = text.replace("\t", " ")
        text = text.replace("\u00A0", " ")

        # --------------------------------------------------
        # Remove invisible Unicode characters
        # --------------------------------------------------

        text = re.sub(
            r"[\u200B-\u200D\uFEFF]",
            "",
            text,
        )

        # --------------------------------------------------
        # Normalize quotation marks
        # --------------------------------------------------

        text = (
            text.replace("“", '"')
                .replace("”", '"')
                .replace("‘", "'")
                .replace("’", "'")
        )

        # --------------------------------------------------
        # Normalize dashes
        # --------------------------------------------------

        text = (
            text.replace("–", "-")
                .replace("—", "-")
        )

        # --------------------------------------------------
        # Merge words split by line breaks
        #
        # Example:
        # organi-
        # zation
        # ->
        # organization
        # --------------------------------------------------

        text = re.sub(
            r"(\w)-\n(\w)",
            r"\1\2",
            text,
        )

        # --------------------------------------------------
        # Remove trailing spaces on each line
        # --------------------------------------------------

        text = re.sub(
            r"[ \t]+\n",
            "\n",
            text,
        )

        # --------------------------------------------------
        # Trim every line
        # --------------------------------------------------

        lines = [line.strip() for line in text.split("\n")]

        text = "\n".join(lines)

        # --------------------------------------------------
        # Collapse multiple spaces
        # --------------------------------------------------

        text = re.sub(
            r"[ ]{2,}",
            " ",
            text,
        )

        # --------------------------------------------------
        # Collapse excessive blank lines
        # --------------------------------------------------

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        # --------------------------------------------------
        # Remove leading/trailing whitespace
        # --------------------------------------------------

        text = text.strip()

        logger.debug(
            "Text cleaned (%d → %d characters).",
            original_length,
            len(text),
        )

        return text

    @staticmethod
    def clean_documents(documents: list[Document]) -> list[Document]:
        """
        Clean a list of LangChain Document objects.

        Args:
            documents (list[Document]): Documents to clean.

        Returns:
            list[Document]: Cleaned documents.
        """

        if not documents:
            logger.info("No documents to clean.")
            return []

        logger.info(
            "Cleaning %d document(s)...",
            len(documents),
        )

        cleaned_documents = [
            Document(
                page_content=TextCleaner.clean_text(doc.page_content),
                metadata=doc.metadata,
            )
            for doc in documents
        ]

        logger.info("Document cleaning completed.")

        return cleaned_documents
