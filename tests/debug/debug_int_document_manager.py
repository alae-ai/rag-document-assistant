from app.documents.document_manager import DocumentManager

manager = DocumentManager()

print("=" * 80)
print("DOCUMENT MANAGER TEST")
print("=" * 80)

# ------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------

print("\nStatistics")
print(manager.get_statistics())

# ------------------------------------------------------------------
# Indexed documents
# ------------------------------------------------------------------

print("\nIndexed documents")

documents = manager.list_documents()

for document in documents:
    print(f" - {document}")

# ------------------------------------------------------------------
# Remove document
# ------------------------------------------------------------------

document_to_remove = "company_policy.txt"

print(f"\nRemoving '{document_to_remove}'...")

manager.remove_document(document_to_remove)

print("\nDocuments after deletion")

documents = manager.list_documents()

for document in documents:
    print(f" - {document}")

print("\nStatistics")
print(manager.get_statistics())

# ------------------------------------------------------------------
# Clear database
# ------------------------------------------------------------------

print("\nClearing database...")

manager.clear_database()

print("\nDocuments after clearing")

documents = manager.list_documents()

for document in documents:
    print(f" - {document}")

print("\nStatistics")
print(manager.get_statistics())
