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
        prompt_path = Path("prompts") / PROMPT_TEMPLATE

        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read().strip()

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
