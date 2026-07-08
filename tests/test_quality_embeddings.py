from app.embeddings.embedding_model import EmbeddingModel
from sklearn.metrics.pairwise import cosine_similarity

embedding_model = EmbeddingModel()

texts = [
    "Employees may work remotely two days per week.",
    "Staff members can work from home twice a week.",
    "The cafeteria serves lunch every day."
]

embeddings = embedding_model.embed_documents(texts)

similarity_1 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
similarity_2 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]

print(f"Similarity (1 ↔ 2): {similarity_1:.4f}")
print(f"Similarity (1 ↔ 3): {similarity_2:.4f}")
