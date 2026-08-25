"""The Patient Explanation Agent: language over evidence, never instead of it.

**The generator is a communication layer, not a source of truth.** The chain is
sensor -> runtime -> evidence -> explanation, and only the last hop is
generative. If the model is unavailable, unconfigured, slow, or produces
something that breaks the publication claim boundary, the agent falls back to a
deterministic template renderer and **says that it did**.

That fallback is the design, not an error path. An intelligent physical system
that answers *"explanation service unavailable"* when its language model is down
has confused its communication layer for its intelligence. This one still says
what happened; it just says it in rules-generated prose and labels it as such.

**Transparency is mandatory.** Every `Explanation` carries `explanation_mode`,
so nobody has to guess whether prose came from a model or a template::

    {"explanation_mode": "GENERATIVE",    "context_source": "EVIDENCE_GRAPH"}
    {"explanation_mode": "DETERMINISTIC", "fallback_reason": "no provider configured"}

**What the generator may see** is `ExplanationContext` and nothing else -- no
handbook, no reports, no research prose. See `context.py`.
"""

from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from . import claims
from .context import ExplanationContext, build_context
from .graph import EvidenceGraph

GENERATIVE = "GENERATIVE"
DETERMINISTIC = "DETERMINISTIC"

#: The instruction a generator receives. It is deliberately a translation brief.
SYSTEM_BRIEF = """\
You are a translator for a cardiac monitoring system, not a clinician and not
an analyst.

Rewrite the supplied JSON as a short factual paragraph for a technically
literate reader. Rules, all mandatory:

- Use only the values in the JSON. Introduce no number, cause or mechanism that
  is not there.
- `temporal_support_bounded_score` is a bounded score, NOT a probability. Never
  call it one.
- If `safety.learning_blocked` is true, say that the system declined to update
  the patient baseline and give the reason from `safety.reasons`. This is a
  control working correctly, not a fault.
- Describe system behaviour only. Do not diagnose, do not speculate about the
  patient's condition, and do not say the system detected disease.
- Do not claim the finding generalises, is statistically significant, or was
  externally validated.
- End with this sentence, copied EXACTLY, changing nothing:
  "{disclaimer}"
"""

SYSTEM_BRIEF = SYSTEM_BRIEF.format(disclaimer=claims.SYSTEM_BEHAVIOUR_ONLY)


class ExplanationProvider(Protocol):
    """Anything that can turn a brief plus JSON into prose."""

    name: str

    def generate(self, brief: str, payload: str) -> str: ...


@dataclass(frozen=True)
class Explanation:
    text: str
    explanation_mode: str
    context_source: str = "EVIDENCE_GRAPH"
    provider: str | None = None
    fallback_reason: str | None = None
    claim_violations: tuple[str, ...] = ()
    context: dict[str, Any] = field(default_factory=dict)
    #: Model id WITH revision, e.g. `Qwen/Qwen3-1.7B@<sha>`. A bare tag is a
    #: moving pointer; provenance here is expected to outlive the tag moving.
    model: str | None = None
    #: Wall clock for the path actually taken, generative or deterministic.
    #: Not comparable across hosts, and reported with that caveat.
    latency_seconds: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _number(value: float | None, places: int = 3) -> str:
    return "undefined" if value is None else f"{value:.{places}f}"


class TemplateRenderer:
    """The deterministic renderer. Always available, never surprising."""

    name = "template"

    def render(self, context: ExplanationContext) -> str:
        event = context.event
        evidence = context.evidence
        safety = context.safety

        sentences: list[str] = []
        duration = event.get("duration_seconds")
        span = (
            f"for {duration:.0f} seconds across {event.get('window_count')} windows"
            if duration is not None
            else f"across {event.get('window_count')} windows and was still "
            "active when the stream ended"
        )
        sentences.append(
            f"The system entered the EVENT state at {event.get('opened_at')}, "
            f"from {event.get('entered_from')}, and held it {span}."
        )
        sentences.append(
            "At its strongest the calibrated probability reached "
            f"{_number(evidence.get('calibrated_probability'))} and the bounded "
            "temporal support score reached "
            f"{_number(evidence.get('temporal_support_bounded_score'))}; the "
            "deviation from this patient's learned baseline reached "
            f"{_number(evidence.get('memory_deviation'))}."
        )
        if safety.get("learning_blocked"):
            reasons = "; ".join(safety.get("reasons", ())) or "a safety condition"
            sentences.append(
                "During this period the system declined to update the patient's "
                f"baseline, because {reasons}. That is the contamination "
                "control behaving as designed."
            )
        else:
            sentences.append(
                "The patient's baseline continued to update during this period."
            )
        # The one canonical disclaimer, registered in `claims`. Not reworded.
        sentences.append(claims.SYSTEM_BEHAVIOUR_ONLY)
        return " ".join(sentences)


class PatientExplanationAgent:
    """Graph in, guarded explanation out, with the mode always declared.

    **Two gates, not one.** `claims.audit` is lexical and cannot catch a
    fabricated *number*: asked to describe `peak_probability = 0.545613`, a
    model that writes "an estimated peak probability of 54.6%" passes the claim
    guard cleanly, because a percentage breaks no forbidden-claim pattern. So
    generated text is additionally scored for evidence fidelity and falls back
    when it states a number the evidence does not contain.
    """

    @staticmethod
    def _fidelity(text: str, context: ExplanationContext) -> float | None:
        """Fraction of stated numbers present in the evidence, or `None`.

        Imported lazily: `evaluation` imports `runner`, which imports this
        module, so a module-level import would be circular.
        """
        from .evaluation.metrics import evidence_fidelity

        return evidence_fidelity(text, context)

    @staticmethod
    def _states_a_percentage(text: str) -> bool:
        """A percentage the evidence never contained.

        **Why this is separate from `_fidelity`.** The registered fidelity metric
        extracts numbers matching `\d+\.\d{2,}` -- two or more decimals -- so a
        probability rendered as "54.6%" is invisible to it: one decimal place,
        nothing extracted, fidelity `None`. That threshold is deliberate in the
        metric, which is registered in `EXPLANATION_EVALUATION_PROTOCOL.md` §3.1
        and is **not changed here**; redefining a registered statistic to make a
        gate work is the failure this programme's apparatus exists to prevent.

        A gate may be stricter than the metric it sits beside. No field of
        `ExplanationContext` is a percentage and the template never emits one, so
        a `%` in generated prose is always a unit conversion the evidence does
        not license -- and converting `0.545613` into `54.6%` changes a reported
        value, which is precisely what this layer must not do.
        """
        return bool(re.search(r"\d\s*%", text))

    def __init__(
        self,
        provider: ExplanationProvider | None = None,
        *,
        renderer: TemplateRenderer | None = None,
    ) -> None:
        self._provider = provider
        self._renderer = renderer or TemplateRenderer()

    def explain(self, graph: EvidenceGraph) -> Explanation:
        context = build_context(graph)
        payload = context.as_dict()

        if self._provider is None:
            return self._fallback(context, payload, "no provider configured")

        model_name = getattr(self._provider, "model_name", None)
        started = time.perf_counter()
        try:
            import json

            generated = self._provider.generate(
                SYSTEM_BRIEF, json.dumps(payload, indent=2, default=str)
            )
        except Exception as error:  # noqa: BLE001 - any provider failure degrades
            return self._fallback(
                context,
                payload,
                f"provider {self._provider.name!r} failed: "
                f"{type(error).__name__}",
                model=model_name,
            )
        elapsed = time.perf_counter() - started

        if not generated or not generated.strip():
            return self._fallback(
                context,
                payload,
                f"provider {self._provider.name!r} returned nothing",
                model=model_name,
            )

        # `audit`, not `find_violations`: the brief REQUIRES the canonical
        # disclaimer, so raw matching would reject a model for complying.
        violations = claims.audit(generated)
        if violations:
            # The interesting case: the model spoke, and what it said was not
            # allowed. Degrade to the auditable path and record exactly why.
            return self._fallback(
                context,
                payload,
                f"generated text broke the claim boundary "
                f"({len(violations)} violation(s))",
                violations=tuple(str(violation) for violation in violations),
                model=model_name,
            )

        # The second gate. `None` -- prose stating no numbers at all -- does not
        # fail: avoiding numbers is a completeness concern, which the evaluation
        # protocol measures separately, not a fabrication.
        fidelity = self._fidelity(generated, context)
        if fidelity is not None and fidelity < 1.0:
            return self._fallback(
                context,
                payload,
                "generated text stated a number not present in the evidence "
                f"(fidelity {fidelity:.3f})",
                model=model_name,
            )
        if self._states_a_percentage(generated):
            return self._fallback(
                context,
                payload,
                "generated text converted a value to a percentage, which the "
                "evidence does not contain",
                model=model_name,
            )

        return Explanation(
            text=generated.strip(),
            explanation_mode=GENERATIVE,
            provider=self._provider.name,
            context=payload,
            model=model_name,
            latency_seconds=elapsed,
        )

    def _fallback(
        self,
        context: ExplanationContext,
        payload: dict[str, Any],
        reason: str,
        *,
        violations: tuple[str, ...] = (),
        model: str | None = None,
    ) -> Explanation:
        # The template output is guarded too. If the deterministic renderer
        # ever breaks the boundary that is a defect in this repository, not a
        # model's fault, and it should fail loudly.
        started = time.perf_counter()
        text = claims.enforce(self._renderer.render(context))
        return Explanation(
            text=text,
            explanation_mode=DETERMINISTIC,
            provider=self._renderer.name,
            fallback_reason=reason,
            claim_violations=violations,
            context=payload,
            model=model,
            latency_seconds=time.perf_counter() - started,
        )
