import ollama

from app.llm.config import (
    OLLAMA_MODEL,
    TEMPERATURE,
    NUM_CTX,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLM:
    """
    Handles interactions with the Ollama language model.
    """

    def __init__(self):
        self.model = OLLAMA_MODEL

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

            response = ollama.chat(
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
                },
            )

            logger.info("Response generated successfully.")

            return response["message"]["content"]

        except Exception:
            logger.exception(
                f"Failed to generate response with model '{self.model}'."
            )
            raise
