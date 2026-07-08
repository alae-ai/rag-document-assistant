from langchain_ollama import OllamaEmbeddings

from app.embeddings.config import EMBEDDING_MODEL


class EmbeddingModel:
    """
    Wrapper around the Ollama embedding model.
    Responsible for generating vector embeddings from text.
    """

    def __init__(self):
        self.embedding_model = OllamaEmbeddings(
            model=EMBEDDING_MODEL
        )

    def embed_documents(self, texts):
        """
        Generate embeddings for a list of text chunks.

        Args:
            texts (list[str]): List of chunk texts.

        Returns:
            list[list[float]]: List of embedding vectors.
        """
        return self.embedding_model.embed_documents(texts)

    def embed_query(self, query):
        """
        Generate an embedding for a user query.

        Args:
            query (str): User question.

        Returns:
            list[float]: Query embedding.
        """
        return self.embedding_model.embed_query(query)
