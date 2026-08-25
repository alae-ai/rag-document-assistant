from app.sources.document_source import (
    DocumentSource,
    SourceDocument,
)
from app.utils.logger import get_logger


logger = get_logger(__name__)


class MCPDocumentSource(DocumentSource):
    """
    Document source backed by an MCP server.
    """

    def __init__(self, client):
        self.client = client

    def list_documents(self) -> list[str]:
        """
        Return documents available through the MCP server.
        """
        logger.info("Listing documents from MCP source.")

        return self.client.list_documents()

    def get_document(self, name: str) -> SourceDocument:
        """
        Retrieve a document from the MCP server.

        Args:
            name: Document name.

        Returns:
            Document content as bytes.
        """
        logger.info(
            "Retrieving document '%s' from MCP source.",
            name,
        )

        return self.client.get_document(name)