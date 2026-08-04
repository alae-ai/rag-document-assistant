from app.vector_store.vector_store import VectorStore

vs = VectorStore()

print("Before:")
print(vs.list_documents())

vs.delete_document("company_policy.txt")

print("\nAfter:")
print(vs.list_documents())
