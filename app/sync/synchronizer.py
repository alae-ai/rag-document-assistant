from app.sources.document_source import DocumentSource
from app.documents.document_manager import DocumentManager
from app.utils.logger import get_logger


logger = get_logger(__name__)


class Synchronizer:
    """
    Synchronizes documents from an external source
    with the indexed documents.

    Synchronization is currently based on document names:

    - New document      -> ADD
    - Missing document  -> DELETE
    - Existing document -> IGNORE

    Content changes are not detected yet.
    """

    def __init__(
        self,
        source: DocumentSource,
        document_manager: DocumentManager,
    ):
        self.source = source
        self.document_manager = document_manager

    def sync(self) -> dict:
        """
        Synchronize the external document source
        with the vector database.

        Returns:
            Dictionary containing synchronization statistics.
        """

        logger.info("Starting document synchronization.")

        source_documents = self.source.list_documents()

        source_names = {
            document.name
            for document in source_documents
        }

        indexed_names = set(
            self.document_manager.list_documents()
        )

        added = 0
        deleted = 0
        skipped = 0

        # Add new documents
        for document in source_documents:

            if document.name in indexed_names:
                logger.debug(
                    "Document '%s' already indexed. Skipping.",
                    document.name,
                )
                skipped += 1
                continue

            logger.info(
                "New document detected: '%s'.",
                document.name,
            )

            self.document_manager.add_document(
                document.content,
                document.name,
            )

            added += 1

        # Delete documents no longer present in the source
        for document_name in indexed_names - source_names:

            logger.info(
                "Removed document detected: '%s'.",
                document_name,
            )

            self.document_manager.remove_document(
                document_name
            )

            deleted += 1

        statistics = {
            "added": added,
            "deleted": deleted,
            "skipped": skipped,
        }

        logger.info(
            "Synchronization completed: %s",
            statistics,
        )

        return statistics