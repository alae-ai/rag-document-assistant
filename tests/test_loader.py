from app.loaders.loader_factory import LoaderFactory

loader = LoaderFactory.get_loader("data/raw/Travel and Expense Policy.pdf")

documents = loader.load()

print(f"Documents loaded: {len(documents)}")

print("\nMetadata:")
print(documents[0].metadata)

print("\nContent:")
print(documents[0].page_content)
