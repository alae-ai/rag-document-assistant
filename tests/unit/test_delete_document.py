from app.documents.document_manager import DocumentManager

def test_remove_document():

    manager = DocumentManager()

    # Start from a clean database
    manager.clear_database()

    file_path = "data/tmp/company_policy.txt"
    filename = "company_policy.txt"

    # Add the document
    manager.add_document(file_path)

    # Verify it exists
    assert manager.document_exists(filename) is True

    # Remove it
    result = manager.remove_document(filename)

    # The operation should succeed
    assert result is True

    # The document should no longer exist
    assert manager.document_exists(filename) is False

    # Cleanup
    manager.clear_database()