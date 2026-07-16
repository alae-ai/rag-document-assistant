from app.config import settings

QDRANT_HOST = settings.QDRANT_HOST
QDRANT_PORT = settings.QDRANT_PORT
COLLECTION_NAME = settings.QDRANT_COLLECTION

VECTOR_SIZE = 768
DISTANCE = "Cosine"
