from __future__ import annotations

from typing import Any

from app.mcp.google_drive_client import GoogleDriveMCPClient
from app.utils.logger import get_logger

 
logger = get_logger(__name__)


class GoogleDriveService:
    """
    Synchronous service layer for Google Drive.

    GoogleDriveMCPClient internally manages its own dedicated
    asyncio event loop. This service intentionally does not
    create or manage another event loop.

    This keeps the Streamlit layer completely synchronous.
    """

    def __init__(
        self,
        mcp_url: str = "http://localhost:3000/mcp",
        callback_host: str = "localhost",
        callback_port: int = 8080,
    ):
        self.mcp_url = mcp_url
        self.callback_host = callback_host
        self.callback_port = callback_port

        self._client: GoogleDriveMCPClient | None = None
        self._connected = False
        self._closed = False

    # ========================================================
    # Connection
    # ========================================================

    def connect(self):
        """
        Connect to Google Drive through the MCP client.

        This is a synchronous method intended for Streamlit.
        The MCP client internally manages its asyncio loop.
        """

        if self._connected and self._client is not None:
            return

        logger.info(
            "Creating Google Drive MCP client."
        )

        self._client = GoogleDriveMCPClient(
            mcp_url=self.mcp_url,
            callback_host=self.callback_host,
            callback_port=self.callback_port,
        )

        try:

            self._client.connect()

            self._connected = True
            self._closed = False

            logger.info(
                "Google Drive service connected."
            )

        except Exception:

            logger.exception(
                "Failed to connect to Google Drive."
            )

            self._client = None
            self._connected = False

            raise

    # ========================================================
    # Files
    # ========================================================

    def list_files(self) -> list[dict[str, Any]]:
        """
        List Google Drive files.
        """

        self._ensure_connected()

        return self._client.list_files()

    # ========================================================
    # Get file
    # ========================================================

    def get_file(
        self,
        file_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve Google Drive file metadata.
        """

        self._ensure_connected()

        return self._client.get_file(
            file_id
        )

    # ========================================================
    # Download file
    # ========================================================

    def download_file(
        self,
        file_id: str,
    ) -> bytes:
        """
        Download a Google Drive file.

        Returns:
            Raw file content as bytes.
        """

        self._ensure_connected()

        return self._client.download_file(
            file_id
        )

    # ========================================================
    # Close
    # ========================================================

    def close(self):
        """
        Close the Google Drive MCP connection.
        """

        if self._client is None:
            self._connected = False
            self._closed = True
            return

        try:

            logger.info(
                "Closing Google Drive service."
            )

            self._client.close()

        except Exception:

            logger.exception(
                "Failed to close Google Drive service."
            )

            raise

        finally:

            self._client = None
            self._connected = False
            self._closed = True

    # ========================================================
    # State
    # ========================================================

    @property
    def connected(self) -> bool:
        """
        Return whether Google Drive is connected.
        """

        return (
            self._connected
            and self._client is not None
            and self._client.is_connected()
        )

    # ========================================================
    # Internal
    # ========================================================

    def _ensure_connected(self):
        """
        Ensure that Google Drive is connected.
        """

        if not self.connected:

            raise RuntimeError(
                "Google Drive is not connected. "
                "Call 'connect()' first."
            )