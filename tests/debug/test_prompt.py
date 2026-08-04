from app.retrieval.retriever import Retriever
from app.prompting.prompt_builder import PromptBuilder

# Initialize components
retriever = Retriever()
prompt_builder = PromptBuilder()

# User question
question = "How many remote work days are employees allowed?"

# Retrieve relevant chunks
chunks = retriever.retrieve(question)

# Build prompt
prompt = prompt_builder.build(question, chunks)

# Display result
print("=" * 80)
print("FINAL PROMPT")
print("=" * 80)
print()
print(prompt)
