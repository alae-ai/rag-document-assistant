from pathlib import Path

from app.loaders.pdf_loader import PDFLoader
from app.loaders.docx_loader import DOCXLoader
from app.loaders.txt_loader import TXTLoader


class LoaderFactory:

    @staticmethod
    def get_loader(file_path: str):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return PDFLoader(file_path)

        elif extension == ".docx":
            return DOCXLoader(file_path)

        elif extension == ".txt":
            return TXTLoader(file_path)

        else:
            raise ValueError(f"Unsupported file type: {extension}")
