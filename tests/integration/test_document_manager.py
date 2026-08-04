from app.documents.document_manager import DocumentManager


def test_add_document():

    manager = DocumentManager()

    # Start from a clean database
    manager.clear_database()

    file_path = "data/tmp/company_policy.txt"
    filename = "company_policy.txt"

    # Add the document
    result = manager.add_document(file_path)

    # The operation should succeed
    assert result is True

    # The document should now exist
    assert manager.document_exists(filename) is True

    # Cleanup
    manager.clear_database()

    
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

def test_replace_document():

    manager = DocumentManager()

    file_path = "data/tmp/Travel and Expense Policy.pdf"
    filename = "Travel and Expense Policy.pdf"

    # Start from a clean database
    manager.clear_database()

    # Add the document
    manager.add_document(file_path)

    # Number of documents before replacement
    before = manager.get_statistics()["documents"]

    # Replace the document
    manager.replace_document(file_path)

    # It should still exist
    assert manager.document_exists(filename) is True

    # Replacement should not create a new document
    after = manager.get_statistics()["documents"]

    assert after == before

    # Cleanup
    manager.clear_database()

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

def test_clear_database():

    manager = DocumentManager()

    file_path = "data/tmp/Travel and Expense Policy.pdf"

    # Start from a clean database
    manager.clear_database()

    # Add a document
    manager.add_document(file_path)

    # Database should not be empty
    assert len(manager.list_documents()) > 0

    # Clear the database
    manager.clear_database()

    # Database should now be empty
    assert manager.list_documents() == []


