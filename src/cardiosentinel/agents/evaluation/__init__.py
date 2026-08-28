"""Evidence-constrained explanation evaluation.

Implements `docs/explanation/EXPLANATION_EVALUATION_PROTOCOL.md`. Lives under `agents/`
rather than the top-level `evaluation/` package, which is the research
evaluation code and already owns `protocol.py` and `metrics.py`.
"""

from .metrics import (
    COMPLETENESS_ELEMENTS,
    ExplanationScore,
    claim_violations,
    completeness,
    evidence_fidelity,
    score_explanation,
)
from .protocol import ARMS, REPORTING_RULES, ArmResult, EvaluationReport
from .runner import evaluate_arms, render_report

__all__ = [
    "ARMS",
    "COMPLETENESS_ELEMENTS",
    "REPORTING_RULES",
    "ArmResult",
    "EvaluationReport",
    "ExplanationScore",
    "claim_violations",
    "completeness",
    "evaluate_arms",
    "evidence_fidelity",
    "render_report",
    "score_explanation",
]
