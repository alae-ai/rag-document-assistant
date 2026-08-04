from app.documents.document_manager import DocumentManager

def test_get_statistics():

    manager = DocumentManager()

    file_path = "data/tmp/Travel and Expense Policy.pdf"

    # Start from a clean database
    manager.clear_database()

    # Add a document
    manager.add_document(file_path)

    # Get statistics
    statistics = manager.get_statistics()

    # The returned object should be a dictionary
    assert isinstance(statistics, dict)

    # Expected keys
    assert "documents" in statistics
    assert "vectors" in statistics

    # One document should be indexed
    assert statistics["documents"] == 1

    # At least one vector should exist
    assert statistics["vectors"] > 0

    # Cleanup
    manager.clear_database()