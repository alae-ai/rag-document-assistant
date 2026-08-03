from app.embeddings.embedding_model import EmbeddingModel


def test_embeddings():

    embedding_model = EmbeddingModel()

    texts = [
        "Employees may work remotely two days per week.",
        "The company provides laptops to all employees.",
    ]

    embeddings = embedding_model.embed_documents(texts)

    # One embedding should be generated for each input text.
    assert len(embeddings) == len(texts)

    # Embeddings should have the expected dimension.
    assert len(embeddings[0]) == 768

    # All embeddings should have the same dimension.
    assert all(
        len(embedding) == 768
        for embedding in embeddings
    )

    # Embeddings should not be empty.
    assert embeddings[0] is not None