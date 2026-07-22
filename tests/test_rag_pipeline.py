from app.rag.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

print("=" * 80)
print("RAG DOCUMENT ASSISTANT")
print("=" * 80)
print("Type 'exit' to quit.\n")

while True:
    question = input("Question > ").strip()

    if question.lower() in ["exit", "quit", "q"]:
        print("\nGoodbye!")
        break

    if not question:
        continue

    answer, _ = pipeline.ask(question)

    print("\nAnswer:")
    print(answer)
    print("\n" + "-" * 80 + "\n")
