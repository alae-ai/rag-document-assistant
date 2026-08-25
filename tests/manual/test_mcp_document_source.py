from unittest.mock import Mock

from app.sources.mcp_document_source import MCPDocumentSource


client = Mock()

client.list_documents.return_value = [
    "contract.pdf",
    "policy.docx",
]

client.get_document.return_value = b"fake document content"


source = MCPDocumentSource(client)


# Test list_documents()
documents = source.list_documents()

print("Documents:")
print(documents)


# Test get_document()
content = source.get_document("contract.pdf")

print("\nDocument content:")
print(content)


# Verify calls
client.list_documents.assert_called_once()
client.get_document.assert_called_once_with("contract.pdf")

print("\nMCPDocumentSource test passed.")