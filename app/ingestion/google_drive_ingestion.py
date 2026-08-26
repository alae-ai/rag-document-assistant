from __future__ import annotations

from typing import Any

from app.documents.document_manager import DocumentManager
from app.mcp.google_drive_client import GoogleDriveMCPClient
from app.utils.logger import get_logger


logger = get_logger(__name__)


class GoogleDriveIngestion:
    """
    Handles ingestion of Google Drive documents.

    Pipeline:

        Google Drive
             ↓
        GoogleDriveMCPClient
             ↓
        file bytes
             ↓
        DocumentManager
             ↓
        Loader → Cleaner → Chunker → VectorStore
    """

    def __init__(
        self,
        drive_client: GoogleDriveMCPClient,
        document_manager: DocumentManager,
    ):
        self.drive_client = drive_client
        self.document_manager = document_manager

    def ingest_file(
        self,
        file_id: str,
        filename: str,
    ) -> bool:
        """
        Download and ingest a single Google Drive file.
        """

        logger.info(
            "Downloading Google Drive file '%s'.",
            filename,
        )

        file_content = self.drive_client.download_file(
            file_id
        )

        if not file_content:
            raise ValueError(
                f"Downloaded file '{filename}' is empty."
            )

        logger.info(
            "Sending '%s' to DocumentManager.",
            filename,
        )

        result = self.document_manager.add_document(
            file_content,
            filename,
        )

        if result:

            logger.info(
                "Google Drive file '%s' ingested successfully.",
                filename,
            )

        else:

            logger.info(
                "Google Drive file '%s' already exists. "
                "Skipping ingestion.",
                filename,
            )

        return result

    def ingest_files(
        self,
        files: list[dict[str, Any]],
    ) -> dict[str, int]:
        """
        Ingest multiple Google Drive files.

        Folders are ignored.
        """

        statistics = {
            "ingested": 0,
            "skipped": 0,
            "failed": 0,
        }

        for file in files:

            file_id = file.get("id")
            filename = file.get("name")
            mime_type = file.get("mimeType")

            if (
                mime_type
                == "application/vnd.google-apps.folder"
            ):
                logger.debug(
                    "Skipping folder '%s'.",
                    filename,
                )
                continue

            if not file_id or not filename:

                logger.warning(
                    "Skipping Google Drive item with "
                    "missing ID or name: %s",
                    file,
                )

                statistics["failed"] += 1
                continue

            try:

                result = self.ingest_file(
                    file_id=file_id,
                    filename=filename,
                )

                if result:
                    statistics["ingested"] += 1
                else:
                    statistics["skipped"] += 1

            except Exception:

                logger.exception(
                    "Failed to ingest Google Drive file '%s'.",
                    filename,
                )

                statistics["failed"] += 1

        return statistics

    def ingest_all_files(self) -> dict[str, int]:
        """
        Retrieve all Google Drive files and ingest them.
        """

        logger.info(
            "Retrieving files from Google Drive."
        )

        files = self.drive_client.list_files()

        logger.info(
            "Retrieved %d Google Drive items.",
            len(files),
        )

        return self.ingest_files(files)