from app.retrieval.retriever import Retriever
from app.prompting.prompt_builder import PromptBuilder
from app.llm.llm import LLM

# Initialize components
retriever = Retriever()
prompt_builder = PromptBuilder()
llm = LLM()

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

    chunks = retriever.retrieve(question)

    prompt = prompt_builder.build(question, chunks)

    response = llm.generate(prompt)

    print("\nAnswer:")
    print(response)
    print("\n" + "-" * 80 + "\n")
