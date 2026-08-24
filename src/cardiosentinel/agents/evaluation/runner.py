"""Run both arms on identical evidence and emit the trade-off table.

Protocol §4. The only thing this module guarantees beyond bookkeeping is the
one guarantee that makes the numbers mean anything: **both arms receive the
same `ExplanationContext` object**, and a test asserts it.
"""

from __future__ import annotations

import time
from collections.abc import Sequence

from .. import claims
from ..context import ExplanationContext
from ..explain import TemplateRenderer
from .metrics import ExplanationScore, score_explanation
from .protocol import ARM_DETERMINISTIC, ARM_GENERATIVE, ArmResult, EvaluationReport

#: Disclaimers both arms are expected to quote in order to deny them.
_QUOTING: tuple[str, ...] = (claims.SYSTEM_BEHAVIOUR_ONLY,)


def _score_deterministic(
    contexts: Sequence[ExplanationContext],
) -> tuple[ExplanationScore, ...]:
    renderer = TemplateRenderer()
    scores = []
    for context in contexts:
        started = time.perf_counter()
        text = renderer.render(context)
        elapsed = time.perf_counter() - started
        scores.append(
            score_explanation(
                ARM_DETERMINISTIC,
                text,
                context,
                latency_seconds=elapsed,
                quoting=_QUOTING,
            )
        )
    return tuple(scores)


def _score_generative(
    contexts: Sequence[ExplanationContext], provider
) -> tuple[ExplanationScore, ...]:
    import json

    from ..explain import SYSTEM_BRIEF

    scores = []
    for context in contexts:
        payload = json.dumps(context.as_dict(), indent=2, default=str)
        started = time.perf_counter()
        text = provider.generate(SYSTEM_BRIEF, payload)
        elapsed = time.perf_counter() - started
        scores.append(
            score_explanation(
                ARM_GENERATIVE,
                text,
                context,
                latency_seconds=elapsed,
                quoting=_QUOTING,
            )
        )
    return tuple(scores)


def evaluate_arms(
    contexts: Sequence[ExplanationContext], *, provider=None
) -> EvaluationReport:
    """Both arms, identical input. `provider=None` leaves Arm B unexercised."""
    if not contexts:
        raise ValueError("no evidence contexts to evaluate")

    deterministic = _score_deterministic(contexts)
    arms = [
        ArmResult(
            arm=ARM_DETERMINISTIC,
            exercised=True,
            provider="template",
            scores=deterministic,
        )
    ]

    if provider is None:
        arms.append(
            ArmResult(
                arm=ARM_GENERATIVE,
                exercised=False,
                provider=None,
                note=(
                    "NOT EXERCISED: no provider configured in this environment. "
                    "The harness runs this arm in one command wherever "
                    "credentials exist."
                ),
            )
        )
    else:
        arms.append(
            ArmResult(
                arm=ARM_GENERATIVE,
                exercised=True,
                provider=getattr(provider, "name", "unknown"),
                scores=_score_generative(contexts, provider),
            )
        )

    # Protocol §6: Arm A can only emit values it was handed, so a violation or
    # a fidelity below 1.0 here is a defect in this repository, not a finding.
    defects: list[str] = []
    for score in deterministic:
        if score.violation_count:
            defects.append(
                f"deterministic arm produced {score.violation_count} claim "
                "violation(s); the template can only emit what it was given, "
                "so this is a defect here, not a result"
            )
        if score.fidelity is not None and score.fidelity < 1.0:
            defects.append(
                f"deterministic arm fabricated {list(score.fabricated_numbers)}; "
                "this is a defect here, not a result"
            )

    return EvaluationReport(
        contexts_evaluated=len(contexts),
        arms=tuple(arms),
        defects=tuple(defects),
    )


def render_report(report: EvaluationReport) -> str:
    """The trade-off table. Never a ranking."""
    lines = [
        "Evidence-Constrained Explanation Evaluation",
        f"Protocol: {report.protocol}",
        f"Evidence contexts evaluated: {report.contexts_evaluated}",
        "",
        f"{'Metric':<26}" + "".join(f"{arm.arm:>20}" for arm in report.arms),
        "-" * (26 + 20 * len(report.arms)),
    ]

    def row(label: str, render) -> str:
        return f"{label:<26}" + "".join(f"{render(arm):>20}" for arm in report.arms)

    def fmt(value, places=3, suffix=""):
        return "undefined" if value is None else f"{value:.{places}f}{suffix}"

    lines.append(
        row("exercised", lambda a: "yes" if a.exercised else "NOT EXERCISED")
    )
    lines.append(row("provider", lambda a: a.provider or "-"))
    lines.append(
        row(
            "evidence fidelity",
            lambda a: fmt(a.mean_fidelity) if a.exercised else "-",
        )
    )
    lines.append(
        row(
            "claim violations",
            lambda a: str(a.total_violations) if a.exercised else "-",
        )
    )
    lines.append(
        row(
            "completeness",
            lambda a: fmt(a.mean_completeness) if a.exercised else "-",
        )
    )
    lines.append(
        row(
            "latency",
            lambda a: fmt(a.mean_latency, 4, " s") if a.exercised else "-",
        )
    )
    lines.append("")

    for arm in report.arms:
        if not arm.exercised and arm.note:
            lines.append(f"  {arm.arm}: {arm.note}")
    if any(not arm.exercised for arm in report.arms):
        lines.append("")

    if report.defects:
        lines.append("DEFECTS IN THIS REPOSITORY, not findings about generation:")
        for defect in report.defects:
            lines.append(f"  - {defect}")
        lines.append("")

    lines.append("Reporting rules in force:")
    for rule in report.reporting_rules:
        lines.append(f"  - {rule}")
    lines.append("")
    lines.append(report.conclusion)
    return "\n".join(lines)
