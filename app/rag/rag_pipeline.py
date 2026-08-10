from app.llm.llm import LLM
from app.prompting.prompt_builder import PromptBuilder
from app.retrieval.retriever import Retriever

from app.conversation.intent_classifier import IntentClassifier
from app.conversation.intent import Intent

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
        self.intent_classifier = IntentClassifier(self.llm)

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
            # Determine user intent
            intent = self.intent_classifier.classify(question)

            # General conversation → no retrieval
            if intent == Intent.CHAT:

                logger.info("General conversation detected.")

                prompt = self.prompt_builder.build_chat_prompt(question)

                answer = self.llm.generate(prompt)

                return answer, []

            # Retrieve relevant chunks
            chunks = self.retriever.retrieve(question)

            # No relevant documents found
            if not chunks:
                logger.warning(
                    "No relevant documents found for question."
                )
                return (
                    "I don't know based on the provided documents.",
                    []
                )

            # Build prompt
            prompt = self.prompt_builder.build(
                question=question,
                retrieved_chunks=chunks,
            )

            # Generate response
            answer = self.llm.generate(prompt)

            logger.info("RAG pipeline completed successfully.")
            logger.info("Pipeline returning %d chunks", len(chunks))
            return answer, chunks

        except Exception:
            logger.exception("RAG pipeline failed.")
            raise
