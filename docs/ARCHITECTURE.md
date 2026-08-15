# IntegrationOps AI Copilot - System Architecture

## System Overview

The **IntegrationOps AI Copilot** is a decoupled, modular AI system designed to assist operations engineers in monitoring, diagnosing, and resolving integration pipeline issues. 

The architecture prioritizes **zero infrastructure friction**, **provider independence**, and **clean separation of concerns**.

```
[ React / Vite Frontend ]
           │  (REST API / JSON)
           ▼
[ FastAPI Application Layer ] (app/main.py)
   │               │               │
   ▼               ▼               ▼
[ Agent Engine ] [ RAG Engine ] [ Direct LLM ]
   │ (Tools)       │ (Retrieval)   │
   ├───────────────┼───────────────┘
   │               │
   ▼               ▼
[ Ops Tools ]  [ Vector Store ] (In-Memory / NumPy)
(JSON Data)        ▲
                   │ (Chunks & Embeddings)
               [ Document Chunker ]
                   ▲
               [ Ops Docs (Markdown) ]
```

---

## Key Architectural Principles

### 1. Provider-Independent LLM & Embedding Layer
To prevent vendor lock-in and allow seamless switching between cloud LLMs (OpenAI, Gemini, Anthropic) and local models (Ollama, mock/test providers), all AI components interact strictly with abstract interfaces:

- `LLMProvider` (`app/llm/base.py`): Enforces standard signature for text generation, structured outputs, and streaming.
- `EmbeddingProvider` (`app/llm/embeddings.py`): Enforces vector generation methods.
- `LLMFactory`: Instantiates runtime provider singletons based on `.env` configuration.

### 2. In-Memory Vector Store & Easy Database Migration
For the initial version, vector retrieval relies on an **in-memory vector store** powered by `NumPy` cosine similarity computations:

* **Why start in-memory?**
  - **Zero Database Setup**: Developer can run the project immediately with `pip install -r requirements.txt` without installing PostgreSQL, Docker, or Redis.
  - **Sub-Millisecond Speed**: For typical domain documentation (<5,000 chunks), NumPy vector operations are faster than local network round-trips to an external database.
  - **Zero Cost**: Works seamlessly in free serverless/container environments (Render, HuggingFace Spaces, Railway).

* **Migration Strategy to PostgreSQL + pgvector**:
  - The vector store implements an abstract interface `VectorStoreBase` (`add_documents`, `similarity_search`, `delete`).
  - When migrating to PostgreSQL, a new `PgVectorStore` class will be implemented wrapping `sqlalchemy` or `asyncpg` with the `pgvector` extension.
  - The RAG engine requires **zero code changes** because it consumes `VectorStoreBase`.

### 3. Synthetic Integration Operations Domain
All data sources are synthetic JSON datasets and local Markdown documents:
- `integrations.json`: Synthetic metadata for external API connections (e.g., Salesforce CRM sync, SAP ERP pipeline, Stripe webhook ingest).
- `jobs.json`: Execution history of data sync jobs, including status (`SUCCESS`, `FAILED`, `RUNNING`), duration, and timestamps.
- `logs.json`: Detailed error trace logs for troubleshooting failed integration runs.
- `docs/*.md`: Standard operating procedures, error code reference guides, and SLA resolution steps.

---

## Directory Structure

```
integrationops-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI application entrypoint & middleware
│   │   ├── config.py          # Environment settings with Pydantic BaseSettings
│   │   ├── api/               # API route handlers (/chat, /rag, /agent)
│   │   ├── llm/               # Provider-independent LLM & embedding wrappers
│   │   ├── rag/               # Chunking, indexing, and RAG search pipeline
│   │   ├── agent/             # Tool definitions and agent execution logic
│   │   └── models/            # Pydantic schemas for requests/responses
│   ├── data/                  # Synthetic JSON data & documentation files
│   ├── tests/                 # Unit & integration tests
│   ├── requirements.txt       # Minimal Python dependencies
│   └── .env.example           # Environment template
├── frontend/                  # React + Vite application
├── evaluation/                # Ground-truth Q&A set and eval runner script
├── docs/                      # Architectural & feature design specs
├── PROJECT_PLAN.md            # Detailed implementation roadmap
└── README.md                  # Project overview & getting started guide
```
