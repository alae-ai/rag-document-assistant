from pathlib import Path

from app.loaders.pdf_loader import PDFLoader
from app.loaders.docx_loader import DOCXLoader
from app.loaders.txt_loader import TXTLoader

from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoaderFactory:
    """
    Factory responsible for selecting the appropriate document loader
    based on the file extension.
    """

    @staticmethod
    def get_loader(file_path: str): 
        """
        Return the appropriate loader for the given file.

        Args:
            file_path (str): Path to the document.

        Returns:
            PDFLoader | DOCXLoader | TXTLoader

        Raises:
            ValueError: If the file type is not supported.
        """
        extension = Path(file_path).suffix.lower()

        logger.debug(
            f"Selecting loader for '{file_path}' "
            f"(extension: {extension})"
        )

        if extension == ".pdf":
            return PDFLoader(file_path)

        if extension == ".docx":
            return DOCXLoader(file_path)

        if extension == ".txt":
            return TXTLoader(file_path)

        logger.error(
            f"Unsupported file type: '{extension}' "
            f"for file '{file_path}'."
        )

        raise ValueError(
            f"Unsupported file type: {extension}"
        )
