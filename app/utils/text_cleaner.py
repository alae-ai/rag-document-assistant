import re
from langchain_core.documents import Document


class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean raw extracted text while preserving its meaning.
        """

        # Normalize line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Collapse multiple spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        # Collapse multiple blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Trim leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def clean_documents(documents: list[Document]) -> list[Document]:
        """
        Clean a list of LangChain Document objects.
        """

        cleaned_documents = []

        for doc in documents:
            cleaned_documents.append(
                Document(
                    page_content=TextCleaner.clean_text(doc.page_content),
                    metadata=doc.metadata,
                )
            )

        return cleaned_documents
