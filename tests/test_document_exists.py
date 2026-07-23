from app.vector_store.vector_store import VectorStore

vs = VectorStore()

print(
    vs.document_exists("IT Support Policy.docx")
)
