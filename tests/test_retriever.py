from app.retrieval.retriever import Retriever

# Initialize retriever
retriever = Retriever()

# Test query
query = "How many remote work days are employees allowed?"

print(f"\nQuestion:\n{query}\n")

# Retrieve documents
results = retriever.retrieve(query)

print(f"Retrieved {len(results)} results\n")

for i, result in enumerate(results, start=1):
    print("=" * 60)
    print(f"Result #{i}")
    print(f"Similarity score : {result.score:.4f}")
    print(f"Source           : {result.payload['source']}")
    print(f"Chunk ID         : {result.payload['chunk_id']}")
    print("\nText:")
    print(result.payload["text"])
    print()
