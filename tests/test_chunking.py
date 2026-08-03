from app.loaders.loader_factory import LoaderFactory
from app.utils.text_cleaner import TextCleaner
from app.chunking.chunker import Chunker


def test_chunking():

    # Load document
    loader = LoaderFactory.get_loader(
        "data/raw/company_policy.txt"
    )
    documents = loader.load()

    # Clean document
    documents = TextCleaner.clean_documents(documents)

    # Chunk document
    chunker = Chunker()
    chunks = chunker.split_documents(documents)

    # At least one chunk should be created.
    assert len(chunks) > 0

    # Every chunk should contain text.
    assert all(
        chunk.page_content.strip() != ""
        for chunk in chunks
    )

    # Metadata should be preserved.
    assert all(
        "source" in chunk.metadata
        for chunk in chunks
    )

    # Chunking should never reduce to zero chunks.
    assert len(chunks) >= len(documents)

    print("✓ test_chunking passed")