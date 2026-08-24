from pathlib import Path

from app.loaders.loader_factory import LoaderFactory


def test_loader(filename):
    path = Path("tests/fixtures") / filename

    content = path.read_bytes()

    loader = LoaderFactory.get_loader(
        content,
        filename,
    )

    documents = loader.load()

    print(f"\n{filename}")
    print(f"Documents: {len(documents)}")

    for document in documents:
        print(document.page_content[:200])


test_loader("company_policy.txt")
test_loader("IT Support Policy.docx")
test_loader("Travel and Expense Policy.pdf")