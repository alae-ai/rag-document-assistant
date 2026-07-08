from app.embeddings.embedding_model import EmbeddingModel

embedding_model = EmbeddingModel()

texts = [
    "Employees may work remotely two days per week.",
    "The company provides laptops to all employees."
]

embeddings = embedding_model.embed_documents(texts)

print(f"Number of embeddings: {len(embeddings)}")

print(f"Embedding dimension: {len(embeddings[0])}")

print("\nFirst 10 values of the first embedding:")
print(embeddings[0][:10])
