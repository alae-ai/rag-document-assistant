from app.llm.llm import LLM
from app.prompting.prompt_builder import PromptBuilder
from app.retrieval.retriever import Retriever

from app.conversation.intent_classifier import IntentClassifier
from app.conversation.intent import Intent

import time

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
        pipeline_start = time.perf_counter()


        try:

            # Start timer
            start = time.perf_counter()

            # Determine user intent
            intent = self.intent_classifier.classify(question)

            # Measure intent classification time
            intent_time = time.perf_counter() - start

            logger.info(
                "Intent classification completed in %.4f seconds.",
                intent_time,
            )

            # General conversation → no retrieval
            if intent == Intent.CHAT:

                logger.info("General conversation detected.")

                # Measure time for prompt building and LLM generation
                start = time.perf_counter()

                prompt = self.prompt_builder.build_chat_prompt(question)

                prompt_time = time.perf_counter() - start

                logger.info(
                    "Chat prompt built in %.4f seconds.",
                    prompt_time,
                )

                # Measure time for LLM generation
                start = time.perf_counter()
                answer = self.llm.generate(prompt)

                llm_time = time.perf_counter() - start

                logger.info(
                    "LLM generation completed in %.4f seconds.",
                    llm_time,
                )
                total_time = time.perf_counter() - pipeline_start
                logger.info(
                    "Total pipeline time: %.4f seconds.",
                    total_time,
                )
                return answer, []

            # Retrieve relevant chunks
            start = time.perf_counter()

            chunks = self.retriever.retrieve(question)

            retrieval_time = time.perf_counter() - start

            logger.info(
                "Retrieval completed in %.4f seconds.",
                retrieval_time,
            )

            # No relevant documents found
            if not chunks:
                logger.warning(
                    "No relevant documents found for question."
                )

                total_time = time.perf_counter() - pipeline_start
                logger.info(
                    "Total pipeline time: %.4f seconds.",
                    total_time,
                )

                return (
                    "I don't know based on the provided documents.",
                    []
                )

            # Build prompt

            start = time.perf_counter()

            prompt = self.prompt_builder.build(
                question=question,
                retrieved_chunks=chunks,
            )
            prompt_time = time.perf_counter() - start
            logger.info(
                "Prompt construction completed in %.4f seconds.",
                prompt_time,
            )

            # Generate response

            start = time.perf_counter()
            
            answer = self.llm.generate(prompt)

            llm_time = time.perf_counter() - start
            logger.info(
                "LLM generation completed in %.4f seconds.",
                llm_time,
            )
            total_time = time.perf_counter() - pipeline_start
            logger.info(
                "Total pipeline time: %.4f seconds.",
                total_time,
            )
            logger.info("RAG pipeline completed successfully.")
            logger.info("Pipeline returning %d chunks", len(chunks))
            return answer, chunks

        except Exception:
            logger.exception("RAG pipeline failed.")
            raise
