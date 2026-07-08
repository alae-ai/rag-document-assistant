from app.loaders.loader_factory import LoaderFactory
from app.utils.text_cleaner import TextCleaner
from app.chunking.chunker import Chunker

# Load document
loader = LoaderFactory.get_loader("data/raw/company_policy.txt")
documents = loader.load()

# Clean document
documents = TextCleaner.clean_documents(documents)

# Chunk document
chunker = Chunker()
chunks = chunker.split_documents(documents)

print(f"Original documents : {len(documents)}")
print(f"Generated chunks   : {len(chunks)}")

print("\nFirst chunk:\n")
print(chunks[0].page_content)

print("\nMetadata:\n")
print(chunks[0].metadata)
