from app.retrieval.retriever import Retriever
from app.documents.document_manager import DocumentManager



def test_retriever():

    retriever = Retriever()
    manager = DocumentManager()
    
    # Start from a clean database
    manager.clear_database()

    file_path = "data/tmp/company_policy.txt"
    filename = "company_policy.txt"

    # Add the document
    manager.add_document(file_path)

    query = "How many remote work days are employees allowed?"

    results = retriever.retrieve(query)

    # Retrieval should return a list of results
    assert isinstance(results, list)

    # At least one relevant chunk should be retrieved
    assert len(results) > 0

    # Every result should contain the expected information
    for result in results:

        assert result.score is not None
        assert result.payload is not None

        assert "source" in result.payload
        assert "text" in result.payload
        assert "chunk_id" in result.payload

        assert isinstance(result.payload["text"], str)
        assert len(result.payload["text"]) > 0