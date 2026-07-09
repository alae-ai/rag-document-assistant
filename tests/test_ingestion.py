from app.loaders.loader_factory import LoaderFactory
from app.utils.text_cleaner import TextCleaner
from app.chunking.chunker import Chunker
from app.vector_store.vector_store import VectorStore

# Load document
loader = LoaderFactory.get_loader("data/raw/company_policy.txt")
documents = loader.load()

# Clean text
documents = TextCleaner.clean_documents(documents)

# Chunk text
chunker = Chunker()
chunks = chunker.split_documents(documents)

print(f"Generated {len(chunks)} chunks")

# Connect to Qdrant
store = VectorStore()

# Create collection if needed
store.create_collection()

# Insert chunks
store.add_documents(chunks)

print(f"\nVectors stored: {store.count_vectors()}")
print("\nPipeline completed successfully!")

