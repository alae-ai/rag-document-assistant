import asyncio
import base64
import json
import threading
import webbrowser

import httpx2

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

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
# In-memory OAuth storage
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
    Receives the OAuth callback from Google.
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

        loop = OAuthCallbackHandler.loop
        future = OAuthCallbackHandler.callback_future

        if loop is not None and future is not None:

            loop.call_soon_threadsafe(
                future.set_result,
                result,
            )

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
                <h2>Authentication completed.</h2>
                <p>You can return to the application.</p>
            </body>
            </html>
            """
        )

    def log_message(self, format, *args):
        pass


# ============================================================
# Google Drive MCP Client
# ============================================================

class GoogleDriveMCPClient:
    """
    Synchronous facade around an asynchronous Google Drive MCP
    client.

    The MCP connection runs inside a dedicated background thread
    with its own asyncio event loop.

    This makes the client safe to use from Streamlit, whose script
    is rerun frequently.
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

        # OAuth storage
        self.storage = MemoryTokenStorage()

        # Background asyncio infrastructure
        self.loop = None
        self.thread = None

        # Async MCP resources
        self.http_client = None
        self.mcp_context = None
        self.session = None

        # OAuth callback server
        self.callback_server = None

        # Synchronization
        self._ready_event = threading.Event()
        self._connect_exception = None

        # State
        self.connected = False
        self.connecting = False

    # ========================================================
    # Background event loop
    # ========================================================

    def _run_event_loop(self):
        """
        Run the asyncio event loop in a dedicated background thread.
        """

        self.loop = asyncio.new_event_loop()

        asyncio.set_event_loop(self.loop)

        self._ready_event.set()

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
        Start the background asyncio thread.
        """

        if (
            self.thread is not None
            and self.thread.is_alive()
        ):
            return

        self._ready_event.clear()

        self.thread = threading.Thread(
            target=self._run_event_loop,
            name="google-drive-mcp-loop",
            daemon=True,
        )

        self.thread.start()

        self._ready_event.wait()

    # ========================================================
    # Run coroutine in background loop
    # ========================================================

    def _run_async(self, coroutine):
        """
        Execute a coroutine in the background event loop and wait
        synchronously for its result.
        """

        if self.loop is None:
            raise RuntimeError(
                "Google Drive event loop is not running."
            )

        future = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.loop,
        )

        return future.result()

    # ========================================================
    # OAuth callback server
    # ========================================================

    def _start_callback_server(self):

        if self.callback_server is not None:
            return

        self.callback_server = HTTPServer(
            (
                self.callback_host,
                self.callback_port,
            ),
            OAuthCallbackHandler,
        )

        thread = threading.Thread(
            target=self.callback_server.serve_forever,
            name="google-drive-oauth-callback",
            daemon=True,
        )

        thread.start()

    def _stop_callback_server(self):

        if self.callback_server is None:
            return

        self.callback_server.shutdown()

        self.callback_server.server_close()

        self.callback_server = None

    # ========================================================
    # OAuth redirect
    # ========================================================

    async def _redirect_handler(self, url: str):

        print(
            "\nOpening Google OAuth authorization page..."
        )

        print(
            "\nAuthorization URL:"
        )

        print(url)

        print(
            f"\nWaiting for OAuth callback on "
            f"{self.callback_url} ..."
        )

        webbrowser.open(url)

    # ========================================================
    # OAuth callback
    # ========================================================

    async def _callback_handler(self):

        loop = asyncio.get_running_loop()

        future = loop.create_future()

        OAuthCallbackHandler.loop = loop
        OAuthCallbackHandler.callback_future = future

        try:

            result = await future

            if not result.code:
                raise RuntimeError(
                    "OAuth authorization failed."
                )

            return result

        finally:

            OAuthCallbackHandler.loop = None
            OAuthCallbackHandler.callback_future = None

    # ========================================================
    # Async connection
    # ========================================================

    async def _connect_async(self):

        if self.session is not None:
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

        print(
            "Google Drive MCP connection established."
        )

    # ========================================================
    # Connect
    # ========================================================

    def connect(self):

        if self.connected:
            return

        if self.connecting:
            return

        self.connecting = True

        self._connect_exception = None

        try:

            self._start_event_loop()

            self._start_callback_server()

            self._run_async(
                self._connect_async()
            )

            self.connected = True

        except Exception as error:

            self._connect_exception = error

            self.close()

            raise

        finally:

            self.connecting = False

    # ========================================================
    # Close
    # ========================================================

    async def _close_async(self):

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

        if self.loop is not None:

            try:

                self._run_async(
                    self._close_async()
                )

            except Exception:
                pass

        self._stop_callback_server()

        self.connected = False

        # Stop asyncio loop

        if self.loop is not None:

            self.loop.call_soon_threadsafe(
                self.loop.stop
            )

        # Wait for background thread

        if (
            self.thread is not None
            and self.thread.is_alive()
        ):

            self.thread.join(
                timeout=5
            )

        self.thread = None

        self.loop = None

    # ========================================================
    # Ensure connected
    # ========================================================

    def _ensure_connected(self):

        if not self.connected:
            raise RuntimeError(
                "GoogleDriveMCPClient is not connected. "
                "Call connect() first."
            )

    # ========================================================
    # JSON helper
    # ========================================================

    @staticmethod
    def _extract_json(result):

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
            "Could not parse JSON response from MCP tool."
        )

    # ========================================================
    # List files
    # ========================================================

    async def _list_files_async(self):

        result = await self.session.call_tool(
            "files_list",
            arguments={},
        )

        data = self._extract_json(result)

        return data.get(
            "files",
            [],
        )

    def list_files(self):

        self._ensure_connected()

        return self._run_async(
            self._list_files_async()
        )

    # ========================================================
    # Get file
    # ========================================================

    async def _get_file_async(
        self,
        file_id: str,
    ):

        result = await self.session.call_tool(
            "file_get",
            arguments={
                "fileId": file_id,
            },
        )

        return self._extract_json(result)

    def get_file(
        self,
        file_id: str,
    ):

        self._ensure_connected()

        if not file_id:
            raise ValueError(
                "file_id must not be empty."
            )

        return self._run_async(
            self._get_file_async(
                file_id
            )
        )

    # ========================================================
    # Download file
    # ========================================================

    async def _download_file_async(
        self,
        file_id: str,
    ):

        result = await self.session.call_tool(
            "file_download",
            arguments={
                "fileId": file_id,
            },
        )

        data = self._extract_json(result)

        content = data.get(
            "content"
        )

        if not isinstance(
            content,
            str,
        ):
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

    def download_file(
        self,
        file_id: str,
    ) -> bytes:

        self._ensure_connected()

        if not file_id:
            raise ValueError(
                "file_id must not be empty."
            )

        return self._run_async(
            self._download_file_async(
                file_id
            )
        )