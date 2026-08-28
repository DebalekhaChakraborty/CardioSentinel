"""The IPS demonstration console: the presentation layer, and nothing else.

**No new intelligence, no new data path, no new dependency.** It composes the
runtime, the evidence graph and the three agents that already exist, and renders
them for a terminal. Every number it prints was produced by a component that
was already tested; this module only arranges them.

Terminal rather than browser, deliberately. The scientific environment is frozen
at 335 packages with a recorded digest, and adding a web framework to it would
invite the one question the whole reproducibility argument exists to close:
*did the UI dependency change the environment the science ran in?* It did not,
because there is no UI dependency.

What it renders is contracted by `docs/explanation/DEMO_SCENARIO.md` and checked by
`tests/edge/test_demo_scenario.py`.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..agents.architecture import ArchitectureSelectionAgent
from ..agents.evidence import EvidenceAgent
from ..agents.explain import PatientExplanationAgent
from ..agents.graph import build_evidence_graph, summarise_lineage
from .artifacts import DEFAULT_FEATURE_ROOT, DEFAULT_RUN_ROOT, DEFAULT_SOURCE_ROOT

STATE_MARK = {"NORMAL": ".", "WATCH": "w", "EVENT": "E", "RECOVERY": "r"}

#: Stated on every run. Omitting any of these would overclaim by omission.
LIMITATIONS = (
    "Simulation only: a stored recording is replayed. No sensor, no acquisition.",
    "Not a diagnosis. Detection only; no clinical utility is claimed.",
    "Not deployment validation. No serving path, and a laptop is not edge hardware.",
    "Not generalisation. One dataset, twelve validation subjects.",
    "The sealed neural test was consumed once, on twelve subjects, and no "
    "cohort exists to corroborate it.",
)


def _rule(title: str = "", width: int | None = None) -> str:
    width = width or min(shutil.get_terminal_size((78, 24)).columns, 78)
    if not title:
        return "=" * width
    return f"[ {title} ]".ljust(width, " ")


def _clock(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"


@dataclass
class ConsoleReport:
    """Everything the console rendered, so a test can check it."""

    record_id: str
    subject_id: str
    windows: int
    alerts: int
    simulated_seconds: float
    wall_seconds: float
    memory_updates_admitted: int
    provenance: dict[str, Any]
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def render(
    record_id: str,
    *,
    channel_index: int = 0,
    seconds: float = 2400.0,
    source_root: Path | str = DEFAULT_SOURCE_ROOT,
    run_root: Path | str = DEFAULT_RUN_ROOT,
    feature_root: Path | str = DEFAULT_FEATURE_ROOT,
    architecture_question: str = "Why was S4D selected?",
) -> ConsoleReport:
    """Run the scenario and render it. Composition only."""
    from .replay import replay_record

    result = replay_record(
        record_id,
        channel_index=channel_index,
        max_seconds=seconds,
        source_root=source_root,
        run_root=run_root,
        feature_root=feature_root,
    )
    provenance = result.provenance
    lines: list[str] = []
    add = lines.append

    add(_rule())
    add("CardioSentinel IPS Runtime Console")
    add(f"Subject: {provenance.get('subject_id')}   Record: {record_id}   "
        f"Mode: REPLAY SIMULATION")
    add(_rule())
    add("")

    # -- stream ------------------------------------------------------------
    add(_rule("ECG STREAM"))
    marks = "".join(STATE_MARK.get(o.state, "?") for o in result.observations)
    for offset in range(0, len(marks), 72):
        add(f"  {marks[offset:offset + 72]}")
    add("")
    add(f"  windows {len(result.observations)}   window 10 s / stride 5 s   "
        f"{result.simulated_seconds / 60:.0f} min of ECG in "
        f"{result.wall_seconds:.0f} s wall ({result.real_time_factor:.0f}x)")
    add("  legend  . NORMAL   w WATCH   E EVENT   r RECOVERY")
    add("")

    admitted = sum(o.memory_update_admitted for o in result.observations)
    evidence_agent = EvidenceAgent(provenance)

    if not result.alerts:
        add(_rule("DECISION"))
        add("  No EVENT run in this window. Nothing to explain.")
        add("")
    for index, alert in enumerate(result.alerts):
        record = evidence_agent.explain(alert, result.observations, index=index)
        graph = build_evidence_graph(record, run_root=run_root)

        add(_rule("DECISION"))
        add(f"  Alert                {record.alert_id}")
        add(f"  Window               {record.opened_at} -> "
            f"{record.closed_at or '(still open)'}")
        span = (
            f"{record.duration_seconds:.0f} s"
            if record.duration_seconds is not None
            else "open"
        )
        add(f"  Asserted for         {span} across {record.window_count} windows")
        for label, value in (
            ("Probability p_t", record.peak_calibrated_probability),
            ("Temporal evidence", record.peak_temporal_evidence),
            ("Memory deviation", record.max_memory_deviation),
        ):
            rendered = "undefined" if value is None else f"{value:.6f}"
            add(f"  {label:20s} {rendered}")
        add("")

        add(_rule("SAFETY GATES"))
        add("  " + "   ".join(f"{g.condition} {g.status}" for g in record.gate))
        blocked = [g.condition for g in record.gate if g.passed is False]
        if blocked:
            add(f"  {', '.join(blocked)} blocked the baseline update. "
                "That is the contamination control working, not a fault.")
        add("")

        add(_rule("EVIDENCE"))
        add(f"  {record.alert_id}")
        for line in summarise_lineage(graph, "measurement:p_t"):
            add(f"    +-- {line}")
        add("")

        add(_rule("EXPLANATION"))
        explanation = PatientExplanationAgent(None).explain(graph)
        add(f"  mode={explanation.explanation_mode}  "
            f"provider={explanation.provider}")
        if explanation.fallback_reason:
            add(f"  fell back: {explanation.fallback_reason}")
        add("")
        import textwrap

        for line in textwrap.wrap(explanation.text, 74):
            add(f"  {line}")
        add("")

    # -- research panel ----------------------------------------------------
    add(_rule("RESEARCH LINEAGE"))
    add(f"  Q: {architecture_question}")
    add("")
    for line in ArchitectureSelectionAgent().explain(architecture_question).split("\n"):
        add(f"  {line}")
    add("")

    # -- boundary ----------------------------------------------------------
    add(_rule("LIMITATIONS"))
    for item in LIMITATIONS:
        add(f"  - {item}")
    add("")
    add(_rule())

    return ConsoleReport(
        record_id=record_id,
        subject_id=str(provenance.get("subject_id")),
        windows=len(result.observations),
        alerts=len(result.alerts),
        simulated_seconds=result.simulated_seconds,
        wall_seconds=result.wall_seconds,
        memory_updates_admitted=admitted,
        provenance=provenance,
        lines=lines,
    )
