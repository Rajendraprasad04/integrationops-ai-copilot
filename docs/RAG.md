# RAG Architecture & Grounded Generation Specification

## Executive Overview
**Retrieval-Augmented Generation (RAG)** is an architectural pattern that enhances Large Language Models (LLMs) by retrieving external, up-to-date domain documentation and injecting it into the prompt context prior to answer generation.

In **IntegrationOps AI Copilot**, RAG equips the copilot with operational manuals (architecture specs, scheduler rules, normalization pipelines, error guides) without requiring model re-training or fine-tuning.

---

## The RAG End-to-End Execution Flow

```
[ User Question ] ("What happens during publishing?")
       │
       ▼
[ Embedding Model ] ──► Encodes question into dense vector
       │
       ▼
[ InMemoryVectorStore ] ──► Calculates NumPy Cosine Similarity
       │
       ▼
[ Top-K Ranked Chunks ] ──► Retrieves relevant documentation snippets
       │
       ▼
[ Context Assembler ] ──► Formats chunks with source metadata headers
       │
       ▼
[ LLM Generation Client ] ──► Generates grounded answer adhering to system prompt
       │
       ▼
[ Grounded JSON Response ] ──► Returns { "answer": "...", "sources": [...] }
```

---

## Core Concepts Explained

### 1. RAG (Retrieval-Augmented Generation)
RAG combines non-parametric memory (external vector indexes over Markdown documentation) with parametric memory (pretrained LLMs). It ensures answers reflect real-time, domain-specific documentation rather than outdated pre-training knowledge.

### 2. Retrieval
The process of identifying and extracting the top-$K$ most relevant document chunks from the vector database for a given user query using dense vector cosine similarity.

### 3. Context
The structured prompt block assembled from retrieved document chunks. The context is injected into the user prompt alongside source metadata headers:
```text
[Source: publishing.md | Section: Pre-Publish Schema Validation]
Before executing SQL bulk upserts, the Publisher queries destination table metadata...
```

### 4. Grounding
Grounding enforces that the LLM's generated response is strictly derived from the provided context blocks. The system prompt instructs the model:
> *"Rely ONLY on the provided DOCUMENT CONTEXT... Do NOT invent unsupported facts... State explicitly when evidence is insufficient."*

### 5. Hallucination & Mitigation Strategies
- **Hallucination**: Occurs when an LLM generates plausible-sounding but factually incorrect or unsupported statements.
- **Mitigation in IntegrationOps**:
  - Low generation temperature ($\text{temperature} = 0.2$).
  - Strict system prompt guardrails.
  - Explicit fallback: *"I do not have sufficient evidence in the documentation to answer this question."*
  - Source citation tracking in API responses.

---

## Architectural Comparisons

### RAG vs Fine-Tuning

| Metric / Dimension | Retrieval-Augmented Generation (RAG) | Model Fine-Tuning |
|---|---|---|
| **Data Freshness** | **Real-time**: Instantly updates when `.md` files change. | **Static**: Requires expensive re-training cycles. |
| **Hallucination Risk** | **Low**: Output is strictly bound to retrieved context. | **Moderate to High**: Harder to audit exact knowledge sources. |
| **Traceability & Citations** | **High**: Exact source files and section names returned. | **None**: Knowledge is implicit within model weights. |
| **Compute / Financial Cost** | **Minimal**: In-memory vector search runs in <1ms. | **High**: Requires GPU training clusters. |
| **Primary Use Case** | Knowledge lookup, ops manuals, dynamic data. | Custom tone, specialized syntax, language style. |

---

## Retrieval Quality vs. Generation Quality

A production RAG pipeline's overall performance depends on two distinct layers:

1. **Retrieval Quality (Search Performance)**:
   - *Metrics*: Context Precision, Context Recall, Mean Reciprocal Rank (MRR).
   - *Failure Mode*: The retriever returns irrelevant chunks, or fails to retrieve the passage containing the answer.
2. **Generation Quality (LLM Performance)**:
   - *Metrics*: Faithfulness, Answer Relevance.
   - *Failure Mode*: The retriever found the correct chunk, but the LLM ignored it, misconstrued the facts, or hallucinated extra details.

By decoupling retrieval (`app/rag/retriever.py`) from generation (`app/llm/client.py`), IntegrationOps AI Copilot allows independent evaluation and optimization of both layers.
