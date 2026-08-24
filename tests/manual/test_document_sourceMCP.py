from app.sources.mock_document_source import MockDocumentSource
from app.sources.document_source import SourceDocument


source = MockDocumentSource([
    SourceDocument(
        name="contract.pdf",
        content=b"fake pdf content",
        metadata={"source": "mock"},
    )
])

documents = source.list_documents()

for document in documents:
    print(document.name)
    print(document.content)
    print(document.metadata)