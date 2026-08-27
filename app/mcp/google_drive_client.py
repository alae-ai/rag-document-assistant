from __future__ import annotations

import asyncio
import base64
import json
import threading
import webbrowser
from concurrent.futures import Future
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import httpx2

from mcp import ClientSession
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.auth.oauth2 import OAuthToken
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import (
    AuthorizationCodeResult,
    OAuthClientInformationFull,
    OAuthClientMetadata,
)


# ============================================================
# OAuth token storage
# ============================================================


class MemoryTokenStorage(TokenStorage):
    """In-memory storage for OAuth tokens and client information."""

    def __init__(self):
        self.tokens = None
        self.client_info = None

    async def get_tokens(self):
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken):
        self.tokens = tokens

    async def get_client_info(self):
        return self.client_info

    async def set_client_info(
        self,
        client_info: OAuthClientInformationFull,
    ):
        self.client_info = client_info


# ============================================================
# OAuth callback handler
# ============================================================


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """
    HTTP handler used by the local OAuth callback server.

    The callback is received in the HTTP server thread and
    forwarded safely to the MCP asyncio event loop.
    """

    loop = None
    callback_future = None

    def do_GET(self):

        parsed = urlparse(self.path)

        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)

        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        iss = params.get("iss", [None])[0]
        error = params.get("error", [None])[0]

        if error:
            result = AuthorizationCodeResult(
                code="",
                state=state,
                iss=iss,
            )
        else:
            result = AuthorizationCodeResult(
                code=code or "",
                state=state,
                iss=iss,
            )

        # ----------------------------------------------------
        # Forward result to asyncio loop
        # ----------------------------------------------------

        loop = OAuthCallbackHandler.loop
        future = OAuthCallbackHandler.callback_future

        if loop is not None and future is not None:

            loop.call_soon_threadsafe(
                self._set_callback_result,
                future,
                result,
            )

        # ----------------------------------------------------
        # Browser response
        # ----------------------------------------------------

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8",
        )

        self.end_headers()

        self.wfile.write(
            b"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>OAuth Authentication</title>
            </head>
            <body>
                <h2>OAuth authentication completed.</h2>
                <p>You can return to the application.</p>
            </body>
            </html>
            """
        )

    @staticmethod
    def _set_callback_result(
        future,
        result,
    ):
        """
        Safely resolve the callback future.

        The future may already be completed if Streamlit
        reran or the OAuth flow was cancelled.
        """

        if not future.done():
            future.set_result(result)

    def log_message(self, format, *args):
        pass


# ============================================================
# Google Drive MCP Client
# ============================================================


class GoogleDriveMCPClient:
    """
    Client for communicating with the Google Drive MCP server
    through Streamable HTTP and OAuth.

    The MCP connection lives inside a dedicated asyncio event
    loop running in a persistent background thread.

    This design prevents Streamlit reruns from creating and
    destroying different asyncio event loops around the same
    MCP session.
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

        self.callback_url = (
            f"http://{callback_host}:{callback_port}/callback"
        )

        # ----------------------------------------------------
        # OAuth
        # ----------------------------------------------------

        self.storage = MemoryTokenStorage()

        # ----------------------------------------------------
        # MCP resources
        # ----------------------------------------------------

        self.http_client = None
        self.mcp_context = None
        self.session = None

        # ----------------------------------------------------
        # OAuth callback server
        # ----------------------------------------------------

        self.callback_server = None
        self.callback_thread = None

        # ----------------------------------------------------
        # Dedicated asyncio loop
        # ----------------------------------------------------

        self.loop = None
        self.loop_thread = None
        self.loop_ready = threading.Event()

        # ----------------------------------------------------
        # State
        # ----------------------------------------------------

        self.connected = False
        self._closing = False

    # ========================================================
    # Event loop
    # ========================================================

    def _event_loop_worker(self):
        """
        Run the dedicated asyncio event loop.

        This thread stays alive for the lifetime of the MCP
        connection.
        """

        self.loop = asyncio.new_event_loop()

        asyncio.set_event_loop(self.loop)

        self.loop_ready.set()

        try:
            self.loop.run_forever()

        finally:

            pending = asyncio.all_tasks(self.loop)

            for task in pending:
                task.cancel()

            if pending:
                self.loop.run_until_complete(
                    asyncio.gather(
                        *pending,
                        return_exceptions=True,
                    )
                )

            self.loop.close()

            self.loop = None

    def _start_event_loop(self):
        """
        Start the dedicated asyncio event loop if necessary.
        """

        if (
            self.loop_thread is not None
            and self.loop_thread.is_alive()
        ):
            return

        self.loop_ready.clear()

        self.loop_thread = threading.Thread(
            target=self._event_loop_worker,
            daemon=True,
            name="google-drive-mcp-loop",
        )

        self.loop_thread.start()

        if not self.loop_ready.wait(timeout=10):
            raise RuntimeError(
                "Failed to start Google Drive MCP asyncio loop."
            )

    def _stop_event_loop(self):
        """
        Stop the dedicated asyncio event loop.
        """

        if self.loop is not None:

            self.loop.call_soon_threadsafe(
                self.loop.stop
            )

        if (
            self.loop_thread is not None
            and self.loop_thread.is_alive()
        ):

            self.loop_thread.join(timeout=10)

        self.loop_thread = None
        self.loop = None

    def run(self, coroutine):
        """
        Execute a coroutine inside the dedicated MCP event loop.

        This is the method Streamlit should use instead of
        asyncio.run().

        Example:

            client.run(client.connect())

            files = client.run(
                client.list_files()
            )
        """

        if self.loop is None:
            raise RuntimeError(
                "GoogleDriveMCPClient event loop is not running."
            )

        future = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.loop,
        )

        try:
            return future.result()

        except Exception:
            # Make sure exceptions propagate normally.
            raise

    # ========================================================
    # OAuth callback server
    # ========================================================

    def _start_callback_server(self):
        """
        Start the OAuth callback server only once.
        """

        if self.callback_server is not None:
            return

        try:

            self.callback_server = HTTPServer(
                (
                    self.callback_host,
                    self.callback_port,
                ),
                OAuthCallbackHandler,
            )

        except OSError as error:

            raise RuntimeError(
                f"Could not start OAuth callback server on "
                f"{self.callback_host}:{self.callback_port}. "
                "The port may already be in use."
            ) from error

        self.callback_thread = threading.Thread(
            target=self.callback_server.serve_forever,
            daemon=True,
            name="google-drive-oauth-callback",
        )

        self.callback_thread.start()

    def _stop_callback_server(self):
        """
        Stop the OAuth callback server.
        """

        if self.callback_server is None:
            return

        self.callback_server.shutdown()
        self.callback_server.server_close()

        if (
            self.callback_thread is not None
            and self.callback_thread.is_alive()
        ):

            self.callback_thread.join(timeout=5)

        self.callback_server = None
        self.callback_thread = None

    # ========================================================
    # OAuth handlers
    # ========================================================

    async def _redirect_handler(self, url: str):
        """
        Open the Google OAuth authorization page.
        """

        print(
            "\nOpening Google OAuth authorization page..."
        )

        print("\nAuthorization URL:")
        print(url)

        print(
            f"\nWaiting for OAuth callback on "
            f"{self.callback_url} ..."
        )

        webbrowser.open(url)

    async def _callback_handler(self):
        """
        Wait for the OAuth callback.

        This coroutine executes inside the dedicated MCP
        asyncio event loop.
        """

        loop = asyncio.get_running_loop()

        future = loop.create_future()

        OAuthCallbackHandler.loop = loop
        OAuthCallbackHandler.callback_future = future

        try:

            result = await future

            if not result.code:

                raise RuntimeError(
                    "OAuth authorization failed: "
                    "no authorization code received."
                )

            return result

        finally:

            if (
                OAuthCallbackHandler.callback_future
                is future
            ):
                OAuthCallbackHandler.callback_future = None

            if OAuthCallbackHandler.loop is loop:
                OAuthCallbackHandler.loop = None

    # ========================================================
    # Async connection
    # ========================================================

    async def _connect(self):
        """
        Internal asynchronous MCP connection.

        This method must run inside the dedicated event loop.
        """

        if self.session is not None:
            self.connected = True
            return

        print(
            "Connecting to Google Drive MCP server..."
        )

        client_metadata = OAuthClientMetadata(
            redirect_uris=[
                self.callback_url
            ],
            token_endpoint_auth_method="none",
            grant_types=[
                "authorization_code",
                "refresh_token",
            ],
            application_type="native",
        )

        auth_provider = OAuthClientProvider(
            server_url=self.mcp_url,
            client_metadata=client_metadata,
            storage=self.storage,
            redirect_handler=self._redirect_handler,
            callback_handler=self._callback_handler,
        )

        self.http_client = httpx2.AsyncClient(
            auth=auth_provider,
            timeout=60.0,
        )

        try:

            self.mcp_context = streamable_http_client(
                self.mcp_url,
                http_client=self.http_client,
            )

            read_stream, write_stream = (
                await self.mcp_context.__aenter__()
            )

            self.session = ClientSession(
                read_stream,
                write_stream,
            )

            await self.session.__aenter__()

            print(
                "Initializing MCP session..."
            )

            await self.session.initialize()

            self.connected = True

            print(
                "Google Drive MCP connection established."
            )

        except Exception:

            self.connected = False

            if self.session is not None:

                await self.session.__aexit__(
                    None,
                    None,
                    None,
                )

                self.session = None

            if self.mcp_context is not None:

                await self.mcp_context.__aexit__(
                    None,
                    None,
                    None,
                )

                self.mcp_context = None

            if self.http_client is not None:

                await self.http_client.aclose()

                self.http_client = None

            raise

    def connect(self):
        """
        Connect to Google Drive MCP.

        This is the synchronous method intended for Streamlit.
        """

        if self.connected:
            return

        self._start_callback_server()
        self._start_event_loop()

        try:

            self.run(
                self._connect()
            )

        except Exception:

            self._stop_callback_server()
            self._stop_event_loop()

            raise

    # ========================================================
    # Connection state
    # ========================================================

    def is_connected(self) -> bool:
        """
        Return whether the MCP connection is active.
        """

        return (
            self.connected
            and self.session is not None
        )

    # ========================================================
    # Close
    # ========================================================

    async def _close(self):
        """
        Internal asynchronous cleanup.
        """

        self.connected = False

        if self.session is not None:

            await self.session.__aexit__(
                None,
                None,
                None,
            )

            self.session = None

        if self.mcp_context is not None:

            await self.mcp_context.__aexit__(
                None,
                None,
                None,
            )

            self.mcp_context = None

        if self.http_client is not None:

            await self.http_client.aclose()

            self.http_client = None

    def close(self):
        """
        Close the MCP connection and all associated resources.
        """

        if self.loop is not None:

            try:

                self.run(
                    self._close()
                )

            finally:

                self._stop_event_loop()

        self._stop_callback_server()

        self.connected = False

    # ========================================================
    # Internal helpers
    # ========================================================

    def _ensure_connected(self):
        """
        Ensure that the MCP session is connected.
        """

        if not self.is_connected():

            raise RuntimeError(
                "GoogleDriveMCPClient is not connected. "
                "Call 'connect()' first."
            )

    @staticmethod
    def _extract_json(result):
        """
        Extract JSON data from an MCP tool result.
        """

        for content in result.content:

            text = getattr(
                content,
                "text",
                None,
            )

            if not text:
                continue

            try:

                return json.loads(text)

            except json.JSONDecodeError:
                continue

        raise RuntimeError(
            "Could not parse JSON response "
            "from MCP tool."
        )

    # ========================================================
    # Async MCP operations
    # ========================================================

    async def _list_files(self):
        """
        Internal asynchronous files_list operation.
        """

        self._ensure_connected()

        result = await self.session.call_tool(
            "files_list",
            arguments={},
        )

        data = self._extract_json(result)

        return data.get("files", [])

    async def _get_file(
        self,
        file_id: str,
    ):
        """
        Internal asynchronous file_get operation.
        """

        self._ensure_connected()

        if not file_id:
            raise ValueError(
                "file_id must not be empty."
            )

        result = await self.session.call_tool(
            "file_get",
            arguments={
                "fileId": file_id,
            },
        )

        return self._extract_json(result)

    async def _download_file(
        self,
        file_id: str,
    ) -> bytes:
        """
        Internal asynchronous file_download operation.
        """

        self._ensure_connected()

        if not file_id:
            raise ValueError(
                "file_id must not be empty."
            )

        result = await self.session.call_tool(
            "file_download",
            arguments={
                "fileId": file_id,
            },
        )

        data = self._extract_json(result)

        content = data.get("content")

        if not isinstance(content, str):

            raise RuntimeError(
                "MCP file_download response does not "
                "contain Base64 content."
            )

        try:

            return base64.b64decode(
                content,
                validate=True,
            )

        except Exception as error:

            raise RuntimeError(
                "Failed to decode Base64 file content."
            ) from error

    # ========================================================
    # Public MCP operations
    # ========================================================

    def list_files(self):
        """
        List files available in Google Drive.

        Returns:
            list[dict]: Google Drive file metadata.
        """

        return self.run(
            self._list_files()
        )

    def get_file(
        self,
        file_id: str,
    ):
        """
        Retrieve metadata for a Google Drive file.

        Args:
            file_id: Google Drive file ID.

        Returns:
            dict: Google Drive file metadata.
        """

        return self.run(
            self._get_file(file_id)
        )

    def download_file(
        self,
        file_id: str,
    ) -> bytes:
        """
        Download a Google Drive file.

        Returns:
            bytes: Raw file content.
        """

        return self.run(
            self._download_file(file_id)
        )