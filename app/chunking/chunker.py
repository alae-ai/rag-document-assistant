from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.chunking.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SEPARATORS,
)


class Chunker:
    """
    Splits LangChain Document objects into smaller chunks.
    """

    def __init__(
        self,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=SEPARATORS,
        )

    def split_documents(self, documents):
        """
        Split a list of LangChain Documents into chunks.
        """
        return self.text_splitter.split_documents(documents)
