from app.vector_store.vector_store import VectorStore

store = VectorStore()

store.create_collection()

print(store.list_collections())
