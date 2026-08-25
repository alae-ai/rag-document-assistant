from unittest.mock import Mock

from app.sources.document_source import SourceDocument
from app.sources.mcp_document_source import MCPDocumentSource
from app.sync.synchronizer import Synchronizer


# --------------------------------------------------
# Mock MCP client
# --------------------------------------------------

mcp_client = Mock()

mcp_client.list_documents.return_value = [
    "existing.pdf",
    "new.pdf",
]

mcp_client.get_document.return_value = SourceDocument(
    name="new.pdf",
    content=b"new document content",
    metadata={"source": "mock_mcp"},
)


# --------------------------------------------------
# MCP source
# --------------------------------------------------

source = MCPDocumentSource(mcp_client)


# --------------------------------------------------
# Mock DocumentManager
# --------------------------------------------------

document_manager = Mock()

document_manager.list_documents.return_value = [
    "existing.pdf",
]


# --------------------------------------------------
# Synchronizer
# --------------------------------------------------

synchronizer = Synchronizer(
    source,
    document_manager,
)


# --------------------------------------------------
# Synchronize
# --------------------------------------------------

result = synchronizer.sync()


# --------------------------------------------------
# Results
# --------------------------------------------------

print("\nSynchronization result:")
print(result)

print("\nMCP calls:")
print("list_documents:", mcp_client.list_documents.call_args_list)
print("get_document:", mcp_client.get_document.call_args_list)

print("\nDocumentManager calls:")
print("add_document:", document_manager.add_document.call_args_list)
print("remove_document:", document_manager.remove_document.call_args_list)


# --------------------------------------------------
# Assertions
# --------------------------------------------------

assert result["added"] == 1
assert result["deleted"] == 0
assert result["skipped"] == 1

mcp_client.list_documents.assert_called_once()

mcp_client.get_document.assert_called_once_with(
    "new.pdf"
)

document_manager.add_document.assert_called_once_with(
    b"new document content",
    "new.pdf",
)

document_manager.remove_document.assert_not_called()

print("\nMCP synchronization test passed.")