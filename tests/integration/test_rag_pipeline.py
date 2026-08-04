from app.rag.rag_pipeline import RAGPipeline


def test_rag_pipeline():

    pipeline = RAGPipeline()

    question = "What is the travel policy?"

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