# Virtuoso — Internal Documentation Assistant

**Virtuoso** is an AI-powered internal documentation assistant based on **Retrieval-Augmented Generation (RAG)**. The project is designed to provide employees with fast and contextual access to information contained in enterprise documents.

The application processes internal documentation, converts it into semantic embeddings, stores the resulting vectors in a vector database, retrieves relevant information for user queries, and uses a Large Language Model (LLM) to generate contextual answers.

The project is built with a **modular architecture** designed to facilitate maintenance, testing, scalability, and future integrations with enterprise services.

---

# Project Status

The repository currently contains two main development branches.

## `main` — Functional Version

The `main` branch contains the **fully functional core version** of the application.

It provides:

* Document upload
* PDF, DOCX and TXT processing
* Text cleaning and preprocessing
* Configurable document chunking
* Embedding generation
* Vector storage with Qdrant
* Semantic similarity retrieval
* Retrieval-Augmented Generation
* LLM-based question answering
* Document management
* Dashboard and statistics
* Configurable retrieval parameters
* Logging
* Component-level testing
* Initial CI/CD workflow structure

This version is suitable for demonstrating and deploying the core RAG system.

### Advantages

The main branch provides a simple and stable architecture focused on the core objective of the project: **making internal documentation searchable and accessible through natural language**.

It can also be deployed in a cloud environment without requiring authentication to be implemented directly inside the application.

### Current limitations

The main version currently focuses on locally uploaded documents. It does not yet provide native synchronization with external enterprise document repositories such as Google Drive.

Other limitations include:

* No automatic document synchronization
* No built-in user authentication
* Limited handling of contradictory documents
* Retrieval quality depends on chunking and similarity parameters
* No advanced reranking layer
* No automatic document update detection

These limitations are considered future improvements rather than architectural blockers.

---

# `mcp` — Under Development

The `mcp` branch contains the ongoing development for integrating **Google Drive through the Model Context Protocol (MCP)**.

The objective of this branch is to extend the existing document management system so that authorized users can retrieve documents directly from Google Drive and index them using the same RAG pipeline.

The planned architecture is:

```text
Google Drive
      │
      ▼
Google Drive MCP Server
      │
      ▼
GoogleDriveMCPClient
      │
      ▼
GoogleDriveService
      │
      ▼
DocumentManager
      │
      ▼
Document Processing Pipeline
      │
      ├── Loader
      ├── Text Cleaning
      ├── Chunking
      ├── Embeddings
      └── Qdrant
```

The MCP branch also introduces **Google OAuth authentication for Google Drive access**.

The authentication is specifically related to accessing Google Drive and is **not intended to become authentication for the Virtuoso application itself**.

---

# Application Authentication and Cloud Deployment

The application itself does not currently implement an internal authentication system.

This is intentional.

Virtuoso is designed as an **internal enterprise application**, expected to be deployed inside a controlled cloud environment. In such an architecture, authentication and access control can be delegated to the cloud infrastructure rather than being implemented independently inside the application.

For example:

* **AWS** → IAM, IAM Identity Center, Cognito, or an organization-level access layer
* **Azure** → Microsoft Entra ID, Azure RBAC, resource groups and related access-control mechanisms
* **GCP** → IAM and Identity-Aware Proxy

This approach avoids duplicating authentication logic inside the application and allows the organization to manage access centrally according to its existing security infrastructure.

The Google OAuth mechanism being developed in the `mcp` branch serves a different purpose: **authorizing the application to access the user's Google Drive resources**.

Therefore:

```text
Application Access
        │
        ▼
Cloud / Enterprise IAM
        │
        ▼
Virtuoso Application
        │
        └──────────────► Google Drive OAuth
                              │
                              ▼
                         Google Drive
```

This separation makes the architecture more suitable for enterprise deployment.

---

# RAG Architecture

The core RAG pipeline follows a modular architecture:

```text
                 ┌─────────────────────┐
                 │     User Query      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      Retriever      │
                 └──────────┬──────────┘
                            │
                            ▼
                       ┌─────────┐
                       │ Qdrant  │
                       └────┬────┘
                            │
                     Relevant Chunks
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Prompt Builder    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     Qwen / LLM      │
                 └──────────┬──────────┘
                            │
                            ▼
                       Final Answer
```

The document ingestion pipeline is:

```text
Document
   │
   ▼
Loader
   │
   ▼
Text Cleaning
   │
   ▼
Chunking
   │
   ▼
Embeddings
   │
   ▼
Qdrant
```

Keeping these components separated makes it possible to replace or improve one component without redesigning the entire system.

For example:

* The embedding model can be changed without modifying the retriever.
* Qdrant can be replaced by another vector database.
* The LLM can be changed without modifying document ingestion.
* The chunking strategy can be modified independently.
* Additional document formats can be supported by adding new loaders.
* A reranking component can be added between retrieval and prompt construction.

This modularity is one of the main design choices of the project and provides a foundation for future scalability.

---

# Configuration

The application was designed to avoid hard-coding important parameters directly into the source code.

Most technical parameters can be modified through the `.env` configuration file and the application's settings/configuration modules.

For example:

```env
OLLAMA_MODEL=qwen2.5:7b

QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=company_documents

VECTOR_SIZE=768
DISTANCE=Cosine

SIMILARITY_THRESHOLD=0.65
TOP_K=5

NUM_CTX=4096
TEMPERATURE=0.2

MAX_CONTEXT_LENGTH=4000
```

This allows the behavior of the system to be adjusted without modifying the implementation itself.

Parameters such as:

* LLM model
* Embedding model
* Vector dimensions
* Qdrant configuration
* Similarity threshold
* Number of retrieved chunks
* Chunk size
* Chunk overlap
* Context length
* LLM temperature

can therefore be adapted according to the deployment environment and the characteristics of the documentation.

The project also centralizes application settings in dedicated configuration modules, providing a clear separation between **application logic and configuration**.

---

# Why Configurable Chunking?

Chunking is particularly important in a RAG system because it directly affects retrieval quality.

If chunks are too large:

```text
Large chunk
 ├── Relevant information
 ├── Unrelated information
 ├── More unrelated information
 └── More context
```

the retrieved context may contain unnecessary information.

If chunks are too small:

```text
Chunk 1 → incomplete information
Chunk 2 → missing context
Chunk 3 → incomplete sentence
```

important information may become fragmented.

For this reason, chunk size and overlap are configurable rather than fixed permanently in the code.

This makes it possible to experiment with different configurations depending on the document collection.

---

# Technology Stack

| Component            | Technology                      |
| -------------------- | ------------------------------- |
| Language             | Python                          |
| UI                   | Streamlit                       |
| RAG                  | Retrieval-Augmented Generation  |
| LLM                  | Qwen 2.5                        |
| LLM Runtime          | Ollama                          |
| Vector Database      | Qdrant                          |
| Embeddings           | 768-dimensional embedding model |
| Documents            | PDF, DOCX, TXT                  |
| Cloud Integration    | Google Drive                    |
| Integration Protocol | MCP                             |
| Authentication       | Google OAuth for Drive          |
| Configuration        | `.env` + Settings modules       |
| Testing              | Python automated/manual tests   |
| Version Control      | Git                             |
| CI/CD Foundation     | GitHub Actions workflow         |

---

# Project Structure

```text
rag-document-assistant/
│
├── app/
│   │
│   ├── chunking/
│   │   └── chunker.py
│   │
│   ├── documents/
│   │   └── document_manager.py
│   │
│   ├── embeddings/
│   │   └── embedding_model.py
│   │
│   ├── ingestion/
│   │   └── google_drive_ingestion.py
│   │
│   ├── llm/
│   │   └── llm.py
│   │
│   ├── mcp/
│   │   ├── google_drive_client.py
│   │   └── google_drive_service.py
│   │
│   ├── prompting/
│   │   ├── config.py
│   │   ├── prompt_builder.py
│   │   └── prompts/
│   │       └── system_prompt.txt
│   │
│   ├── rag/
│   │   └── rag_pipeline.py
│   │
│   ├── retrieval/
│   │   └── retriever.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   └── text_cleaner.py
│   │
│   ├── vector_store/
│   │   ├── config.py
│   │   └── vector_store.py
│   │
│   └── ui/
│       ├── streamlit_app.py
│       └── pages/
│           ├── assistant.py
│           ├── dashboard.py
│           └── documents.py
│
├── assets/
│   └── virtuoso-logo.png
│
├── tests/
│   ├── ...
│   └── manual/
│       └── test_google_drive_client.py
│
├── .github/
│   └── workflows/
│       └── ...
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# Testing

The project follows a **component-oriented testing approach**.

Individual components were tested independently before being integrated into the complete pipeline.

Examples include tests for:

* Document loading
* Text processing
* Chunk generation
* Embedding generation
* Vector database insertion
* Retrieval
* RAG pipeline behavior
* Google Drive MCP communication

For example, the embedding pipeline was validated to produce vectors with the expected dimension:

```text
Embedding dimension: 768
```

The ingestion pipeline was also tested by inserting generated chunks into the Qdrant collection.

This approach makes it easier to identify whether an issue comes from document processing, embeddings, retrieval, or generation rather than debugging the complete system as a single block.

---

# CI/CD Foundation

The repository also contains a `.github/workflows` directory as the starting point for a **continuous integration pipeline**.

The goal is to progressively automate tasks such as:

```text
Git Push
   │
   ▼
GitHub Actions
   │
   ├── Install dependencies
   ├── Run automated tests
   ├── Validate code
   └── Build / deployment checks
```

The workflow structure provides a foundation that can later be extended to include:

* Automated testing
* Linting
* Formatting checks
* Security checks
* Docker image building
* Deployment to AWS / Azure / GCP

This allows the development workflow to evolve toward a complete CI/CD process as the application moves closer to production deployment.

---
# Intent Classification and Future Agentic Architecture

The application also includes an **intent classification layer** designed to determine the type of request submitted by the user before executing the appropriate processing pipeline.

The objective is not only to improve the current RAG workflow, but also to provide an architectural foundation for evolving Virtuoso into a more advanced **AI agent**.

A simplified version of the architecture is:

```text
User Query
    │
    ▼
Intent Classification
    │
    ├── Document Question
    │       │
    │       ▼
    │     RAG Pipeline
    │
    ├── Document Management
    │       │
    │       ▼
    │     Document Tools
    │
    ├── Google Drive Request
    │       │
    │       ▼
    │     MCP / Google Drive
    │
    └── Other Intent
            │
            ▼
        Future Tools
```

The classifier allows the system to distinguish between different types of requests and route them toward the appropriate component instead of sending every request through the same RAG pipeline.

## Optional by Design

Intent classification is designed as an **optional layer** rather than a mandatory part of every request.

The classification itself can be performed by an LLM. Consequently, enabling it introduces an **additional model inference for each user request**, which increases:

* LLM usage
* Response latency
* Computational requirements
* Operational cost

For a simple internal question that can be directly handled by the RAG pipeline, performing an additional LLM classification step may therefore provide limited benefit compared with its cost.

For this reason, the system keeps intent classification configurable. It can be enabled when more complex routing is required, while the simpler RAG workflow remains available when classification is unnecessary.

## Foundation for an AI Agent

The intent classification architecture also provides a natural transition toward an **agent-based system**.

Instead of having the assistant only retrieve information from Qdrant, future versions could allow the model to decide which tools or actions are appropriate for a given request.

For example:

```text
                    User Query
                        │
                        ▼
                ┌───────────────┐
                │ Intent / LLM  │
                │   Router      │
                └───────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       RAG Tool     Drive Tool     Other Tools
          │             │             │
          ▼             ▼             ▼
       Qdrant       Google Drive    Future APIs
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                   Final Answer
```

This means that the current architecture does not need to be redesigned completely to support agentic capabilities later. New tools and integrations can be added behind the existing routing layer.

The long-term objective could therefore be to evolve from:

```text
User → RAG → Answer
```

toward:

```text
User → Agent → Tool Selection → Execution → Answer
```

while preserving the existing document processing and retrieval components.

This approach allows the project to remain **simple and cost-efficient in its current form**, while maintaining a clear technical path toward a more autonomous enterprise AI assistant.

---

# Evaluation

The RAG system was evaluated using a dataset of **30 questions** based on the company's documentation.

The evaluation considered:

* Answer correctness
* Source retrieval
* Retrieval recall
* Number of retrieved chunks
* Response time

The final evaluation achieved:

**27 / 30 correct answers**

The three incorrect cases were analyzed individually.

They included:

1. The system responding that the information was unavailable even though the required information was present in the retrieved context.
2. Contradictory information being present in two different documents, with the model selecting the information from the document that was not requested.
3. An answer being judged incorrect despite relevant information being retrieved.

These results indicate that the retrieval pipeline is generally effective while also highlighting areas for improvement in **generation reliability, source prioritization, contradiction handling, and retrieval strategy**.

---

# Future Improvements

The modular architecture makes it possible to progressively add more advanced capabilities.

### Retrieval

Potential improvements include:

* Hybrid semantic + keyword retrieval
* Reranking models
* Adaptive similarity thresholds
* Metadata filtering
* Improved chunking strategies
* Query expansion

### Generation

Potential improvements include:

* Better source attribution
* Contradiction detection
* Confidence estimation
* More advanced prompt strategies
* Structured citations

### Google Drive / MCP

The `mcp` branch is being developed toward:

* Google Drive document retrieval
* OAuth authentication
* Direct document import
* Incremental synchronization
* File modification detection
* Folder-based indexing

### Cloud Deployment

The application can eventually be deployed as a containerized service with:

* Cloud-managed authentication
* Managed Qdrant or another vector database
* Container orchestration
* Centralized logging
* Monitoring
* CI/CD deployment pipelines
* Enterprise access control

---

# Design Philosophy

The project follows several core principles:

### Modularity

Each major component has a well-defined responsibility.

### Configurability

Important parameters are exposed through configuration rather than being hard-coded.

### Testability

Components are tested independently before being integrated.

### Scalability

The architecture allows individual components to be replaced, optimized, or scaled independently.

### Separation of concerns

Document processing, retrieval, generation, UI, configuration, and external integrations remain separated.

### Cloud readiness

The application is designed so that infrastructure-level authentication and access management can be handled by the target cloud environment rather than being tightly coupled to the application itself.

---

# Project Context

Virtuoso was developed during a **two-month improvement internship at VIRTUO Technology, part of the EDGE Group**.

The objective was to design and develop an internal AI assistant capable of improving access to enterprise documentation through natural-language interaction.

The project combines:

**Artificial Intelligence + RAG + LLMs + Vector Databases + Document Processing + Enterprise Integrations**

into a modular internal application.

---

# Author

**Alae Mlaachiri**

AI & Data Science Engineering Student

VIRTUO Technology — EDGE Group
2026
