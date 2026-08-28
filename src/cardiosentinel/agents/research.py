"""The Evidence-Grounded Research Assistant: retrieval over structure, not prose.

**It answers only from curated research evidence objects.** It never reads a
`_V1` document at runtime, never embeds one, and never searches. That is the
deliberate difference between this and a retrieval chatbot: a RAG system over
these documents would happily answer *"was the router any good?"* with a
plausible paragraph assembled from sentences that were never meant to sit
together. This one can only say what an evidence object records, and each
object carries the claims it licenses **and the claims it forbids**.

**The name is chosen carefully.** It is an assistant, not a scientist. It
retrieves, traces, explains and audits. It does not discover, and it does not
form hypotheses -- and the paper should say so, because that restraint is the
contribution rather than a shortfall.

**How the objects were made.** Each one was curated by hand from the merged
report or retention decision it cites, at authoring time, and its values are
checked against the frozen artifacts by
`tests/agents/test_research_assistant.py`. Curation at authoring time plus
verification at test time is what lets the runtime avoid touching prose at all.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from . import claims


class ResearchQuestionError(RuntimeError):
    """The assistant has no evidence object for this question."""


@dataclass(frozen=True)
class ResearchEvidence:
    """One curated research finding, with its permission boundary attached."""

    topic: str
    question: str
    component: str
    decision: str
    basis: dict[str, Any]
    claims_allowed: tuple[str, ...]
    claims_forbidden: tuple[str, ...]
    source_document: str
    source_lock: dict[str, Any] = field(default_factory=dict)
    keywords: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


RESEARCH_REGISTRY: tuple[ResearchEvidence, ...] = (
    ResearchEvidence(
        topic="u1_router_rejected",
        question="Why was the selective router rejected?",
        component="U1 symmetric window-level selective router at c_star = 0.90",
        decision="evaluated and NOT retained",
        basis={
            "calibration_agreement_guard": "PASSED",
            "risk_agreement_absolute_error": 0.006683691656635168,
            "risk_agreement_tolerance": 0.02,
            "asymmetric_abstention_guard": "RAISED",
            "positive_label_escalation_fraction": 0.5167375624190864,
            "negative_label_escalation_fraction": 0.0800696045937263,
            "escalation_ratio": 6.453604523726777,
            "frozen_asymmetric_abstention_limit": 3.0,
            "accepted_sensitivity_at_u_star": 0.0007654037504783774,
            "u_star_dev": 0.12763774358328017,
            "achieved_coverage": 0.9000014771142253,
            "reason": (
                "at the frozen operating point the router escalated "
                "positive-label windows 6.45 times as often as negative-label "
                "windows, against a limit of 3.0 fixed in advance"
            ),
        },
        claims_allowed=(
            "the router was implemented and evaluated against prespecified guards",
            "the router was not retained",
            "the asymmetric-abstention guard was raised",
            "the calibration-agreement guard passed",
            "RQ3 is answered negatively, which is a real result",
        ),
        claims_forbidden=(
            "uncertainty estimation is ineffective",
            "selective prediction does not work",
            "the router would fail at any other operating point",
            "selective routing is implemented or deployed",
        ),
        source_document="docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md",
        source_lock={
            "experiment_id": "u1-v1-development",
            "test_accessed": False,
            "sealed_test_state": "unopened",
        },
        keywords=("router", "routing", "rejected", "selective", "rq3", "abstention"),
    ),
    ResearchEvidence(
        topic="u1_calibration_retained",
        question="Why was Platt calibration retained?",
        component="U1 Platt calibration on the recovered logit",
        decision="retained, as a probability transformation only",
        basis={
            "selection_criterion": "pooled_out_of_fold_negative_log_likelihood",
            "platt_nll": 0.14370784818131235,
            "baseline_nll": 0.23170495211589118,
            "platt_brier": 0.040344375976781484,
            "baseline_brier": 0.0635671818303644,
            "protocol_condition_2": "Brier and NLL both lower than baseline: holds",
            "classification_disagreements": 0,
            "baseline_is_out_of_fold": False,
            "caveat": (
                "the uncalibrated baseline is a reference, not out-of-fold "
                "evidence, so the two rows are not a matched comparison"
            ),
        },
        claims_allowed=(
            "calibration was retained as a probability transformation",
            "it changes no detection decision: zero classification disagreements",
            "pooled OOF Brier and NLL are both lower than the baseline",
        ),
        claims_forbidden=(
            "calibration improves detection performance",
            "the ECE improvement alone justifies retention",
            "the baseline comparison is matched",
        ),
        source_document="docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md",
        source_lock={"experiment_id": "u1-v1-development", "test_accessed": False},
        keywords=("calibration", "platt", "retained", "calibrated", "nll", "brier"),
    ),
    ResearchEvidence(
        topic="t2_s4d_selected",
        question="Why was S4D selected instead of GRU?",
        component="T2 longitudinal arm",
        decision="S4D selected by the predefined rule; no superiority established",
        basis={
            "selection_basis": "pooled_primary_validation_auprc",
            "selected_arm": "causal_s4d_longitudinal_v1",
            "pooled_auprc_difference": 0.093215,
            "tie_tolerance": 0.002,
            "paired_subject_bootstrap_95": [-0.015229, 0.148951],
            "interval_includes_zero": True,
            "subject_macro_contributing_subjects": "9 of 12",
            "reason": (
                "the rule was fixed before the deciding evidence existed and "
                "S4D had the higher pooled validation AUPRC; the paired "
                "interval on the difference includes zero"
            ),
        },
        claims_allowed=(
            "the predefined selection rule selected S4D based on the observed "
            "validation contrast",
            "the paired contrast is unbiased because the rule was fixed in advance",
            "the 95% paired subject-bootstrap interval includes zero",
        ),
        claims_forbidden=(
            "S4D outperforms GRU",
            "S4D is the better architecture",
            "the difference is statistically significant",
            "the selected arm's absolute AUPRC is an unbiased performance estimate",
        ),
        source_document="docs/experiments/t2/T2_ARM_COMPARISON_REPORT_V1.md",
        source_lock={
            "experiment_id": "t2-v1-outer-validation",
            "test_accessed": False,
            "sealed_test_state": "unopened",
        },
        keywords=("s4d", "gru", "t2", "longitudinal", "arm"),
    ),
    ResearchEvidence(
        topic="w1_rq4_answered",
        question="Does episode reasoning help, and how much?",
        component="W1 window-only comparator",
        decision="RQ4 supported, bounded at one operating point",
        basis={
            "arm_t1_subject_macro_episode_f1": 0.2524,
            "arm_window_subject_macro_episode_f1": 0.0603,
            "difference": 0.1921,
            "paired_subject_bootstrap_95": [0.0505, 0.3455],
            "interval_excludes_zero": True,
            "bound": (
                "both arms ran at thresholds selected with the state machine in "
                "the loop; a well-tuned memoryless rule was never tested"
            ),
            "registered_predictions_refuted": 2,
        },
        claims_allowed=(
            "episode reasoning improves episode-level agreement relative to a "
            "memoryless window rule, on identical rows, at the promoted "
            "operating point",
            "the 95% paired interval excludes zero",
            "two registered predictions were refuted and reported as refuted",
        ),
        claims_forbidden=(
            "episode reasoning improves monitoring quality in general",
            "the state machine beats any memoryless alerting rule",
            "W1 says anything about the S4D architecture's contribution",
        ),
        source_document="docs/experiments/w1/W1_WINDOW_COMPARATOR_REPORT_V1.md",
        source_lock={"experiment_id": "t1-v1-measurement-continuation"},
        keywords=("w1", "episode", "rq4", "comparator", "memoryless", "state machine"),
    ),
    ResearchEvidence(
        topic="b4b_encoder_selected",
        question="Why was the B4-B encoder selected?",
        component="B4 global encoder",
        decision="B4-B selected",
        basis={
            "candidates": ["B4-A compact CNN", "B4-B CNN+Transformer", "B4-C CNN+SSM"],
            "selected": "B4-B",
            "trainable_parameter_count": 309809,
            "reason": "B4-B had the highest pooled validation AUPRC",
            "b4c_note": (
                "B4-C recurs inside one 10-second window and discards state at "
                "the boundary, so it is not longitudinal modelling"
            ),
        },
        claims_allowed=(
            "B4-B was selected under a rule predeclared before the evidence existed",
            "B4-B had the highest pooled validation AUPRC of the three candidates",
        ),
        claims_forbidden=(
            "B4-C provides longitudinal modelling",
            "the encoder contributes measurably to detection performance",
        ),
        source_document="docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md",
        source_lock={"experiment_id": "B4B_cnn_transformer_v1", "test_accessed": False},
        keywords=("b4", "b4-b", "b4b", "encoder", "transformer", "cnn", "ssm"),
    ),
    ResearchEvidence(
        topic="sealed_test_consumed",
        question="What happened in the B4 sealed evaluation?",
        component="B4-B / neural sealed evaluation",
        decision="consumed once; attempt 1 COMPLETE; repeat prohibited",
        basis={
            "budgets_tracked": 15,
            "budgets_spent": 15,
            "test_attempt_files_present": 1,
            "attempt_sequence": 1,
            "attempt_status": "COMPLETE",
            "repeat_attempt_permitted": False,
            "registered_primary": "pooled-window AUPRC",
            "pooled_auprc": 0.0935334,
            "prevalence": 0.0460529,
            "subject_macro_auprc": 0.354901,
            "subject_macro_contributing_subjects": "8 of 12",
            "subject_bootstrap_95": [0.033058, 0.239284],
            "comparison": (
                "B4-B was below B1, B2 and B3, and above only the constant "
                "prior; this confirmed the development ordering"
            ),
            "result_available_through": (
                "docs/experiments/b4/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md"
            ),
            "boundary": (
                "one attempt, twelve subjects, one dataset, uncalibrated "
                "scores, and no independent cohort for corroboration"
            ),
        },
        claims_allowed=(
            "the B4-B sealed evaluation was consumed exactly once",
            "attempt 1 completed and repeat is prohibited",
            "the registered primary pooled-window AUPRC is 0.0935334, with "
            "its pre-registered boundary attached",
            "the post-hoc analysis explains existing values and authorizes no "
            "experiment",
        ),
        claims_forbidden=(
            "B4-B outperforms the classical baselines",
            "the result establishes generalization or clinical utility",
            "the assembled IPS has a sealed evaluation result",
            "a second attempt is permitted",
        ),
        source_document="docs/experiments/b4/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md",
        source_lock={
            "experiment_id": "B4B_cnn_transformer_v1",
            "sealed_test_state": "consumed",
            "test_accessed": True,
            "attempt_sequence": 1,
            "attempt_status": "COMPLETE",
            "repeat_attempt_permitted": False,
        },
        keywords=(
            "b4",
            "sealed",
            "test",
            "consumed",
            "unopened",
            "attempt",
            "budget",
            "result",
        ),
    ),
)


def find_evidence(question: str) -> ResearchEvidence:
    """Match a question to exactly one curated evidence object, or refuse.

    Keyword matching, deliberately. Semantic retrieval would let the assistant
    answer questions no object covers, which is the failure this design exists
    to prevent.
    """
    words = {word.strip("?.,'\"").lower() for word in question.split()}
    scored = [
        (sum(1 for keyword in item.keywords if keyword in words), item)
        for item in RESEARCH_REGISTRY
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    best_score, best = scored[0]
    # An ambiguous question is refused, not guessed. Two topics scoring equally
    # means the keywords are not discriminating, and answering from whichever
    # happened to be declared first is how an assistant gives a confident
    # answer about the wrong experiment.
    tied = [item for score, item in scored if score == best_score and best_score]
    if len(tied) > 1:
        raise ResearchQuestionError(
            f"{question!r} matches {len(tied)} topics equally "
            f"({', '.join(item.topic for item in tied)}). Ask about one of them "
            "specifically; the assistant does not guess between experiments."
        )
    if best_score == 0:
        raise ResearchQuestionError(
            f"No curated research evidence covers {question!r}. The assistant "
            "answers only from evidence objects; it does not search documents "
            "and does not speculate. Known topics: "
            + ", ".join(item.topic for item in RESEARCH_REGISTRY)
            + "."
        )
    return best


class ResearchAssistantAgent:
    """Retrieves, traces, explains and audits. It does not discover."""

    def answer(self, question: str) -> str:
        evidence = find_evidence(question)
        lines = [
            f"Question   {question}",
            f"Component  {evidence.component}",
            f"Decision   {evidence.decision}",
            "",
            "Basis, read from the frozen record:",
        ]
        for key, value in evidence.basis.items():
            lines.append(f"  {key:42s} {value}")
        lines.append("")
        lines.append("This evidence supports:")
        for claim in evidence.claims_allowed:
            lines.append(f"  + {claim}")
        lines.append("")
        lines.append("This evidence does NOT support:")
        for claim in evidence.claims_forbidden:
            lines.append(f"  - {claim}")
        lines.append("")
        lines.append(f"Source     {evidence.source_document}")
        if evidence.source_lock:
            for key, value in evidence.source_lock.items():
                lines.append(f"  {key:42s} {value}")
        # `claims_forbidden` quotes forbidden claims in order to prohibit
        # them, so the agent declares them as quotation. Everything else in
        # the answer is still guarded normally.
        return claims.enforce(
            "\n".join(lines), quoting=evidence.claims_forbidden
        )
