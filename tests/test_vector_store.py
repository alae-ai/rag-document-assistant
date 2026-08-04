from app.vector_store.vector_store import VectorStore


def test_create_collection():

    vector_store = VectorStore()

    vector_store.create_collection()

    collections = vector_store.list_collections()

    assert "company_documents" in collections


def test_list_collections():

    vector_store = VectorStore()

    collections = vector_store.list_collections()

    assert isinstance(collections, list)
    assert "company_documents" in collections


def test_count_vectors():

    vector_store = VectorStore()

    count = vector_store.count_vectors()

    assert isinstance(count, int)
    assert count >= 0


def test_document_exists():

    vector_store = VectorStore()

    exists = vector_store.document_exists(
        "Travel and Expense Policy.pdf"
    )

    assert isinstance(exists, bool)


def test_list_documents():

    vector_store = VectorStore()

    documents = vector_store.list_documents()

    assert isinstance(documents, list)

    for document in documents:
        assert isinstance(document, str)


def test_get_statistics():

    vector_store = VectorStore()

    statistics = vector_store.get_statistics()

    assert isinstance(statistics, dict)

    assert "documents" in statistics
    assert "vectors" in statistics

    assert isinstance(statistics["documents"], int)
    assert isinstance(statistics["vectors"], int)


def test_clear_collection():

    vector_store = VectorStore()

    vector_store.clear_collection()

    assert vector_store.count_vectors() == 0