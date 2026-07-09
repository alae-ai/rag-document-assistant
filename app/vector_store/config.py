import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================
# Qdrant Configuration
# ==========================

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# ==========================
# Collection Configuration
# ==========================

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "company_documents"
)

# ==========================
# Embedding Configuration
# ==========================

VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 768))

# ==========================
# Similarity Metric
# ==========================

DISTANCE = os.getenv("DISTANCE", "Cosine")
