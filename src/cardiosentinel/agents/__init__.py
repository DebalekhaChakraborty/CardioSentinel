"""Agentic layer, grounded on frozen evidence.

Built in the order the audit required: the runtime first, then the decision
stream, then agents over it. Nothing here invents a number, and everything here
passes its output through the publication claim boundary before returning it.
"""

from .architecture import (
    ARCHITECTURE_REGISTRY,
    ArchitectureSelectionAgent,
    CandidateArchitecture,
)
from .claims import (
    ClaimBoundaryError,
    ClaimViolation,
    audit,
    enforce,
    find_violations,
)
from .context import ExplanationContext, build_context
from .evidence import EvidenceAgent, EvidenceRecord, GateExplanation
from .explain import (
    DETERMINISTIC,
    GENERATIVE,
    Explanation,
    PatientExplanationAgent,
    TemplateRenderer,
)
from .graph import (
    EvidenceEdge,
    EvidenceGraph,
    EvidenceGraphError,
    EvidenceNode,
    build_evidence_graph,
    summarise_lineage,
)
from .research import (
    RESEARCH_REGISTRY,
    ResearchAssistantAgent,
    ResearchEvidence,
    ResearchQuestionError,
)

__all__ = [
    "ARCHITECTURE_REGISTRY",
    "ArchitectureSelectionAgent",
    "CandidateArchitecture",
    "ClaimBoundaryError",
    "ClaimViolation",
    "audit",
    "DETERMINISTIC",
    "GENERATIVE",
    "Explanation",
    "ExplanationContext",
    "RESEARCH_REGISTRY",
    "ResearchAssistantAgent",
    "ResearchEvidence",
    "ResearchQuestionError",
    "EvidenceAgent",
    "PatientExplanationAgent",
    "TemplateRenderer",
    "build_context",
    "EvidenceEdge",
    "EvidenceGraph",
    "EvidenceGraphError",
    "EvidenceNode",
    "EvidenceRecord",
    "GateExplanation",
    "build_evidence_graph",
    "summarise_lineage",
    "enforce",
    "find_violations",
]
