from app.documents.document_manager import DocumentManager


def test_list_documents():

    manager = DocumentManager()

    # Start from a clean database
    manager.clear_database()

    file_path = "data/tmp/Travel and Expense Policy.pdf"
    filename = "Travel and Expense Policy.pdf"

    # Add the document
    manager.add_document(file_path)

    # Retrieve indexed documents
    documents = manager.list_documents()

    # The document should be present
    assert filename in documents

    # At least one document should be indexed
    assert len(documents) >= 1

    # Cleanup
    manager.clear_database()