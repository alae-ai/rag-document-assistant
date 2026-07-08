from app.loaders.loader_factory import LoaderFactory
from app.utils.text_cleaner import TextCleaner

loader = LoaderFactory.get_loader("data/raw/company_policy.txt")

documents = loader.load()

print("=== BEFORE ===")
print(documents[0].page_content)

cleaned_documents = TextCleaner.clean_documents(documents)

print("\n=== AFTER ===")
print(cleaned_documents[0].page_content)
