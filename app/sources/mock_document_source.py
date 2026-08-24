from app.sources.document_source import DocumentSource, SourceDocument


class MockDocumentSource(DocumentSource):
    """
    Simple document source used for testing the synchronization flow.
    """

    def __init__(self, documents=None):
        self.documents = documents or []

    def list_documents(self) -> list[SourceDocument]:
        return self.documents