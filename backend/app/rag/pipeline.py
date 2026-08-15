"""RAG Pipeline orchestrator for grounded question answering and operational tool integration."""

import logging
from typing import Any, Dict, List, Optional

from app.agent.orchestrator import agent_orchestrator
from app.llm.client import BaseLLMClient, get_llm_client
from app.rag.retriever import RAGRetriever, rag_retriever

logger = logging.getLogger("app.rag.pipeline")

SYSTEM_PROMPT = """You are an expert AI Assistant for the IntegrationOps platform.
Your objective is to provide accurate, grounded answers to operational queries, integration statuses, and technical documentation questions.

STRICT GROUNDING INSTRUCTIONS:
1. Rely ONLY on the provided CONTEXT (Tool Outputs and Document Snippets) below to answer the question.
2. Do NOT invent, extrapolate, or introduce facts not directly supported by the context.
3. If operational metrics or job logs are provided in Tool Outputs, summarize the status, error message, and record counts clearly.
4. If documentation context is provided, explain the architecture or publishing flow accurately.
5. If provided context is insufficient, explicitly state: "I do not have sufficient evidence in the context to answer this question."
"""


class RAGPipeline:
    """Hybrid pipeline connecting operational tool execution, RAG retrieval, and LLM synthesis."""

    def __init__(
        self,
        retriever: Optional[RAGRetriever] = None,
        llm_client: Optional[BaseLLMClient] = None,
    ):
        self.retriever = retriever or rag_retriever
        self.llm_client = llm_client or get_llm_client()

    async def ask(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Execute hybrid tool & RAG pipeline for a user question."""
        logger.info("Executing pipeline for question: '%s'", question)

        # 1. Execute deterministic tools based on entity detection
        tools_used, tool_contexts = agent_orchestrator.analyze_and_execute_tools(question)

        # 2. Perform document retrieval (always run or when documentation context is needed)
        hits = self.retriever.retrieve(query=question, top_k=top_k)

        context_blocks: List[str] = []
        sources: List[Dict[str, Any]] = []
        seen_sources = set()

        # Add Tool Contexts
        if tool_contexts:
            context_blocks.append("--- OPERATIONAL TOOL OUTPUTS ---\n" + "\n\n".join(tool_contexts))

        # Add Document Contexts
        if hits:
            doc_blocks = []
            for hit in hits:
                doc_name = hit.metadata.get("document_name", "unknown.md")
                section = hit.metadata.get("section", "General")
                source_path = hit.metadata.get("source_path", "")

                doc_blocks.append(f"[Source: {doc_name} | Section: {section}]\n{hit.chunk_text}")

                source_key = (doc_name, section)
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    sources.append(
                        {
                            "document_name": doc_name,
                            "section": section,
                            "source_path": source_path,
                        }
                    )
            context_blocks.append("--- DOCUMENT CONTEXT ---\n" + "\n\n".join(doc_blocks))

        context_str = "\n\n".join(context_blocks) if context_blocks else "No context available."

        # 3. Construct user prompt
        user_prompt = f"""CONTEXT INFORMATION:
{context_str}

USER QUESTION:
{question}

Please answer the user question using ONLY the context provided above."""

        # 4. Synthesize answer via LLM
        answer = await self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
        )

        return {
            "answer": answer,
            "sources": sources,
            "tools_used": tools_used,
        }


# Global RAG Pipeline Singleton
rag_pipeline = RAGPipeline()
