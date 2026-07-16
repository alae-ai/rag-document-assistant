"""
Application settings.

This module is the single source of configuration for the entire project.
It loads environment variables from the .env file and exposes them as
Python constants.

No other module should call load_dotenv() or os.getenv().
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Load .env
# -----------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

# -----------------------------------------------------------------------------
# LLM
# -----------------------------------------------------------------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))

# -----------------------------------------------------------------------------
# Embeddings
# -----------------------------------------------------------------------------

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# -----------------------------------------------------------------------------
# Vector Database (Qdrant)
# -----------------------------------------------------------------------------

VECTOR_DB = os.getenv("VECTOR_DB")

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")

# -----------------------------------------------------------------------------
# Retrieval
# -----------------------------------------------------------------------------

TOP_K = int(os.getenv("TOP_K", "3"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))

# -----------------------------------------------------------------------------
# Chunking
# -----------------------------------------------------------------------------

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "80"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "20"))

# -----------------------------------------------------------------------------
# Documents
# -----------------------------------------------------------------------------

DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH")

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/rag.log")

# -----------------------------------------------------------------------------
# Streamlit
# -----------------------------------------------------------------------------

STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

_REQUIRED_SETTINGS = {
    "OLLAMA_HOST": OLLAMA_HOST,
    "OLLAMA_MODEL": OLLAMA_MODEL,
    "EMBEDDING_MODEL": EMBEDDING_MODEL,
    "QDRANT_HOST": QDRANT_HOST,
    "QDRANT_COLLECTION": QDRANT_COLLECTION,
    "DOCUMENTS_PATH": DOCUMENTS_PATH,
}

missing = [key for key, value in _REQUIRED_SETTINGS.items() if not value]

if missing:
    raise RuntimeError(
        "Missing required environment variables:\n"
        + "\n".join(f" - {name}" for name in missing)
    )
