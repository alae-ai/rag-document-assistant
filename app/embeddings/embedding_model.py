from langchain_ollama import OllamaEmbeddings

from app.embeddings.config import EMBEDDING_MODEL
from app.utils.logger import get_logger

logger = get_logger(__name__)


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
        try:
            return self.embedding_model.embed_documents(texts)

        except Exception:
            logger.exception(
                "Failed to generate document embeddings using model '%s'.",
                EMBEDDING_MODEL,
            )
            raise RuntimeError(
                "Unable to generate embeddings. "
                "Please verify that Ollama is running and that the "
                f"'{EMBEDDING_MODEL}' model is installed."
            )

    def embed_query(self, query):
        """
        Generate an embedding for a user query.

        Args:
            query (str): User question.

        Returns:
            list[float]: Query embedding.
        """
        try:
            return self.embedding_model.embed_query(query)

        except Exception:
            logger.exception(
                "Failed to generate query embedding."
            )
            raise RuntimeError(
                "Unable to generate the query embedding. "
                "Please verify that Ollama is running."
            )