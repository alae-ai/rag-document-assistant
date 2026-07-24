from app.conversation.intent_classifier import IntentClassifier
from app.llm.llm import LLM


def main():
    classifier = IntentClassifier(LLM())

    test_messages = [
        "Hi",
        "Hello!",
        "Bonjour",
        "Salut",
        "Merci beaucoup",
        "Goodbye",
        "Who are you?",
        "What can you do?",
        "What's the password policy?",
        "Can employees work remotely?",
        "How do I submit an expense report?",
        "Quelle est la politique de télétravail ?",
        "Comment réinitialiser mon mot de passe ?",
    ]

    print("=" * 80)
    print("Intent Classifier Test")
    print("=" * 80)

    for message in test_messages:
        intent = classifier.classify(message)

        print(f"Message : {message}")
        print(f"Intent  : {intent.value}")
        print("-" * 80)


if __name__ == "__main__":
    main()
