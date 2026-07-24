from app.conversation.intent import Intent
from app.prompting.prompt_builder import PromptBuilder
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IntentClassifier:
    """
    Classifies a user message to determine whether it
    requires document retrieval or is general conversation.
    """

    def __init__(self, llm):
        self.llm = llm
        self.prompt_builder = PromptBuilder()

    def classify(self, message: str) -> Intent:
        """
        Classify the user's intent.

        Parameters
        ----------
        message : str
            User input.

        Returns
        -------
        Intent
            CHAT or RAG.
        """

        try:
            logger.info("Classifying user intent.")

            prompt = self.prompt_builder.build_intent_prompt(message)

            response = self.llm.generate(prompt)

            response = response.strip().upper()

            logger.info(f"Intent classifier returned '{response}'.")

            if Intent.CHAT.value in response:
                return Intent.CHAT

            if Intent.RAG.value in response:
                return Intent.RAG

            logger.warning(
                f"Unexpected intent '{response}'. Falling back to RAG."
            )

            return Intent.RAG

        except Exception:
            logger.exception("Intent classification failed.")

            return Intent.RAG
