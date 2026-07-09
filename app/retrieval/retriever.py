from app.embeddings.embedding_model import EmbeddingModel
from app.vector_store.vector_store import VectorStore
from app.vector_store.config import COLLECTION_NAME
from app.retrieval.config import TOP_K


class Retriever:
    """
    Retrieves the most relevant document chunks
    from the vector database.
    """

    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

    def retrieve(self, query):
        """
        Retrieve the Top-K most relevant chunks.

        Args:
            query (str): User question.

        Returns:
            list: Search results from Qdrant.
        """

        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)

        # Search Qdrant
        results = self.vector_store.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=TOP_K,
            with_payload=True,
        )

        return results.points
