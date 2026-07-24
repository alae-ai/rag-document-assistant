from pathlib import Path

from app.prompting.config import (
    PROMPT_TEMPLATE,
    MAX_CONTEXT_LENGTH,
    INCLUDE_SOURCES,
    USE_CHUNK_SEPARATORS,
    CHUNK_SEPARATOR,
)


class PromptBuilder:
    """
    Builds the prompt sent to the language model.
    """

    def __init__(self):
        self.system_prompt = self._load_prompt(PROMPT_TEMPLATE)
    
    def _load_prompt(self, filename: str) -> str:
        """
        Load a prompt template from the prompts directory.

        Parameters
        ----------
        filename : str
            Prompt filename.

        Returns
        -------
        str
            Prompt content.
        """

        prompt_path = Path("prompts") / filename

        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def build_intent_prompt(self, message: str) -> str:
        """
        Build the prompt used for intent classification.

        Parameters
        ----------
        message : str
            User message.

        Returns
        -------
        str
            Complete intent classification prompt.
        """

        prompt = self._load_prompt(
            "intent_classifier_prompt.txt"
        )

        return prompt.format(message=message)


    def build(self, question, retrieved_chunks):
        """
        Build the complete RAG prompt.

        Args:
            question (str): User question.
            retrieved_chunks (list): Retrieved chunks returned by Qdrant.

        Returns:
            str: Complete prompt.
        """

        context_parts = []

        for chunk in retrieved_chunks:

            text = chunk.payload["text"]

            if INCLUDE_SOURCES:
                source = chunk.payload.get("source", "Unknown source")
                text = f"Source: {source}\n{text}"

            context_parts.append(text)

        if USE_CHUNK_SEPARATORS:
            context = CHUNK_SEPARATOR.join(context_parts)
        else:
            context = "\n\n".join(context_parts)

        # Prevent sending an excessively long context to the LLM
        context = context[:MAX_CONTEXT_LENGTH]

        prompt = f"""
{self.system_prompt}

==============================
CONTEXT
==============================

{context}

==============================
QUESTION
==============================

{question}

==============================
ANSWER
==============================
"""

        return prompt.strip()


    def build_chat_prompt(self, message: str) -> str:
        """
        Build a prompt for general conversation.

        Parameters
        ----------
        message : str
            User message.

        Returns
        -------
        str
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
