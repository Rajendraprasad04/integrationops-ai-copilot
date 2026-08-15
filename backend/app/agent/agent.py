"""Single-Agent Orchestrator for IntegrationOps AI Copilot."""

import logging
from typing import Any, Dict, List, Optional

from app.agent.orchestrator import agent_orchestrator
from app.llm.client import BaseLLMClient, get_llm_client
from app.rag.retriever import RAGRetriever, rag_retriever

logger = logging.getLogger("app.agent.agent")

AGENT_SYSTEM_PROMPT = """You are the lead AI IntegrationOps Copilot.
Your job is to diagnose integration failures, inspect job execution traces, and explain platform operating procedures.

AGENT EXECUTION RULES:
1. Examine the provided OBSERVATIONS (Tool Outputs and Documentation Context).
2. For job-specific questions, explain the job status, failing service, error message, and log trace.
3. For platform documentation questions, explain the standard workflow or configuration rules.
4. For combined questions, synthesize BOTH the specific job failure diagnosis and the standard operating procedure.
5. Rely ONLY on the provided observations. Do NOT invent unsupported facts.
"""


class IntegrationOpsAgent:
    """Single-Agent orchestrator managing decision making, tool execution, observation gathering, and synthesis."""

    def __init__(
        self,
        retriever: Optional[RAGRetriever] = None,
        llm_client: Optional[BaseLLMClient] = None,
    ):
        self.retriever = retriever or rag_retriever
        self.llm_client = llm_client or get_llm_client()

    async def run(self, question: str) -> Dict[str, Any]:
        """Execute agent workflow: Question -> Decision -> Action -> Observation -> Final Response."""
        logger.info("Agent processing question: '%s'", question)

        # Step 1: Decision & Tool Action (Analyze question & execute tools if needed)
        tools_used, tool_contexts = agent_orchestrator.analyze_and_execute_tools(question)

        # Step 2: RAG Retrieval Action (Execute RAG search for document context)
        hits = self.retriever.retrieve(query=question, top_k=3)

        # Step 3: Collect Observations
        observation_blocks: List[str] = []
        sources: List[Dict[str, Any]] = []
        seen_sources = set()

        if tool_contexts:
            observation_blocks.append("--- TOOL OBSERVATIONS ---\n" + "\n\n".join(tool_contexts))

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
            observation_blocks.append("--- DOCUMENTATION OBSERVATIONS ---\n" + "\n\n".join(doc_blocks))

        observation_str = "\n\n".join(observation_blocks) if observation_blocks else "No observations available."

        # Step 4: Final Response Generation
        user_prompt = f"""OBSERVATIONS:
{observation_str}

USER QUESTION:
{question}

Synthesize a clear, grounded answer addressing the user's question using ONLY the observations above."""

        answer = await self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=AGENT_SYSTEM_PROMPT,
        )

        return {
            "answer": answer,
            "sources": sources,
            "tools_used": tools_used,
        }


# Global Single-Agent Singleton instance
integration_ops_agent = IntegrationOpsAgent()
