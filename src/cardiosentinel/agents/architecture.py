"""Architecture Selection Intelligence: a candidate's lifecycle, from evidence.

**This agent explains selections. It does not make them and it does not
recommend.** The distinction is the whole point: the frozen record supports
*"B4-B was selected under a registered criterion"* and does not support
*"B4-B is the better architecture"*. An agent that recommended would be
asserting the second from evidence for the first.

**The timeline is what makes this more than retrieval.** A candidate is not a
row of metrics; it moved through stages -- proposed, protocol locked, measured,
decided -- and *when the criterion was fixed relative to when the evidence
existed* is what makes a selection prospective rather than post-hoc. Retrieval
over the same documents returns the metric and loses the ordering, which is the
part a reviewer actually needs.

Every answer passes `claims.enforce`, with each candidate's forbidden claims
declared as quotation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from . import claims


class ArchitectureQuestionError(RuntimeError):
    """No curated candidate covers this question, or the question is ambiguous."""


#: The lifecycle every candidate moves through. Closed, and ordered.
LIFECYCLE_STAGES = ("proposed", "protocol_locked", "measured", "decided")


@dataclass(frozen=True)
class LifecycleEvent:
    stage: str
    detail: str
    artifact: str | None = None

    def __post_init__(self) -> None:
        if self.stage not in LIFECYCLE_STAGES:
            raise ArchitectureQuestionError(
                f"Unknown lifecycle stage {self.stage!r}. Stages are closed: "
                f"{', '.join(LIFECYCLE_STAGES)}."
            )


@dataclass(frozen=True)
class CandidateArchitecture:
    """One candidate, its lifecycle, and what it does not establish."""

    key: str
    name: str
    family: str
    status: str
    selection_basis: str
    timeline: tuple[LifecycleEvent, ...]
    observed: dict[str, Any]
    limitations: tuple[str, ...]
    claims_allowed: tuple[str, ...]
    claims_forbidden: tuple[str, ...]
    source_document: str
    experiment_lock: str | None = None
    keywords: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


_B4_PROTOCOL = LifecycleEvent(
    "protocol_locked",
    "selection rule frozen before the deciding evidence existed",
    "docs/B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md",
)
_B4_PROPOSED = LifecycleEvent(
    "proposed",
    "predeclared as one of the B4-A/B/C/D families in handbook v1.1 §10.1, "
    "before any candidate was trained",
)
_B4_SOURCE = "docs/B4_GLOBAL_ENCODER_SELECTION_V1.md"


ARCHITECTURE_REGISTRY: tuple[CandidateArchitecture, ...] = (
    CandidateArchitecture(
        key="B4-A",
        name="B4-A compact CNN",
        family="B4 global encoder",
        status="Rejected",
        selection_basis="highest pooled validation AUPRC, predeclared",
        timeline=(
            _B4_PROPOSED,
            _B4_PROTOCOL,
            LifecycleEvent(
                "measured",
                "87,089 trainable parameters; median 3.274761 ms/window on the "
                "fixed benchmark host",
                "cardiosentinel-runs/phase3b2-b4-v1/B4_raw_compact_cnn_v1",
            ),
            LifecycleEvent(
                "decided", "not selected: lower pooled validation AUPRC than B4-B",
                _B4_SOURCE,
            ),
        ),
        observed={
            "trainable_parameter_count": 87089,
            "median_latency_ms_per_window": 3.274761,
            "latency_host": "fixed benchmark host, NOT edge hardware",
        },
        limitations=(
            "validation cohort only",
            "benchmark-host latency is not an edge measurement",
        ),
        claims_allowed=(
            "B4-A was evaluated under a predeclared rule and not selected",
            "B4-A is the smallest candidate, at 87,089 parameters",
        ),
        claims_forbidden=(
            "B4-A would perform worse on other data",
            "B4-A is unsuitable for edge deployment",
        ),
        source_document=_B4_SOURCE,
        experiment_lock="phase3b2-b4-v1/B4_raw_compact_cnn_v1/EXPERIMENT_LOCK.json",
        keywords=("b4-a", "b4a", "compact"),
    ),
    CandidateArchitecture(
        key="B4-B",
        name="B4-B CNN-Transformer",
        family="B4 global encoder",
        status="Selected",
        selection_basis="highest pooled validation AUPRC, predeclared",
        timeline=(
            _B4_PROPOSED,
            _B4_PROTOCOL,
            LifecycleEvent(
                "measured",
                "309,809 trainable parameters; median 4.161323 ms/window on the "
                "fixed benchmark host",
                "cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1",
            ),
            LifecycleEvent(
                "decided",
                "selected: highest pooled validation AUPRC of the three candidates",
                _B4_SOURCE,
            ),
        ),
        observed={
            "trainable_parameter_count": 309809,
            "median_latency_ms_per_window": 4.1613225,
            "latency_host": "fixed benchmark host, NOT edge hardware",
            "role": "the encoder every downstream component consumes",
        },
        limitations=(
            "validation cohort only; no external cohort exists",
            "no ablation, so the encoder's contribution is unmeasured",
            "no deployment-readiness claim",
        ),
        claims_allowed=(
            "B4-B was selected under a rule predeclared before the evidence existed",
            "B4-B had the highest pooled validation AUPRC of the three candidates",
        ),
        claims_forbidden=(
            "B4-B is the better architecture",
            "the encoder contributes measurably to detection performance",
        ),
        source_document=_B4_SOURCE,
        experiment_lock=(
            "phase3b2-architecture-v1/B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json"
        ),
        keywords=("b4-b", "b4b", "transformer", "encoder"),
    ),
    CandidateArchitecture(
        key="B4-C",
        name="B4-C CNN-SSM",
        family="B4 global encoder",
        status="Rejected",
        selection_basis="highest pooled validation AUPRC, predeclared",
        timeline=(
            _B4_PROPOSED,
            _B4_PROTOCOL,
            LifecycleEvent(
                "measured",
                "155,313 trainable parameters; median 14.436 ms/window, the "
                "slowest candidate on the fixed benchmark host",
                "cardiosentinel-runs/phase3b2-architecture-v1/B4C_cnn_ssm_v1",
            ),
            LifecycleEvent(
                "decided", "not selected: lower pooled validation AUPRC than B4-B",
                _B4_SOURCE,
            ),
        ),
        observed={
            "trainable_parameter_count": 155313,
            "median_latency_ms_per_window": 14.436,
            "recurrence_scope": (
                "window-internal: it recurs inside one 10-second window and "
                "discards state at the boundary"
            ),
        },
        limitations=(
            "validation cohort only",
            "its SSM block is diagonal and time-invariant, and is not Mamba",
        ),
        claims_allowed=(
            "B4-C was evaluated under a predeclared rule and not selected",
            "B4-C recurs within a window and discards state at the boundary",
        ),
        claims_forbidden=(
            "B4-C provides longitudinal modelling",
            "B4-C is the same class of model as the T2 longitudinal arm",
        ),
        source_document=_B4_SOURCE,
        experiment_lock="phase3b2-architecture-v1/B4C_cnn_ssm_v1/EXPERIMENT_LOCK.json",
        keywords=("b4-c", "b4c", "ssm", "mamba"),
    ),
    CandidateArchitecture(
        key="T2-GRU",
        name="T2 causal GRU longitudinal",
        family="T2 longitudinal arm",
        status="Comparator, not selected",
        selection_basis=(
            "pooled_primary_validation_auprc, frozen before outer validation"
        ),
        timeline=(
            LifecycleEvent(
                "proposed",
                "registered as the comparator arm in the T2 longitudinal protocol",
            ),
            LifecycleEvent(
                "protocol_locked",
                "selection basis and tie tolerance 0.002 frozen before the "
                "one-shot outer validation ran",
                "docs/T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md",
            ),
            LifecycleEvent(
                "measured",
                "scored in a single causal pass over the same held-out rows as "
                "S4D; pooled primary AUPRC 0.294870",
                "cardiosentinel-runs/phase8-t2-development-v1/t2-v1-outer-validation",
            ),
            LifecycleEvent(
                "decided",
                "not selected: the registered rule selected the other arm",
                "docs/T2_ARM_COMPARISON_REPORT_V1.md",
            ),
        ),
        observed={
            "pooled_primary_auprc": 0.294870,
            "subject_macro_auprc": 0.409737,
            "contributing_subjects": "9 of 12",
        },
        limitations=(
            "the subject-macro figure is a mean over 9 of 12 subjects",
            "the paired interval on the difference includes zero",
        ),
        claims_allowed=(
            "the GRU arm was trained and scored on identical held-out rows",
            "the registered rule did not select it",
        ),
        claims_forbidden=(
            "the GRU arm is worse",
            "S4D outperforms GRU",
        ),
        source_document="docs/T2_ARM_COMPARISON_REPORT_V1.md",
        experiment_lock=(
            "phase8-t2-development-v1/t2-v1-training/T2_GRU_CHECKPOINT_LOCK.json"
        ),
        keywords=("gru", "t2-gru"),
    ),
    CandidateArchitecture(
        key="T2-S4D",
        name="T2 causal S4D longitudinal",
        family="T2 longitudinal arm",
        status="Selected",
        selection_basis=(
            "pooled_primary_validation_auprc, frozen before outer validation"
        ),
        timeline=(
            LifecycleEvent(
                "proposed",
                "registered as the diagonal state-space arm in the T2 protocol",
            ),
            LifecycleEvent(
                "protocol_locked",
                "selection basis and tie tolerance 0.002 frozen before the "
                "one-shot outer validation ran; the budget is consumed",
                "docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md",
            ),
            LifecycleEvent(
                "measured",
                "pooled primary AUPRC 0.388085; difference over the GRU arm "
                "0.093215 against a tie tolerance of 0.002",
                "cardiosentinel-runs/phase8-t2-development-v1/t2-v1-outer-validation",
            ),
            LifecycleEvent(
                "decided",
                "selected by the registered rule; the 95% paired subject "
                "bootstrap on the difference is [-0.015229, 0.148951] and "
                "includes zero",
                "docs/T2_ARM_COMPARISON_REPORT_V1.md",
            ),
        ),
        observed={
            "pooled_auprc_difference": 0.093215,
            "tie_tolerance": 0.002,
            "paired_subject_bootstrap_95": [-0.015229, 0.148951],
            "interval_includes_zero": True,
            "pooled_primary_auprc": 0.388085,
            "score_is_calibrated_probability": False,
        },
        limitations=(
            "the difference IS the selection criterion, so the winner's absolute "
            "figure is conditioned on having been chosen",
            "the paired interval includes zero",
            "subject-macro is a mean over 9 of 12 subjects",
        ),
        claims_allowed=(
            "the predefined selection rule selected S4D based on the observed "
            "validation contrast",
            "the paired contrast is unbiased because the rule was fixed in advance",
            "the 95% paired interval on the difference includes zero",
        ),
        claims_forbidden=(
            "S4D outperforms GRU",
            "S4D is the better architecture",
            "the difference is statistically significant",
        ),
        source_document="docs/T2_ARM_COMPARISON_REPORT_V1.md",
        experiment_lock=(
            "phase8-t2-development-v1/t2-v1-training/T2_S4D_CHECKPOINT_LOCK.json"
        ),
        # Discriminative only. "arm" and "longitudinal" describe BOTH T2
        # candidates, and a shared keyword makes every question about either
        # one ambiguous -- the defect that sent a B4 question to T2 in #87.
        keywords=("s4d", "t2-s4d"),
    ),
    CandidateArchitecture(
        key="U1-router",
        name="U1 symmetric selective router",
        family="U1 uncertainty component",
        status="Rejected",
        selection_basis="prespecified retention guards in U1 protocol §16",
        timeline=(
            LifecycleEvent(
                "proposed", "registered as the selective-routing component of U1"
            ),
            LifecycleEvent(
                "protocol_locked",
                "c_star = 0.90, the calibration-agreement tolerance 0.02 and the "
                "asymmetric-abstention limit 3.0 all frozen in advance",
                "docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md",
            ),
            LifecycleEvent(
                "measured",
                "risk-agreement absolute error 0.006683691656635168; "
                "positive-label escalation 0.5167375624190864 against "
                "negative-label 0.0800696045937263",
                "cardiosentinel-runs/phase7-u1-development-v1/u1-v1-development",
            ),
            LifecycleEvent(
                "decided",
                "NOT retained: the calibration-agreement guard PASSED, and the "
                "asymmetric-abstention guard was RAISED at a ratio of "
                "6.453604523726777 against a limit of 3.0",
                "docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md",
            ),
        ),
        observed={
            "calibration_agreement_guard": "PASSED",
            "risk_agreement_absolute_error": 0.006683691656635168,
            "risk_agreement_tolerance": 0.02,
            "asymmetric_abstention_guard": "RAISED",
            "escalation_ratio": 6.453604523726777,
            "frozen_limit": 3.0,
            "accepted_sensitivity_at_u_star": 0.0007654037504783774,
        },
        limitations=(
            "development evidence only, at one frozen operating point",
            "the rejected router is preserved as immutable ablation evidence",
        ),
        claims_allowed=(
            "the router was implemented and evaluated against prespecified guards",
            "the router was not retained",
            "one guard passed and a different guard was raised",
            "RQ3 is answered negatively, which is a real result",
        ),
        claims_forbidden=(
            "uncertainty estimation is ineffective",
            "selective prediction does not work",
            "the router would fail at any other operating point",
            "selective routing is implemented or deployed",
        ),
        source_document="docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md",
        experiment_lock="phase7-u1-development-v1/u1-v1-development/U1_EXPERIMENT_LOCK.json",
        keywords=("router", "routing", "selective", "abstention", "u1"),
    ),
)


def find_candidate(question: str) -> CandidateArchitecture:
    """Match a question to exactly one candidate, or refuse.

    Ties are refused rather than resolved by declaration order: answering
    confidently about the wrong candidate is the failure this design prevents.
    """
    words = {word.strip("?.,'\"").lower() for word in question.split()}
    scored = [
        (sum(1 for keyword in item.keywords if keyword in words), item)
        for item in ARCHITECTURE_REGISTRY
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    best_score = scored[0][0]
    tied = [item for score, item in scored if score == best_score and best_score]
    if not tied:
        raise ArchitectureQuestionError(
            f"No curated candidate covers {question!r}. Known candidates: "
            + ", ".join(item.key for item in ARCHITECTURE_REGISTRY)
            + ". The agent explains recorded selections; it does not recommend "
            "architectures and does not evaluate new ones."
        )
    if len(tied) > 1:
        raise ArchitectureQuestionError(
            f"{question!r} matches {len(tied)} candidates equally "
            f"({', '.join(item.key for item in tied)}). Name one; the agent "
            "does not guess between candidates."
        )
    return tied[0]


class ArchitectureSelectionAgent:
    """Explains a candidate's lifecycle. Never recommends."""

    def explain(self, question: str) -> str:
        candidate = find_candidate(question)
        lines = [
            f"Candidate        {candidate.name}",
            f"Family           {candidate.family}",
            f"Status           {candidate.status}",
            f"Selection basis  {candidate.selection_basis}",
            "",
            "Lifecycle:",
        ]
        for index, event in enumerate(candidate.timeline, start=1):
            lines.append(f"  {index}. {event.stage.replace('_', ' ')}")
            lines.append(f"     {event.detail}")
            if event.artifact:
                lines.append(f"     evidence: {event.artifact}")
        lines.append("")
        lines.append("Observed, read from the frozen record:")
        for key, value in candidate.observed.items():
            lines.append(f"  {key:38s} {value}")
        lines.append("")
        lines.append("Known limitations:")
        for item in candidate.limitations:
            lines.append(f"  - {item}")
        lines.append("")
        lines.append("This evidence supports:")
        for item in candidate.claims_allowed:
            lines.append(f"  + {item}")
        lines.append("")
        lines.append("This evidence does NOT support:")
        for item in candidate.claims_forbidden:
            lines.append(f"  - {item}")
        lines.append("")
        lines.append(f"Source           {candidate.source_document}")
        if candidate.experiment_lock:
            lines.append(f"Experiment lock  {candidate.experiment_lock}")
        return claims.enforce(
            "\n".join(lines), quoting=candidate.claims_forbidden
        )
