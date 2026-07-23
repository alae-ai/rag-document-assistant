from app.vector_store.vector_store import VectorStore

vs = VectorStore()

print(f"Before: {vs.count_vectors()} vector(s)")

vs.clear_collection()

print(f"After: {vs.count_vectors()} vector(s)")
