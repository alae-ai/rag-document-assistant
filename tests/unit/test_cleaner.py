from app.loaders.loader_factory import LoaderFactory
from app.utils.text_cleaner import TextCleaner


def test_cleaner():

    loader = LoaderFactory.get_loader(
        "data/raw/Travel and Expense Policy.pdf"
    )

    documents = loader.load()

    cleaned_documents = TextCleaner.clean_documents(
        documents
    )

    # The cleaner should return the same number of documents.
    assert len(cleaned_documents) == len(documents)

    # The cleaned document should not be empty.
    assert cleaned_documents[0].page_content.strip() != ""

    # The cleaned document should not be None.
    assert cleaned_documents[0] is not None

    # The cleaned text should not have leading or trailing whitespace.
    assert (
        cleaned_documents[0].page_content
        == cleaned_documents[0].page_content.strip()
    )

    # There should be no consecutive blank lines.
    assert "\n\n\n" not in cleaned_documents[0].page_content