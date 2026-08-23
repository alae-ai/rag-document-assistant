import ollama

from app.llm.config import (
    OLLAMA_MODEL,
    TEMPERATURE,
    NUM_CTX,
    NUM_PREDICT,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLM:
    """
    Handles interactions with the Ollama language model.
    """

    def __init__(self):
        self.model = OLLAMA_MODEL

        self.client = ollama.Client(
            host=OLLAMA_HOST,
            timeout=OLLAMA_TIMEOUT,
        )

        logger.debug(
            f"LLM initialized with model '{self.model}'."
        )

    def generate(self, prompt):
        """
        Generate a response from the language model.

        Args:
            prompt (str): Prompt to send to the LLM.

        Returns:
            str: Model response.
        """
        try:
            logger.info(
                f"Sending prompt to model '{self.model}'."
            )

            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={
                    "temperature": TEMPERATURE,
                    "num_ctx": NUM_CTX,
                    "num_predict": NUM_PREDICT,
                },
            )

            # --------------------------------------------------
            # Ollama performance metrics
            # --------------------------------------------------

            prompt_eval_count = response.get(
                "prompt_eval_count",
                0,
            )

            prompt_eval_duration = response.get(
                "prompt_eval_duration",
                0,
            )

            eval_count = response.get(
                "eval_count",
                0,
            )

            eval_duration = response.get(
                "eval_duration",
                0,
            )

            # Convert nanoseconds → seconds
            prompt_eval_seconds = (
                prompt_eval_duration / 1_000_000_000
            )

            eval_seconds = (
                eval_duration / 1_000_000_000
            )

            # Calculate tokens/second
            prompt_tokens_per_second = (
                prompt_eval_count / prompt_eval_seconds
                if prompt_eval_seconds > 0
                else 0
            )

            generation_tokens_per_second = (
                eval_count / eval_seconds
                if eval_seconds > 0
                else 0
            )

            logger.info(
                "Prompt evaluation: %d tokens / %.4fs (%.2f tokens/s)",
                prompt_eval_count,
                prompt_eval_seconds,
                prompt_tokens_per_second,
            )

            logger.info(
                "Generation: %d tokens / %.4fs (%.2f tokens/s)",
                eval_count,
                eval_seconds,
                generation_tokens_per_second,
            )

            logger.info("Response generated successfully.")

            return response["message"]["content"]

        except Exception:
            logger.exception(
                f"Failed to generate response with model '{self.model}'."
            )
            raise
