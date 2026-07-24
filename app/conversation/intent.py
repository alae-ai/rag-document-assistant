from enum import Enum


class Intent(Enum):
    """
    Supported user intents.
    """

    CHAT = "CHAT"
    RAG = "RAG"
