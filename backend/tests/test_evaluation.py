import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pytest
from evaluation.eval_runner import run_evaluation


@pytest.mark.asyncio
async def test_evaluation_runner_execution():
    """Verify evaluation runner executes dataset and returns valid metric report structure."""
    report = await run_evaluation()
    assert report["total_questions"] == 5
    assert "mean_doc_hit_rate" in report
    assert "mean_concept_coverage" in report
    assert "mean_context_relevance" in report
    assert "mean_faithfulness" in report
    assert "mean_latency_ms" in report
    assert len(report["per_question_results"]) == 5

    # Check metric bounds
    assert 0.0 <= report["mean_doc_hit_rate"] <= 1.0
    assert 0.0 <= report["mean_faithfulness"] <= 1.0
    assert report["mean_latency_ms"] > 0.0
