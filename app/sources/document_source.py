from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SourceDocument:
    """
    Represents a document provided by an external source.

    Attributes:
        name: Document filename or identifier.
        content: Raw document content as bytes.
        metadata: Additional information provided by the source.
    """

    name: str
    content: bytes
    metadata: dict = field(default_factory=dict)


class DocumentSource(ABC):
    """
    Abstract interface for document sources.

    A document source is responsible for providing documents
    to the ingestion pipeline. It does not handle indexing,
    chunking, embeddings, or vector storage.
    """

    @abstractmethod
    def list_documents(self) -> list[SourceDocument]:
        """
        Return all documents currently available from the source.

        Returns:
            List of available source documents.
        """
        pass