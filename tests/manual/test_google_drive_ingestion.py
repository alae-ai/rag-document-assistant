import asyncio

from app.mcp.google_drive_client import GoogleDriveMCPClient
from app.documents.document_manager import DocumentManager
from app.ingestion.google_drive_ingestion import GoogleDriveIngestion


# ============================================================
# Configuration
# ============================================================

FILE_ID = "1Ndco_EO2REws_sZCg-WsWT3fLpH4YVmV"
FILE_NAME = (
    "Alaae - VIRTUO Technologies - "
    "Fiche de stage 2 - Assistant Documentaire Interne.pdf"
)


# ============================================================
# Main test
# ============================================================

async def main():

    print("=" * 60)
    print("Testing single Google Drive file ingestion")
    print("=" * 60)

    # --------------------------------------------------------
    # Create components
    # --------------------------------------------------------

    drive_client = GoogleDriveMCPClient()

    document_manager = DocumentManager()

    ingestion = GoogleDriveIngestion(
        drive_client=drive_client,
        document_manager=document_manager,
    )

    try:

        # ----------------------------------------------------
        # Connect to Google Drive MCP
        # ----------------------------------------------------

        print("\nConnecting to Google Drive MCP...")

        await drive_client.connect()

        print("Connection: OK")

        # ----------------------------------------------------
        # Check whether document already exists
        # ----------------------------------------------------

        print("\nChecking if document already exists...")

        exists_before = document_manager.document_exists(
            FILE_NAME
        )

        print(
            f"Document exists before ingestion: "
            f"{exists_before}"
        )

        # ----------------------------------------------------
        # Ingest one file
        # ----------------------------------------------------

        print("\nIngesting file...")

        result = await ingestion.ingest_file(
            file_id=FILE_ID,
            filename=FILE_NAME,
        )

        print(
            f"\nIngestion result: {result}"
        )

        # ----------------------------------------------------
        # Verify document
        # ----------------------------------------------------

        print("\nChecking document in vector store...")

        exists_after = document_manager.document_exists(
            FILE_NAME
        )

        print(
            f"Document exists after ingestion: "
            f"{exists_after}"
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        print("\nDocument statistics:")

        statistics = document_manager.get_statistics()

        print(statistics)

        # ----------------------------------------------------
        # Final validation
        # ----------------------------------------------------

        print("\n" + "=" * 60)

        if exists_after:
            print(
                "Single-file Google Drive ingestion: SUCCESS"
            )
        else:
            print(
                "Single-file Google Drive ingestion: FAILED"
            )

        print("=" * 60)

    finally:

        # ----------------------------------------------------
        # Close MCP connection
        # ----------------------------------------------------

        print("\nClosing Google Drive MCP client...")

        await drive_client.close()

        print("Client closed.")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())

