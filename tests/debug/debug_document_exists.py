from app.documents.document_manager import DocumentManager

def test_document_exists():

    manager = DocumentManager()

    # Start from a clean database
    manager.clear_database()

    file_path = "data/tmp/company_policy.txt"
    filename = "company_policy.txt"

    # Add the document
    manager.add_document(file_path)

    # Existing document
    assert manager.document_exists(filename) is True

    # Non-existing document
    assert manager.document_exists("NonExistingDocument.pdf") is False

    # Cleanup
    manager.clear_database()