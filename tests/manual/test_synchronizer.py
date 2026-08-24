from unittest.mock import Mock

from app.sources.document_source import SourceDocument
from app.sources.mock_document_source import MockDocumentSource
from app.sync.synchronizer import Synchronizer


# --------------------------------------------------
# Mock source
# --------------------------------------------------

source = MockDocumentSource(
    [
        SourceDocument(
            name="existing.pdf",
            content=b"existing document content",
            metadata={"source": "mock"},
        ),
        SourceDocument(
            name="new.pdf",
            content=b"new document content",
            metadata={"source": "mock"},
        ),
    ]
)


# --------------------------------------------------
# Mock DocumentManager
# --------------------------------------------------

document_manager = Mock()

# Currently indexed documents
document_manager.list_documents.return_value = [
    "existing.pdf",
    "old.pdf",
]


# --------------------------------------------------
# Synchronization
# --------------------------------------------------

synchronizer = Synchronizer(
    source=source,
    document_manager=document_manager,
)

result = synchronizer.sync()


# --------------------------------------------------
# Results
# --------------------------------------------------

print("\nSynchronization result:")
print(result)

print("\nAdded documents:")

for call in document_manager.add_document.call_args_list:
    print(call)

print("\nDeleted documents:")

for call in document_manager.remove_document.call_args_list:
    print(call)