from app.vector_store.vector_store import VectorStore

vector_store = VectorStore()

records = vector_store.list_documents()

print(records)
