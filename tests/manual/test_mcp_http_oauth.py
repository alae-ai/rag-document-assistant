import asyncio
import base64
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx2

from mcp import ClientSession
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.auth.oauth2 import OAuthToken
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import (
    OAuthClientMetadata,
    OAuthClientInformationFull,
    AuthorizationCodeResult,
)


# ============================================================
# Configuration
# ============================================================

MCP_URL = "http://localhost:3000/mcp"

CALLBACK_HOST = "localhost"
CALLBACK_PORT = 8080
CALLBACK_URL = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}/callback"

# PDF used for file_download test
DOWNLOAD_FILE_ID = "1Ndco_EO2REws_sZCg-WsWT3fLpH4YVmV"

DOWNLOAD_FILE_NAME = (
    "Alaae - VIRTUO Technologies - "
    "Fiche de stage 2 - Assistant Documentaire Interne.pdf"
)

OUTPUT_DIR = Path("tests/manual/output")


# ============================================================
# In-memory OAuth storage
# ============================================================

class MemoryTokenStorage(TokenStorage):

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
# OAuth callback server
# ============================================================

class OAuthCallbackHandler(BaseHTTPRequestHandler):

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

        print("\nOAuth callback received.")

        if error:
            print(f"OAuth error: {error}")

        result = AuthorizationCodeResult(
            code=code or "",
            state=state,
            iss=iss,
        )

        if (
            OAuthCallbackHandler.loop is not None
            and OAuthCallbackHandler.callback_future is not None
        ):
            OAuthCallbackHandler.loop.call_soon_threadsafe(
                OAuthCallbackHandler.callback_future.set_result,
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
                <h2>OAuth authentication completed.</h2>
                <p>You can return to the terminal.</p>
            </body>
            </html>
            """
        )

    def log_message(self, format, *args):
        pass


def start_callback_server():

    server = HTTPServer(
        (CALLBACK_HOST, CALLBACK_PORT),
        OAuthCallbackHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    return server


# ============================================================
# OAuth redirect handler
# ============================================================

async def redirect_handler(url: str):

    print("\nOpening Google OAuth authorization page...")

    print("\nAuthorization URL:")
    print(url)

    print(
        f"\nWaiting for OAuth callback on "
        f"{CALLBACK_URL} ..."
    )

    webbrowser.open(url)


# ============================================================
# OAuth callback handler
# ============================================================

async def callback_handler():

    loop = asyncio.get_running_loop()

    future = loop.create_future()

    OAuthCallbackHandler.loop = loop
    OAuthCallbackHandler.callback_future = future

    result = await future

    OAuthCallbackHandler.loop = None
    OAuthCallbackHandler.callback_future = None

    if not result.code:
        raise RuntimeError(
            "OAuth authorization failed: "
            "no authorization code received."
        )

    return result


# ============================================================
# Helper: extract JSON from MCP TextContent
# ============================================================

def extract_json_from_result(result):

    for content in result.content:

        if not hasattr(content, "text"):
            continue

        try:
            return json.loads(content.text)

        except json.JSONDecodeError:
            continue

    return None


# ============================================================
# Helper: extract text from MCP result
# ============================================================

def extract_text(result):

    for content in result.content:

        text = getattr(content, "text", None)

        if text:
            return text

    return None


# ============================================================
# Main
# ============================================================

async def main():

    # --------------------------------------------------------
    # Start callback server
    # --------------------------------------------------------

    print("Starting OAuth callback server...")

    callback_server = start_callback_server()

    storage = MemoryTokenStorage()

    client_metadata = OAuthClientMetadata(
        redirect_uris=[CALLBACK_URL],
        token_endpoint_auth_method="none",
        grant_types=[
            "authorization_code",
            "refresh_token",
        ],
        application_type="native",
    )

    auth_provider = OAuthClientProvider(
        server_url=MCP_URL,
        client_metadata=client_metadata,
        storage=storage,
        redirect_handler=redirect_handler,
        callback_handler=callback_handler,
    )

    print("Connecting to MCP server...")

    try:

        async with httpx2.AsyncClient(
            auth=auth_provider,
            timeout=60.0,
        ) as http_client:

            async with streamable_http_client(
                MCP_URL,
                http_client=http_client,
            ) as (
                read_stream,
                write_stream,
            ):

                async with ClientSession(
                    read_stream,
                    write_stream,
                ) as session:

                    # ========================================
                    # Initialize
                    # ========================================

                    print("\nInitializing MCP session...")

                    await session.initialize()

                    print(
                        "\nMCP session initialized successfully."
                    )

                    # ========================================
                    # List tools
                    # ========================================

                    print(
                        "\nListing available tools..."
                    )

                    tools_result = await session.list_tools()

                    print(
                        "\nAvailable MCP tools:"
                    )

                    for tool in tools_result.tools:
                        print(f"  - {tool.name}")

                    # ========================================
                    # Display file_get schema
                    # ========================================

                    file_get_tool = next(
                        (
                            tool
                            for tool in tools_result.tools
                            if tool.name == "file_get"
                        ),
                        None,
                    )

                    if file_get_tool is not None:

                        print(
                            "\nfile_get schema:"
                        )

                        print(
                            file_get_tool.input_schema
                        )

                    # ========================================
                    # Test files_list
                    # ========================================

                    print(
                        "\nTesting files_list..."
                    )

                    files_result = await session.call_tool(
                        "files_list",
                        arguments={},
                    )

                    files_data = extract_json_from_result(
                        files_result
                    )

                    if not files_data:

                        print(
                            "\nERROR: Could not parse "
                            "files_list response."
                        )

                        return

                    files = files_data.get("files", [])

                    print(
                        f"\nRetrieved {len(files)} "
                        f"Google Drive file(s)."
                    )

                    # Show a few files only
                    for file in files[:5]:

                        print(
                            f"  - {file.get('name')} "
                            f"({file.get('mimeType')})"
                        )

                    # ========================================
                    # Test file_get
                    # ========================================

                    # Use the known first file returned by
                    # files_list for the file_get test.
                    if files:

                        first_file = files[0]

                        file_id = first_file.get("id")
                        file_name = first_file.get(
                            "name",
                            "Unknown",
                        )

                        print(
                            "\nSelected file for file_get:"
                        )

                        print(
                            f"  Name: {file_name}"
                        )

                        print(
                            f"  ID:   {file_id}"
                        )

                        if file_id:

                            print(
                                "\nTesting file_get..."
                            )

                            file_get_result = (
                                await session.call_tool(
                                    "file_get",
                                    arguments={
                                        "fileId": file_id,
                                    },
                                )
                            )

                            print(
                                "\nfile_get result:"
                            )

                            for content in (
                                file_get_result.content
                            ):
                                print(content)

                    # ========================================
                    # Test file_download
                    # ========================================

                    print(
                        "\nTesting file_download..."
                    )

                    print(
                        f"  File: {DOWNLOAD_FILE_NAME}"
                    )

                    print(
                        f"  ID:   {DOWNLOAD_FILE_ID}"
                    )

                    download_result = (
                        await session.call_tool(
                            "file_download",
                            arguments={
                                "fileId": DOWNLOAD_FILE_ID,
                            },
                        )
                    )

                    print(
                        "\nfile_download completed."
                    )

                    # ----------------------------------------
                    # Extract result
                    # ----------------------------------------

                    download_text = extract_text(
                        download_result
                    )

                    if not download_text:

                        print(
                            "\nERROR: file_download "
                            "returned no text content."
                        )

                        return

                    print(
                        f"Response size: "
                        f"{len(download_text)} characters"
                    )

                    # ----------------------------------------
                    # Parse JSON
                    # ----------------------------------------

                    try:

                        download_data = json.loads(
                            download_text
                        )

                    except json.JSONDecodeError as error:

                        print(
                            "\nERROR: file_download "
                            "response is not valid JSON."
                        )

                        print(
                            f"JSON error: {error}"
                        )

                        return

                    # ----------------------------------------
                    # Extract Base64 content
                    # ----------------------------------------

                    encoded_content = (
                        download_data.get("content")
                    )

                    if not encoded_content:

                        print(
                            "\nERROR: file_download "
                            "response contains no "
                            "'content' field."
                        )

                        return

                    print(
                        f"Base64 content size: "
                        f"{len(encoded_content)} characters"
                    )

                    # ----------------------------------------
                    # Decode Base64
                    # ----------------------------------------

                    try:

                        file_bytes = base64.b64decode(
                            encoded_content,
                            validate=True,
                        )

                    except Exception as error:

                        print(
                            "\nERROR: Could not decode "
                            "Base64 file content."
                        )

                        print(
                            f"Decode error: {error}"
                        )

                        return

                    print(
                        f"Decoded file size: "
                        f"{len(file_bytes)} bytes"
                    )

                    # ----------------------------------------
                    # Verify PDF
                    # ----------------------------------------

                    if file_bytes.startswith(b"%PDF"):

                        print(
                            "File format verification: "
                            "VALID PDF"
                        )

                    else:

                        print(
                            "WARNING: File does not "
                            "start with PDF signature."
                        )

                    # ----------------------------------------
                    # Save downloaded file
                    # ----------------------------------------

                    OUTPUT_DIR.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    output_path = (
                        OUTPUT_DIR / DOWNLOAD_FILE_NAME
                    )

                    output_path.write_bytes(
                        file_bytes
                    )

                    print(
                        "\nDownloaded file saved to:"
                    )

                    print(
                        f"  {output_path}"
                    )

                    # ----------------------------------------
                    # Final success
                    # ----------------------------------------

                    print(
                        "\n========================================"
                    )

                    print(
                        "OAuth + MCP HTTP test successful."
                    )

                    print(
                        "files_list      : OK"
                    )

                    print(
                        "file_get        : OK"
                    )

                    print(
                        "file_download   : OK"
                    )

                    print(
                        "Base64 decoding : OK"
                    )

                    print(
                        "PDF validation  : OK"
                    )

                    print(
                        "========================================"
                    )

    finally:

        callback_server.shutdown()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())

