"""The publication claim boundary, enforced on generated text.

**This module is the reason the agentic layer is safe to build.** Every agent
here turns frozen evidence into prose, and prose is the easiest way in this
entire programme to make a claim the evidence does not support. Appendix A of
the Research Execution Handbook lists twenty-five such claims. Until now it was
a document a human was expected to remember. Here it is a function that fails.

**Scope, stated honestly.** This is a lexical guard, not a semantic one. It
catches the specific phrasings Appendix A names -- the ones that recur, that a
language model will reach for, and that a tired author will not notice. It
cannot catch a novel sentence that means the same thing. It reduces the failure
rate; it does not make overclaiming impossible, and no test here should be read
as saying it does.

**It also cannot tell an assertion from a disclaimer.** *"This does not support
a diagnosis"* trips claim 4 exactly as *"this yields a diagnosis"* does. That is
not a bug to be pattern-matched away -- negation detection by regex is a worse
failure mode than the one it fixes. The resolution is architectural:
`enforce` guards **generated** prose, and curated constant text that states what
the evidence cannot support is reviewed once by a human and passed through
`APPROVED_DISCLAIMERS` instead. This limitation was found by the guard firing on
the Evidence Agent's own disclaimer block, and it is pinned by a test.

**Word boundaries, not substrings.** A substring check for "proved" matches
"improved" and "Provenance"; this repository has already been bitten by that
roughly ten times. Every pattern here is anchored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: Appendix A of the Research Execution Handbook v1.3, as patterns. The claim
#: numbers are the handbook's own, so a violation can be looked up.
FORBIDDEN_CLAIMS: tuple[tuple[int, str, str, str], ...] = (
    (
        1,
        r"\bcausal(?:ly)?\s+(?:inference|effect|relationship)\b|\bcauses?\s+ischemia\b",
        "causal inference",
        "'Causal' here means temporal non-anticipation. Say 'causally ordered "
        "streaming' or 'non-anticipative'.",
    ),
    (
        2,
        r"\b(?:deployment[- ]ready|production[- ]ready|ready\s+for\s+deployment|"
        r"clinically\s+deployed)\b",
        "deployment readiness",
        "No predict(), no ONNX, no TorchScript, no serving path.",
    ),
    (
        3,
        r"\bgenerali[sz]e[sd]?\s+(?:to|across|beyond)\b|\bgenerali[sz]ation\s+to\b",
        "generalization beyond LTSTDB",
        "One dataset, 12 validation subjects. EDB is not independent.",
    ),
    (
        4,
        r"\bdiagnos(?:is|es|ed|tic)\b|\bclinical(?:ly)?\s+(?:useful|utility|benefit)\b",
        "clinical utility",
        "Detection, not diagnosis.",
    ),
    (
        5,
        r"\bedge\s+(?:performance|latency|benchmark)\b"
        r"|\bon[- ]device\s+(?:latency|performance)\b",
        "edge performance",
        "Benchmark-host numbers are not edge measurements.",
    ),
    (
        6,
        r"\b(?:outperform(?:s|ed|ing)?|improve[sd]?\s+(?:on|over)|better\s+than|"
        r"superior\s+to)\b",
        "unqualified improvement",
        "One improvement claim is permitted, and only with its operating-point "
        "clause: episode reasoning improves episode-level agreement relative to "
        "a memoryless window rule, on identical rows, at the promoted operating "
        "point.",
    ),
    (
        7,
        r"\bmemory\s+(?:contributes?|contribution|reduces?\s+false\s+alarms)\b",
        "memory contribution",
        "RQ1 is unanswered; there is no no-memory arm.",
    ),
    (
        8,
        r"\bS4D\s+(?:is\s+)?(?:better|superior|stronger)\b",
        "S4D superiority without selection context",
        "The pooled AUPRC contrast IS the selection rule.",
    ),
    (
        9,
        r"\bcalibrated\s+probabilit(?:y|ies)\b(?=[^.]*\b(?:T2|S4D|temporal)\b)|"
        r"\b(?:T2|S4D|temporal)\s+calibrated\s+probabilit",
        "calibrated probability for T2 scores",
        "score_is_calibrated_probability: false. A bounded sigmoid is not a "
        "probability.",
    ),
    (
        12,
        r"\btest\s+(?:set\s+)?(?:performance|accuracy|auprc|result)\b|"
        r"\bon\s+the\s+(?:sealed\s+)?test\s+set\b",
        "test performance",
        "The neural chain is unopened; the classical chain is spent.",
    ),
    (
        13,
        r"\bstatistical(?:ly)?\s+significan(?:t|ce)\b|\bp\s*[<>=]\s*0?\.\d+",
        "statistical significance",
        "The bootstrap is not a hypothesis test.",
    ),
    (
        14,
        r"\bselective\s+routing\s+(?:is\s+)?(?:implemented|deployed|enabled|active)\b",
        "selective routing implemented",
        "Retained: false. The router was evaluated and rejected.",
    ),
    (
        15,
        r"\bedge[/-]cloud\s+routing\b",
        "edge/cloud routing complete",
        "The router it refers to was rejected.",
    ),
    (
        16,
        r"\bconformal\s+prediction\b",
        "conformal prediction / U2",
        "Declared optional, never begun.",
    ),
    (
        17,
        r"\bearly\s+detection\b|\bwarning\s+time\b|\bpredictive\s+lead\s+time\b|"
        r"\banticipat(?:es|ed|ion)\s+the\s+episode\b",
        "early detection / warning time",
        "Matching is overlap-only with no tolerance window and no run durations "
        "are stored. A negative onset offset does not establish anticipation.",
    ),
    (
        21,
        r"\bfalse\s+alarms?\s+per\s+hour\b|\btemporal\s+IoU\b",
        "false alarms per hour / temporal IoU",
        "Specified in v1.1 §25.3 but never computed.",
    ),
    (
        22,
        r"\bS4D\s+outperform|\boutperform(?:s|ed)\s+(?:the\s+)?GRU\b",
        "S4D outperforms GRU",
        "The 95% paired interval on the difference includes zero.",
    ),
    (
        24,
        r"\bexternal(?:ly)?\s+validat(?:ed|ion)\b|\bEDB\b(?=[^.]*\bexternal\b)",
        "externally validated / EDB as external",
        "No drop-in independent cohort exists. EDB is a secondary cohort.",
    ),
)


@dataclass(frozen=True)
class ClaimViolation:
    claim_number: int
    label: str
    matched: str
    guidance: str

    def __str__(self) -> str:
        return (
            f"Appendix A claim {self.claim_number} ({self.label}): "
            f"matched {self.matched!r}. {self.guidance}"
        )


class ClaimBoundaryError(RuntimeError):
    """Generated text asserted something the evidence does not support."""


def find_violations(text: str) -> tuple[ClaimViolation, ...]:
    """Every forbidden phrasing in `text`, with the handbook claim it breaks."""
    found: list[ClaimViolation] = []
    for number, pattern, label, guidance in FORBIDDEN_CLAIMS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            found.append(
                ClaimViolation(
                    claim_number=number,
                    label=label,
                    matched=match.group(0),
                    guidance=guidance,
                )
            )
    return tuple(found)


#: The canonical closing sentence for any patient-facing explanation.
#:
#: One string, registered once. Every renderer and every generator brief uses
#: it verbatim rather than inventing a variant, because a variant would trip
#: the guard and each author would then be tempted to word around the boundary
#: instead of stating it.
SYSTEM_BEHAVIOUR_ONLY: str = (
    "This describes system behaviour only and does not establish a diagnosis."
)


#: Curated constant text that names a forbidden claim in order to disclaim it.
#: Reviewed by a human once, not generated per alert. Registering a string here
#: is a deliberate act; it is not a way to silence the guard on generated prose.
APPROVED_DISCLAIMERS: tuple[str, ...] = (
    SYSTEM_BEHAVIOUR_ONLY,
    "a diagnosis -- this is detection, and the programme's scope is detection",
    "anticipation of an episode -- matching is overlap-only, with no tolerance "
    "window and no stored run durations",
    "any claim about the sealed test, which is unopened",
    "generalisation beyond LTSTDB's twelve validation subjects",
    "a calibrated confidence -- the component that would have supplied one was "
    "evaluated and not retained",
)


def strip_approved_disclaimers(text: str) -> str:
    """Remove reviewed constant disclaimers before guarding generated prose."""
    for disclaimer in APPROVED_DISCLAIMERS:
        text = text.replace(disclaimer, "")
    return text


def audit(text: str) -> tuple[ClaimViolation, ...]:
    """Violations in `text`, ignoring registered disclaimers.

    **Use this, not `find_violations`, whenever the text may legitimately end
    with an approved disclaimer** -- which is every explanation this system
    produces. `enforce` and the generative path both call it, so the two cannot
    disagree about what compliant text looks like. They did once: the
    generative path checked raw text while the fallback stripped disclaimers,
    so a model that followed its brief exactly was rejected for doing so.
    """
    return find_violations(strip_approved_disclaimers(text))


def enforce(text: str) -> str:
    """Return `text`, or raise if it breaks the claim boundary.

    Agents call this on their own output before returning it. An agent that
    cannot phrase an answer within the boundary must fail loudly rather than
    quietly publish the claim.
    """
    violations = audit(text)
    if violations:
        detail = "\n".join(f"  - {violation}" for violation in violations)
        raise ClaimBoundaryError(
            f"Generated text breaks the publication claim boundary:\n{detail}"
        )
    return text
