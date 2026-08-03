from app.loaders.loader_factory import LoaderFactory


def test_loader():

    loader = LoaderFactory.get_loader(
        "data/raw/Travel and Expense Policy.pdf"
    )

    documents = loader.load()

    # At least one document should be loaded.
    assert len(documents) > 0

    # The loaded document should not be empty.
    assert documents[0].page_content.strip() != ""

    # Metadata should contain the source.
    assert "source" in documents[0].metadata

    # The source should correspond to the loaded file.
    assert (
        documents[0].metadata["source"].endswith(
            "Travel and Expense Policy.pdf"
        )
    )

    print("test_loader passed")