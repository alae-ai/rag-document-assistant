from app.vector_store.vector_store import VectorStore

vs = VectorStore()

documents = vs.list_documents()

print()

for doc in documents:
    print(doc)
