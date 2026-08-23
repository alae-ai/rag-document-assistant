from pathlib import Path

from app.prompting.config import (
    PROMPT_TEMPLATE,
    MAX_CONTEXT_LENGTH,
    INCLUDE_SOURCES,
    USE_CHUNK_SEPARATORS,
    CHUNK_SEPARATOR,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PromptBuilder:
    """
    Builds prompts sent to the language model.
    """

    def __init__(self):
        self.system_prompt = self._load_prompt(PROMPT_TEMPLATE)

    def _load_prompt(self, filename: str) -> str:
        """
        Load a prompt template from the prompts directory.

        Args:
            filename: Name of the prompt file.

        Returns:
            Prompt content.
        """

        project_root = Path(__file__).resolve().parents[2]
        prompt_path = project_root / "prompts" / filename

        try:
            with prompt_path.open("r", encoding="utf-8") as file:
                return file.read().strip()

        except FileNotFoundError:
            logger.error(
                "Prompt template not found: '%s'.",
                prompt_path,
            )
            raise

        except OSError:
            logger.exception(
                "Failed to read prompt template '%s'.",
                prompt_path,
            )
            raise

    def build_intent_prompt(self, message: str) -> str:
        """
        Build the prompt used for intent classification.

        Args:
            message: User message.

        Returns:
            Complete intent classification prompt.
        """

        prompt = self._load_prompt(
            "intent_classifier_prompt.txt"
        )

        return prompt.format(message=message)

    def build(self, question: str, retrieved_chunks: list) -> str:
        """
        Build the complete RAG prompt.

        Args:
            question: User question.
            retrieved_chunks: Chunks returned by Qdrant.

        Returns:
            Complete RAG prompt.
        """

        context_parts = []

        for chunk in retrieved_chunks:
            text = chunk.payload.get("text", "")

            if INCLUDE_SOURCES:
                source = chunk.payload.get(
                    "source",
                    "Unknown source",
                )
                text = f"Source: {source}\n{text}"

            context_parts.append(text)

        if USE_CHUNK_SEPARATORS:
            context = CHUNK_SEPARATOR.join(context_parts)
        else:
            context = "\n\n".join(context_parts)

        context = context[:MAX_CONTEXT_LENGTH]

        prompt = f"""
{self.system_prompt}

{context}

{question}
"""

        return prompt.strip()

    def build_chat_prompt(self, message: str) -> str:
        """
        Build a prompt for general conversation.

        Args:
            message: User message.

        Returns:
            Complete chat prompt.
        """

        prompt = f"""
{self.system_prompt}

==============================
USER MESSAGE
==============================

{message}

==============================
ANSWER
==============================
"""

        return prompt.strip()