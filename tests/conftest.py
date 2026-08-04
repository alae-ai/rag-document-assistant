import pytest

from app.vector_store.vector_store import VectorStore


@pytest.fixture(scope="session", autouse=True)
def setup_qdrant():

    store = VectorStore()

    store.create_collection()

    yield
