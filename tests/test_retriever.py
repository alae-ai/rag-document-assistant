from app.retrieval.retriever import Retriever


def test_retriever():

    retriever = Retriever()

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