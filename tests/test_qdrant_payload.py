from app.vector_store.vector_store import VectorStore
from app.vector_store.config import COLLECTION_NAME

vs = VectorStore()

records, _ = vs.client.scroll(
    collection_name=COLLECTION_NAME,
    limit=5,
    with_payload=True,
    with_vectors=False,
)

print(f"Retrieved {len(records)} point(s).\n")

for i, record in enumerate(records, start=1):
    print("=" * 80)
    print(f"Point {i}")
    print(f"ID      : {record.id}")
    print(f"Payload :")
    for key, value in record.payload.items():
        print(f"  {key}: {value}")
