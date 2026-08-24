from pathlib import Path

from app.documents.document_manager import DocumentManager


def main():
    file_path = Path("tests/fixtures/company_police.txt")

    content = file_path.read_bytes()
    filename = file_path.name

    manager = DocumentManager()

    print(f"Indexing: {filename}")

    result = manager.add_document(
        content,
        filename,
    )

    print(f"Indexation result: {result}")

    print("\nIndexed documents:")
    print(manager.list_documents())

    print("\nStatistics:")
    print(manager.get_statistics())


if __name__ == "__main__":
    main()