from app.documents.document_manager import DocumentManager

manager = DocumentManager()

manager.add_document("data/raw/IT Support Policy.docx")

print("Document indexed successfully!")
