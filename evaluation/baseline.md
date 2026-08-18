FINAL BASELINE — RAG DOCUMENT ASSISTANT

LLM
- Model: qwen2.5:3b
- Temperature: 0.0
- Context: 2048

Retrieval
- Vector database: Qdrant
- Embedding model: nomic-embed-text
- TOP_K: 3
- Similarity threshold: 0.65

Prompt
- System prompt: optimized short version
- Chunk size: 500
- MAX_CONTEXT_LENGTH: -

Intent classifier
- Optional
- Disabled for baseline measurements

Hardware
- CPU inference
- GPU acceleration: not enabled

QUALITY BASELINE

Functional tests: 4/4 passed

- Direct factual question       ✓
- Multi-information question   ✓
- Unsupported information      ✓
- Scenario/rule application     ✓

Observed hallucinations: 0
