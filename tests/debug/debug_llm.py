from app.llm.llm import LLM

# Initialize the LLM
llm = LLM()

# Simple prompt
prompt = """
Who are you?
"""

# Generate response
response = llm.generate(prompt)

print("=" * 80)
print("LLM RESPONSE")
print("=" * 80)
print()
print(response)
