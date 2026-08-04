import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL"),
    temperature=0
)
response = llm.invoke("Explain in one sentence what a Retrieval-Augmented Generation (RAG) system is.")

print(response.content)
