from app.rag.rag_pipeline import RAGPipeline
from app.documents.document_manager import DocumentManager


def test_rag_pipeline():

    manager = DocumentManager()
    
    # Start from a clean database
    manager.clear_database()

    file_path = "data/tmp/company_policy.txt"
    filename = "company_policy.txt"

    # Add the document
    manager.add_document(file_path)

    pipeline = RAGPipeline()

    question = "What is the company policy?"

    answer, chunks = pipeline.ask(question)

    # The pipeline should return a non-empty answer
    assert isinstance(answer, str)
    assert len(answer.strip()) > 0

    # Retrieved chunks
    assert isinstance(chunks, list)
    assert len(chunks) > 0

    # Every retrieved chunk should contain the expected payload
    for chunk in chunks:

        assert chunk.payload is not None

        assert "text" in chunk.payload
        assert "source" in chunk.payload
        assert "chunk_id" in chunk.payload

        assert isinstance(chunk.payload["text"], str)
        assert len(chunk.payload["text"]) > 0