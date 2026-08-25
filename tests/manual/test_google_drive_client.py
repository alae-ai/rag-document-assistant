import asyncio
import base64

from app.mcp.google_drive_client import GoogleDriveMCPClient


# ============================================================
# Configuration
# ============================================================

MCP_URL = "http://localhost:3000/mcp"

TEST_FILE_ID = "1Ndco_EO2REws_sZCg-WsWT3fLpH4YVmV"
TEST_FILE_NAME = (
    "Alaae - VIRTUO Technologies - Fiche de stage "
    "2 - Assistant Documentaire Interne.pdf"
)


# ============================================================
# Main test
# ============================================================

async def main():

    client = GoogleDriveMCPClient(
        mcp_url=MCP_URL,
        callback_host="localhost",
        callback_port=8080,
    )

    try:

        # ====================================================
        # Connect
        # ====================================================

        print("=" * 60)
        print("Testing GoogleDriveMCPClient")
        print("=" * 60)

        print("\nConnecting...")

        await client.connect()

        print("Connection: OK")

        # ====================================================
        # Test list_files
        # ====================================================

        print("\nTesting list_files()...")

        files = await client.list_files()

        print(
            f"list_files: OK "
            f"({len(files)} files returned)"
        )

        if not files:
            raise RuntimeError(
                "Google Drive returned no files."
            )

        # Display a few files

        print("\nFirst files:")

        for file in files[:5]:

            print(
                f"  - {file.get('name')} "
                f"({file.get('mimeType')})"
            )

        # ====================================================
        # Test get_file
        # ====================================================

        print("\nTesting get_file()...")

        metadata = await client.get_file(
            TEST_FILE_ID
        )

        print("get_file: OK")

        print(
            f"  Name: {metadata.get('name')}"
        )

        print(
            f"  MIME type: {metadata.get('mimeType')}"
        )

        print(
            f"  Size: {metadata.get('size')}"
        )

        # Verify expected file

        if metadata.get("name") != TEST_FILE_NAME:
            raise AssertionError(
                "Unexpected file returned by get_file()."
            )

        # ====================================================
        # Test download_file
        # ====================================================

        print("\nTesting download_file()...")

        content = await client.download_file(
            TEST_FILE_ID
        )

        print("download_file: OK")

        print(
            f"  Content type: {type(content).__name__}"
        )

        print(
            f"  Content size: {len(content)} bytes"
        )

        # ====================================================
        # Validate bytes
        # ====================================================

        if not isinstance(content, bytes):
            raise AssertionError(
                "download_file() did not return bytes."
            )

        # ====================================================
        # Validate PDF
        # ====================================================

        print("\nTesting PDF content...")

        if not content.startswith(b"%PDF"):
            raise AssertionError(
                "Downloaded content does not appear "
                "to be a valid PDF."
            )

        print("PDF validation: OK")

        # ====================================================
        # Final result
        # ====================================================

        print("\n" + "=" * 60)
        print("GoogleDriveMCPClient test successful.")
        print("=" * 60)

        print("list_files       : OK")
        print("get_file         : OK")
        print("download_file    : OK")
        print("bytes conversion : OK")
        print("PDF validation   : OK")

        print("=" * 60)

    finally:

        print("\nClosing client...")

        await client.close()

        print("Client closed.")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
