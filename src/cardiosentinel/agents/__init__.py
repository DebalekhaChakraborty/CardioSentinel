"""Agentic layer, grounded on frozen evidence.

Built in the order the audit required: the runtime first, then the decision
stream, then agents over it. Nothing here invents a number, and everything here
passes its output through the publication claim boundary before returning it.
"""

from .claims import ClaimBoundaryError, ClaimViolation, enforce, find_violations
from .evidence import EvidenceAgent, EvidenceRecord, GateExplanation

__all__ = [
    "ClaimBoundaryError",
    "ClaimViolation",
    "EvidenceAgent",
    "EvidenceRecord",
    "GateExplanation",
    "enforce",
    "find_violations",
]
