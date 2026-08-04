from app.conversation.intent_classifier import IntentClassifier
from app.llm.llm import LLM


def test_intent_classifier():

    classifier = IntentClassifier(LLM())

    chat_messages = [
        "Hi",
        "Hello!",
        "Bonjour",
        "Salut",
        "Merci beaucoup",
        "Goodbye",
        "Who are you?",
        "What can you do?",
    ]

    rag_messages = [
        "What's the password policy?",
        "Can employees work remotely?",
        "How do I submit an expense report?",
        "Quelle est la politique de télétravail ?",
        "Comment réinitialiser mon mot de passe ?",
    ]

    for message in chat_messages:
        intent = classifier.classify(message)

        assert intent.value == "CHAT"

    for message in rag_messages:
        intent = classifier.classify(message)

        assert intent.value == "RAG"