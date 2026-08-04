from app.documents.document_manager import DocumentManager

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

