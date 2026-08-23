from io import BytesIO

from pypdf import PdfReader

from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFLoader:
    """Loads a PDF document from in-memory content."""

    def __init__(self, file_content: bytes, filename: str):
        self.file_content = file_content
        self.filename = filename

    def load(self):
        """Load the PDF document."""

        logger.info("Loading PDF file: %s", self.filename)

        try:
            reader = PdfReader(BytesIO(self.file_content))

            documents = []

            for page_number, page in enumerate(reader.pages):
                from langchain_core.documents import Document

                documents.append(
                    Document(
                        page_content=page.extract_text() or "",
                        metadata={
                            "source": self.filename,
                            "page": page_number,
                        },
                    )
                )

            logger.info(
                "Successfully loaded %d page(s) from '%s'.",
                len(documents),
                self.filename,
            )

            return documents

        except Exception:
            logger.exception(
                "Failed to load PDF file: %s",
                self.filename,
            )
            raise