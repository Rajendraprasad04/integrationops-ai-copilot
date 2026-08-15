"""Lightweight RAG Evaluation Runner.

Evaluates RAG pipeline performance across 5 metrics:
1. Source Document Recall / Hit Rate
2. Concept Coverage / Answer Correctness
3. Context Retrieval Relevance
4. Rule-based Faithfulness / Grounding
5. End-to-End Execution Latency
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.rag.pipeline import rag_pipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("eval_runner")


def calculate_concept_matches(text: str, concepts: List[str]) -> float:
    """Calculate proportion of expected concepts present in text."""
    if not concepts:
        return 1.0
    text_lower = text.lower()
    matches = sum(1 for c in concepts if c.lower() in text_lower)
    return matches / len(concepts)


def calculate_doc_hit_rate(retrieved_sources: List[Dict[str, Any]], expected_docs: List[str]) -> float:
    """Calculate ratio of expected source documents retrieved."""
    if not expected_docs:
        return 1.0
    retrieved_names = {s.get("document_name", "").lower() for s in retrieved_sources}
    hits = sum(1 for expected in expected_docs if expected.lower() in retrieved_names)
    return hits / len(expected_docs)


def calculate_faithfulness(answer: str, context_chunks: List[str], concepts: List[str]) -> float:
    """Rule-based grounding score: verifies if concepts in answer exist in retrieved context."""
    if not concepts:
        return 1.0
    combined_context = " ".join(context_chunks).lower()
    answer_lower = answer.lower()

    # Concepts present in answer must also be present in context
    supported_concepts = 0
    total_in_answer = 0

    for concept in concepts:
        c_lower = concept.lower()
        if c_lower in answer_lower:
            total_in_answer += 1
            if c_lower in combined_context:
                supported_concepts += 1

    if total_in_answer == 0:
        return 1.0
    return supported_concepts / total_in_answer


async def run_evaluation() -> Dict[str, Any]:
    """Run evaluation dataset through RAG pipeline and measure metrics."""
    questions_path = Path(__file__).parent / "questions.json"
    with open(questions_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    logger.info("Loaded %d evaluation benchmark questions", len(dataset))
    results = []

    total_doc_hit_rate = 0.0
    total_concept_coverage = 0.0
    total_context_relevance = 0.0
    total_faithfulness = 0.0
    total_latency_ms = 0.0

    for item in dataset:
        q_id = item["id"]
        question = item["question"]
        expected_concepts = item["expected_concepts"]
        expected_docs = item["expected_source_documents"]

        start_time = time.perf_counter()
        
        # Also measure retrieval step directly
        retrieval_hits = rag_pipeline.retriever.retrieve(query=question, top_k=3)
        pipeline_output = await rag_pipeline.ask(question=question, top_k=3)
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000.0

        answer = pipeline_output["answer"]
        retrieved_sources = pipeline_output["sources"]
        context_chunks = [hit.chunk_text for hit in retrieval_hits]

        # Calculate metrics
        doc_hit_rate = calculate_doc_hit_rate(retrieved_sources, expected_docs)
        concept_coverage = calculate_concept_matches(answer, expected_concepts)
        context_relevance = calculate_concept_matches(" ".join(context_chunks), expected_concepts)
        faithfulness = calculate_faithfulness(answer, context_chunks, expected_concepts)

        eval_entry = {
            "id": q_id,
            "question": question,
            "expected_source_documents": expected_docs,
            "retrieved_sources": [s.get("document_name") for s in retrieved_sources],
            "doc_hit_rate": round(doc_hit_rate, 4),
            "concept_coverage": round(concept_coverage, 4),
            "context_relevance": round(context_relevance, 4),
            "faithfulness": round(faithfulness, 4),
            "latency_ms": round(latency_ms, 2),
        }
        results.append(eval_entry)

        total_doc_hit_rate += doc_hit_rate
        total_concept_coverage += concept_coverage
        total_context_relevance += context_relevance
        total_faithfulness += faithfulness
        total_latency_ms += latency_ms

    num_q = len(dataset)
    summary = {
        "total_questions": num_q,
        "mean_doc_hit_rate": round(total_doc_hit_rate / num_q, 4),
        "mean_concept_coverage": round(total_concept_coverage / num_q, 4),
        "mean_context_relevance": round(total_context_relevance / num_q, 4),
        "mean_faithfulness": round(total_faithfulness / num_q, 4),
        "mean_latency_ms": round(total_latency_ms / num_q, 2),
        "per_question_results": results,
    }

    return summary


if __name__ == "__main__":
    report = asyncio.run(run_evaluation())
    print("\n" + "=" * 60)
    print("RAG EVALUATION REPORT SUMMARY")
    print("=" * 60)
    print(f"Total Questions Evaluated : {report['total_questions']}")
    print(f"Mean Source Doc Hit Rate   : {report['mean_doc_hit_rate'] * 100:.1f}%")
    print(f"Mean Concept Coverage      : {report['mean_concept_coverage'] * 100:.1f}%")
    print(f"Mean Context Relevance     : {report['mean_context_relevance'] * 100:.1f}%")
    print(f"Mean Faithfulness Score    : {report['mean_faithfulness'] * 100:.1f}%")
    print(f"Mean Pipeline Latency      : {report['mean_latency_ms']:.2f} ms")
    print("=" * 60 + "\n")
    print(json.dumps(report, indent=2))
