"""The Evidence Agent: why did CardioSentinel raise this alert?

**No language model.** Every field is read from an `AlertEvent`, the
`EdgeObservation`s it spans, and the frozen provenance the session carried. The
agent assembles and renders; it does not infer, summarise or judge. That is
deliberate: this is the layer a later LLM explanation agent will be *grounded
on*, so it has to be the part that cannot hallucinate.

Its output passes through `claims.enforce` before it is returned. An
explanation that cannot be phrased inside the publication claim boundary fails
loudly rather than quietly publishing the claim.

**On confidence.** This agent reports `decision_error_uncertainty` verbatim and
emits **no calibrated confidence band**. U1's selective router is the component
that would have supplied one, and it was evaluated and **rejected**
(`Retained: false`, RQ3 answered negatively). Inventing a three-level band with
chosen cut points would be an unregistered statistic dressed as a system
capability -- exactly the move this programme's discipline exists to prevent.
Saying so is more useful to a reviewer than a reassuring word.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..edge.alerts import AlertEvent
from ..edge.session import EdgeObservation
from . import claims

#: The six admission conditions, in the order the gate evaluates them.
GATE_CONDITIONS: tuple[tuple[str, str, str], ...] = (
    ("G1", "g1_available", "the window is a physical observation"),
    ("G2", "g2_finite_representation", "the 146-d representation is finite"),
    ("G3", "g3_sqi_admissible", "signal quality is within its frozen bounds"),
    ("G4", "g4_normal_evidence", "the window looks normal enough to learn from"),
    ("G5", "g5_not_in_refractory", "no memory-update refractory is active"),
    ("G6", "g6_morphology_computable", "morphology was computable"),
)


@dataclass(frozen=True)
class GateExplanation:
    condition: str
    passed: bool | None
    meaning: str

    @property
    def status(self) -> str:
        if self.passed is None:
            return "N/A"
        return "PASS" if self.passed else "BLOCK"


@dataclass(frozen=True)
class EvidenceRecord:
    """One alert, and everything the repository knows about why it happened."""

    alert_id: str
    record_id: str
    subject_id: str
    channel_index: int
    decision: str
    entered_from: str
    closed_into: str | None
    still_open: bool
    opened_at: str
    closed_at: str | None
    duration_seconds: float | None
    window_count: int
    peak_calibrated_probability: float | None
    peak_temporal_evidence: float | None
    max_memory_deviation: float | None
    decision_error_uncertainty: float | None
    detector_threshold: float | None
    gate: tuple[GateExplanation, ...]
    memory_windows_observed: int | None
    memory_updates_admitted: int | None
    provenance: dict[str, Any] = field(default_factory=dict)
    cannot_support: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


#: What an alert never establishes, whatever its numbers look like.
#:
#: These are `claims.APPROVED_DISCLAIMERS`: curated constant text that names a
#: forbidden claim precisely in order to deny it. They are exempt from the
#: lexical guard because a regex cannot tell "does not support a diagnosis"
#: from "supports a diagnosis", and they are constants a human reviewed rather
#: than prose an agent generated.
CANNOT_SUPPORT: tuple[str, ...] = claims.APPROVED_DISCLAIMERS


def _alert_id(alert: AlertEvent, index: int) -> str:
    return f"EVT-{alert.record_id}-{index:04d}"


class EvidenceAgent:
    """Assembles provenance-backed explanations. Deterministic by construction."""

    def __init__(self, provenance: dict[str, Any] | None = None) -> None:
        self._provenance = dict(provenance or {})

    def explain(
        self,
        alert: AlertEvent,
        observations: list[EdgeObservation] | tuple[EdgeObservation, ...] = (),
        *,
        index: int = 0,
    ) -> EvidenceRecord:
        """Build the record for one alert from the windows it spans."""
        provenance = dict(self._provenance) or dict(alert.provenance)
        spanned = [
            observation
            for observation in observations
            if alert.opened_at_seconds
            <= observation.elapsed_stream_seconds
            <= (alert.closed_at_seconds or observation.elapsed_stream_seconds)
        ]
        # The gate record of the window that opened the alert. A later window's
        # gate would describe a different decision.
        opening = spanned[0] if spanned else None
        gate = tuple(
            GateExplanation(
                condition=name,
                passed=(None if opening is None else opening.gate.get(key)),
                meaning=meaning,
            )
            for name, key, meaning in GATE_CONDITIONS
        )
        uncertainties = [
            observation.decision_error_uncertainty
            for observation in spanned
            if observation.decision_error_uncertainty is not None
        ]
        return EvidenceRecord(
            alert_id=_alert_id(alert, index),
            record_id=alert.record_id,
            subject_id=alert.subject_id,
            channel_index=alert.channel_index,
            decision="EVENT",
            entered_from=alert.entered_from,
            closed_into=alert.closed_into,
            still_open=alert.open,
            opened_at=alert.opened_at,
            closed_at=alert.closed_at,
            duration_seconds=alert.duration_seconds,
            window_count=alert.window_count,
            peak_calibrated_probability=alert.peak_calibrated_probability,
            peak_temporal_evidence=alert.peak_temporal_evidence,
            max_memory_deviation=alert.max_memory_deviation,
            decision_error_uncertainty=(
                min(uncertainties) if uncertainties else None
            ),
            detector_threshold=provenance.get("detector_threshold"),
            gate=gate,
            memory_windows_observed=(
                None
                if opening is None
                else opening.gate.get("past_observed_count_before")
            ),
            memory_updates_admitted=(
                None
                if opening is None
                else opening.gate.get("past_update_count_before")
            ),
            provenance=provenance,
            cannot_support=CANNOT_SUPPORT,
        )

    def render(self, record: EvidenceRecord) -> str:
        """Human-readable explanation, checked against the claim boundary."""
        lines: list[str] = []
        add = lines.append

        add(f"Alert ID          {record.alert_id}")
        add(
            f"Decision          {record.decision}  "
            f"(entered from {record.entered_from})"
        )
        window = (
            f"{record.opened_at} -> {record.closed_at or '(still open)'}"
            if not record.still_open
            else f"{record.opened_at} -> still open at end of stream"
        )
        add(f"Window            {window}")
        if record.duration_seconds is not None:
            add(
                f"Asserted for      {record.duration_seconds:.0f} s across "
                f"{record.window_count} windows"
            )
        else:
            add(f"Asserted for      {record.window_count} windows, run not yet closed")
        add(f"Subject / record  {record.subject_id} / {record.record_id} "
            f"channel {record.channel_index}")
        add("")

        add("Measured evidence, read verbatim from the run:")
        for label, value, note in (
            (
                "calibrated probability p_t (peak)",
                record.peak_calibrated_probability,
                "",
            ),
            ("temporal evidence s_t (peak)", record.peak_temporal_evidence,
             "  bounded score, not a probability"),
            ("memory deviation d_long (max)", record.max_memory_deviation, ""),
            (
                "decision error uncertainty u_t (min)",
                record.decision_error_uncertainty,
                "",
            ),
        ):
            rendered = "undefined" if value is None else f"{value:.6f}"
            add(f"  {label:38s} {rendered}{note}")
        if record.detector_threshold is not None:
            add(
                f"  {'detector threshold (frozen upstream)':38s} "
                f"{record.detector_threshold:.6f}"
            )
        add("")

        add("Memory admission gate, for the window that opened the alert:")
        for item in record.gate:
            add(f"  {item.condition}  {item.status:5s}  {item.meaning}")
        if record.memory_windows_observed is not None:
            add(
                "  patient baseline had seen "
                f"{record.memory_windows_observed} windows, "
                f"{record.memory_updates_admitted} admitted"
            )
        add("")

        add("Model provenance:")
        for key in (
            "encoder_architecture",
            "m2_arm",
            "u1_family",
            "t2_arm",
            "t1_policy_id",
            "t1_held_out_subject",
            "physiology_transform_sha256",
            "sealed_test_state",
        ):
            if key in record.provenance:
                add(f"  {key:30s} {record.provenance[key]}")
        add("")

        add("This alert does not establish:")
        for item in record.cannot_support:
            add(f"  - {item}")

        return claims.enforce("\n".join(lines))
