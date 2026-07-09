from qdrant_client import QdrantClient

client = QdrantClient(
    host="localhost",
    port=6333
)

print("Connected to Qdrant!")

collections = client.get_collections()

print("\nExisting collections:")

for collection in collections.collections:
    print("-", collection.name)
