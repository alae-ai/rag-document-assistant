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
            file_path: Path to the temporary document.

        Returns:
            PDFLoader | DOCXLoader | TXTLoader

        Raises:
            ValueError: If the file type is not supported.
        """

        extension = Path(file_path).suffix.lower()

        logger.debug(
            "Selecting loader for '%s' (extension: %s)",
            file_path,
            extension,
        )

        loaders = {
            ".pdf": PDFLoader,
            ".docx": DOCXLoader,
            ".txt": TXTLoader,
        }

        loader_class = loaders.get(extension)

        if loader_class is None:
            logger.error(
                "Unsupported file type: '%s' for file '%s'.",
                extension,
                file_path,
            )
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return loader_class(file_path)