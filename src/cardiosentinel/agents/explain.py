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
from .alignment import categorical_violations
from .context import ExplanationContext, build_context
from .graph import EvidenceGraph
from .providers import ProviderIdentity

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
    renderer: str | None = None
    fallback_reason: str | None = None
    claim_violations: tuple[str, ...] = ()
    context: dict[str, Any] = field(default_factory=dict)
    model_id: str | None = None
    revision: str | None = None
    quantization: str | None = None
    runtime: str | None = None
    device: str | None = None
    #: Total wall clock from explanation request to returned response. A
    #: provider failure therefore includes both the failed attempt and fallback.
    latency_seconds: float | None = None
    latency_scope: str = "total response latency"

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


#: A numeric claim: a number, optionally carrying a unit that changes what it
#: asserts. Percent is the unit that matters here -- restating a probability as
#: a percentage asserts something the evidence never said.
_NUMERIC_CLAIM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(%|\s?percent\b)?", re.I)


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
    def _supported_numbers(context: ExplanationContext) -> set[str]:
        """Every numeric token the evidence licenses, in any sane rendering.

        Built from **all four sections**: a duration, a window count and a policy
        identifier are as much a part of what the model was given as a
        probability is.

        Digit runs inside strings are included, so the timestamp `"00:17:05"`
        licenses `00`, `17` and `05`. Without that the guard would reject the
        deterministic renderer's own output, which states when an event opened.
        """
        supported: set[str] = set()

        def add_number(value: float) -> None:
            for places in range(0, 7):
                supported.add(f"{float(value):.{places}f}")
            supported.add(str(value))
            if float(value).is_integer():
                supported.add(str(int(value)))

        def walk(node: Any) -> None:
            if isinstance(node, bool) or node is None:
                return
            if isinstance(node, (int, float)):
                add_number(node)
            elif isinstance(node, str):
                for run in re.findall(r"\d+(?:\.\d+)?", node):
                    supported.add(run)
                    add_number(float(run))
            elif isinstance(node, dict):
                for item in node.values():
                    walk(item)
            elif isinstance(node, (list, tuple, set)):
                for item in node:
                    walk(item)

        walk(context.as_dict())
        return supported

    @classmethod
    def _unsupported_numeric_claims(
        cls, text: str, context: ExplanationContext
    ) -> tuple[str, ...]:
        """Numeric claims the evidence does not contain.

        **A governance guard, not the registered metric.** They answer different
        questions and are deliberately kept apart:

        - `evidence_fidelity` asks *what fraction of extractable values are
          supported*, and ignores anything with fewer than two decimals because
          window counts and clock parts are formatting noise **for that
          statistic**. It is registered in
          `EXPLANATION_EVALUATION_PROTOCOL.md` §3.1 and is **not changed here**.
          Redefining a registered statistic so a gate works is the failure this
          apparatus exists to prevent.
        - This asks *does the text assert a number the evidence never gave it*,
          so it extracts integers and one-decimal values too -- which is exactly
          where `54.6%` and `54% improvement` live, and where the metric, by
          design, does not look.

        **A unit changes the claim.** `0.545613` is in the evidence; `54.6%` is
        not, and neither is `54%`. Any number carrying a percent sign is refused
        unless the evidence literally contains that percentage, which no field of
        `ExplanationContext` does.
        """
        supported = cls._supported_numbers(context)
        unsupported: list[str] = []
        for number, unit in _NUMERIC_CLAIM.findall(text):
            if unit:
                unsupported.append(f"{number}{unit.strip()}")
            elif number not in supported:
                unsupported.append(number)
        return tuple(dict.fromkeys(unsupported))

    def __init__(
        self,
        provider: ExplanationProvider | None = None,
        *,
        renderer: TemplateRenderer | None = None,
    ) -> None:
        self._provider = provider
        self._renderer = renderer or TemplateRenderer()

    @staticmethod
    def _identity(provider: ExplanationProvider) -> ProviderIdentity | None:
        identity = getattr(provider, "identity", None)
        return identity if isinstance(identity, ProviderIdentity) else None

    def explain(self, graph: EvidenceGraph) -> Explanation:
        started = time.perf_counter()
        context = build_context(graph)
        payload = context.as_dict()

        if self._provider is None:
            return self._fallback(
                context,
                payload,
                "no provider configured",
                started_at=started,
            )

        identity = self._identity(self._provider)
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
                identity=identity,
                started_at=started,
            )

        if not generated or not generated.strip():
            return self._fallback(
                context,
                payload,
                f"provider {self._provider.name!r} returned nothing",
                identity=identity,
                started_at=started,
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
                identity=identity,
                started_at=started,
            )

        # The second gate. `None` -- prose stating no numbers at all -- does not
        # fail: avoiding numbers is a completeness concern, which the evaluation
        # protocol measures separately, not a fabrication.
        unsupported = self._unsupported_numeric_claims(generated, context)
        if unsupported:
            listed = ", ".join(repr(item) for item in unsupported[:4])
            return self._fallback(
                context,
                payload,
                f"generated text stated {len(unsupported)} numeric claim(s) the "
                f"evidence does not contain: {listed}",
                identity=identity,
                started_at=started,
            )

        # The third gate, registered in protocol §4.4 after Arm B produced a
        # fluent, claim-compliant, numerically-faithful explanation asserting
        # "the system passed ... G1 through G6" while G4 and G5 were blocked.
        # Numeric and lexical guards enforce numeric and lexical properties;
        # neither compares a categorical assertion against the field recording
        # the truth.
        misaligned = categorical_violations(generated, context)
        if misaligned:
            listed = "; ".join(item.detail for item in misaligned[:3])
            return self._fallback(
                context,
                payload,
                f"generated text contradicts the recorded state in "
                f"{len(misaligned)} place(s): {listed}",
                identity=identity,
                started_at=started,
                violations=tuple(str(item) for item in misaligned),
            )

        return Explanation(
            text=generated.strip(),
            explanation_mode=GENERATIVE,
            provider=identity.provider if identity else self._provider.name,
            context=payload,
            model_id=identity.model_id if identity else None,
            revision=identity.revision if identity else None,
            quantization=identity.quantization if identity else None,
            runtime=identity.runtime if identity else None,
            device=identity.device if identity else None,
            latency_seconds=time.perf_counter() - started,
        )

    def _fallback(
        self,
        context: ExplanationContext,
        payload: dict[str, Any],
        reason: str,
        *,
        violations: tuple[str, ...] = (),
        identity: ProviderIdentity | None = None,
        started_at: float,
    ) -> Explanation:
        # The template output is guarded too. If the deterministic renderer
        # ever breaks the boundary that is a defect in this repository, not a
        # model's fault, and it should fail loudly.
        text = claims.enforce(self._renderer.render(context))
        return Explanation(
            text=text,
            explanation_mode=DETERMINISTIC,
            provider=identity.provider if identity else self._renderer.name,
            renderer=self._renderer.name,
            fallback_reason=reason,
            claim_violations=violations,
            context=payload,
            model_id=identity.model_id if identity else None,
            revision=identity.revision if identity else None,
            quantization=identity.quantization if identity else None,
            runtime=identity.runtime if identity else None,
            device=identity.device if identity else None,
            latency_seconds=time.perf_counter() - started_at,
        )
