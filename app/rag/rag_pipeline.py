from app.llm.llm import LLM
from app.prompting.prompt_builder import PromptBuilder
from app.retrieval.retriever import Retriever

from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """
    Orchestrates the complete Retrieval-Augmented Generation (RAG) pipeline.

    Pipeline:
        User Question
            ↓
        Retrieval
            ↓
        Prompt Building
            ↓
        LLM
            ↓
        Response
    """

    def __init__(self):
        self.retriever = Retriever()
        self.prompt_builder = PromptBuilder()
        self.llm = LLM()

    def ask(self, question: str):
        """
        Answer a user question using the RAG pipeline.

        Args:
            question (str): User question.

        Returns:
            tuple[str, list]:
                - Generated answer.
                - Retrieved source chunks.
        """

        logger.info("Starting RAG pipeline.")

        try:
            # Retrieve relevant chunks
            chunks = self.retriever.retrieve(question)

            # Build prompt
            prompt = self.prompt_builder.build(
                question=question,
                retrieved_chunks=chunks,
            )

            # Generate response
            answer = self.llm.generate(prompt)

            logger.info("RAG pipeline completed successfully.")

            return answer, chunks

        except Exception:
            logger.exception("RAG pipeline failed.")
            raise
