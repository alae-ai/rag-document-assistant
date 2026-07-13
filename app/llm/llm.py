import ollama

from app.llm.config import (
    OLLAMA_MODEL,
    TEMPERATURE,
    NUM_CTX,
)


class LLM:
    """
    Handles interactions with the Ollama language model.
    """

    def __init__(self):
        self.model = OLLAMA_MODEL

    def generate(self, prompt):
        """
        Generate a response from the language model.

        Args:
            prompt (str): Prompt to send to the LLM.

        Returns:
            str: Model response.
        """

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

        return response["message"]["content"]
