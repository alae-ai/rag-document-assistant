from app.documents.document_manager import DocumentManager

document_manager = DocumentManager()

result = document_manager.add_document(
    "data/raw/company_policy.txt"
)

print(result)
