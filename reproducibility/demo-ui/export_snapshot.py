"""Export one snapshot of the contracted CardioSentinel replay for the demo UI.

**This script adds no inference, training, selection or scientific logic.** It
calls the existing runtime -- `replay_record` -- and serialises what that
runtime already produced, plus a display-decimated copy of the source ECG for
visualisation only.

Every scientific value written here is read from an `EdgeObservation`, an
`AlertEvent`, an `EvidenceRecord` or the existing agent output. Nothing is
recomputed, rounded into a decision, or derived.

Before writing, the generated replay is checked against the contracted demo
scenario. **A mismatch aborts and writes nothing** -- a presentation layer that
silently renders different numbers than the runtime asserted is worse than no
presentation layer.

Usage, from the repository root, on the frozen scientific interpreter:

    python reproducibility/demo-ui/export_snapshot.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from cardiosentinel.agents.evidence import EvidenceAgent  # noqa: E402
from cardiosentinel.agents.explain import PatientExplanationAgent  # noqa: E402
from cardiosentinel.agents.graph import (  # noqa: E402
    build_evidence_graph,
    summarise_lineage,
)
from cardiosentinel.agents.providers import (  # noqa: E402
    LocalQwenProvider,
    ProviderUnavailable,
)
from cardiosentinel.edge.console import LIMITATIONS  # noqa: E402
from cardiosentinel.edge.replay import (  # noqa: E402
    SAMPLING_FREQUENCY_HZ,
    STRIDE_SECONDS,
    WINDOW_SECONDS,
    replay_record,
    subject_for_record,
)
from cardiosentinel.signal.io import read_local_segment  # noqa: E402

# --------------------------------------------------------------------------
# The canonical demonstration. These are the existing contracted arguments;
# they are not tunable knobs.
# --------------------------------------------------------------------------
RECORD_ID = "s20201"
CHANNEL_INDEX = 0
SIMULATED_SECONDS = 2400.0
SOURCE_ROOT = REPOSITORY_ROOT / "cardiosentinel-data/ltstdb/1.0.0"
RUN_ROOT = REPOSITORY_ROOT / "reproducibility/demo_bundle/runs"
FEATURE_ROOT = REPOSITORY_ROOT / "reproducibility/demo_bundle/features"
OUTPUT = Path(__file__).resolve().parent / "demo_snapshot.json"

#: Fixed-stride decimation only. 250 Hz / 10 = 25 Hz. No filter, no resampling
#: kernel, no interpolation -- every displayed sample is a source sample.
DISPLAY_DECIMATION = 10
DISPLAY_SAMPLING_FREQUENCY_HZ = SAMPLING_FREQUENCY_HZ / DISPLAY_DECIMATION
#: Display rounding, declared rather than silent. Visualisation only.
DISPLAY_DECIMALS = 4

#: The contracted demo scenario. A mismatch is a stop condition.
TOLERANCE = 1e-6
CONTRACT: dict[str, Any] = {
    "record_id": RECORD_ID,
    "subject_id": "ltstdb:s2020",
    "channel_index": 0,
    "observations": 479,
    "alerts": 1,
    "alert_id": "EVT-s20201-0000",
    "opened_at": "00:17:05",
    "closed_at": "00:27:45",
    "duration_seconds": 640.0,
    "window_count": 129,
    "peak_calibrated_probability": 0.545613,
    "peak_temporal_evidence": 0.953344,
    "max_memory_deviation": 1.411607,
    "opening_gate": {
        "G1": "PASS",
        "G2": "PASS",
        "G3": "PASS",
        "G4": "BLOCK",
        "G5": "BLOCK",
        "G6": "PASS",
    },
    "memory_updates_admitted": 0,
}

#: The two locally cached open-weight models, pinned to the immutable revisions
#: the explanation-evaluation record fixes. Nothing is downloaded: a missing or
#: incomplete cache raises `ProviderUnavailable` and is recorded as unavailable.
LOCAL_MODELS = (
    ("Qwen/Qwen3-1.7B", "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"),
    ("Qwen/Qwen3-4B-Instruct-2507", "cdbee75f17c01a7cc42f958dc650907174af0554"),
)
LOCAL_MAX_NEW_TOKENS = 400

GATE_KEYS = (
    ("g1_available", "G1"),
    ("g2_finite_representation", "G2"),
    ("g3_sqi_admissible", "G3"),
    ("g4_normal_evidence", "G4"),
    ("g5_not_in_refractory", "G5"),
    ("g6_morphology_computable", "G6"),
)


class ContractMismatch(RuntimeError):
    """The replay did not reproduce the contracted demonstration."""


def _clock(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"


def _gate_status(value: bool | None) -> str:
    """Tri-state, preserved. An unavailable gate is never rendered as BLOCK."""
    if value is None:
        return "N/A"
    return "PASS" if value else "BLOCK"


def _observation_row(observation: Any) -> dict[str, Any]:
    """Factual fields only, straight off the EdgeObservation."""
    gate = observation.gate or {}
    return {
        "stable_id": observation.stable_id,
        "elapsed_stream_seconds": observation.elapsed_stream_seconds,
        "clock": _clock(observation.elapsed_stream_seconds),
        "state_before": observation.state_before,
        "state": observation.state,
        "detector_score": observation.detector_score,
        "detector_decision": observation.detector_decision,
        "calibrated_probability": observation.calibrated_probability,
        "decision_error_uncertainty": observation.decision_error_uncertainty,
        "temporal_evidence": observation.temporal_evidence,
        "memory_deviation": observation.memory_deviation,
        "memory_update_admitted": bool(observation.memory_update_admitted),
        "contains_filter_warmup": bool(observation.contains_filter_warmup),
        "gate": {
            label: _gate_status(gate.get(key)) for key, label in GATE_KEYS
        },
    }


def _display_waveform(readable_seconds: float) -> dict[str, Any]:
    """Fixed-stride decimation of the real channel-0 signal, for display only.

    Bounded by the last window the runtime actually consumed, so no sample is
    read that the replay did not already read.
    """
    total = int(round(readable_seconds * SAMPLING_FREQUENCY_HZ))
    values: list[float] = []
    chunk = int(SAMPLING_FREQUENCY_HZ * 60)
    start = 0
    while start < total:
        end = min(start + chunk, total)
        segment = read_local_segment(
            SOURCE_ROOT, "ltstdb", RECORD_ID, start, end, (CHANNEL_INDEX,)
        )
        column = segment.values[:, 0]
        for index in range(0, column.shape[0], DISPLAY_DECIMATION):
            values.append(round(float(column[index]), DISPLAY_DECIMALS))
        start = end
    return {
        "record_id": RECORD_ID,
        "channel_index": CHANNEL_INDEX,
        "source_sampling_frequency_hz": SAMPLING_FREQUENCY_HZ,
        "display_sampling_frequency_hz": DISPLAY_SAMPLING_FREQUENCY_HZ,
        "display_decimation_factor": DISPLAY_DECIMATION,
        "display_value_decimals": DISPLAY_DECIMALS,
        "display_waveform_is_inference_input": False,
        "display_waveform_purpose": "visualization_only",
        "display_method": "fixed-stride decimation, no filter, no interpolation",
        "physical_units": "mV",
        "samples": len(values),
        "values": values,
    }


def _explanation_row(explanation: Any, *, label: str, identity: Any) -> dict[str, Any]:
    """Whatever the agent actually returned, recorded verbatim.

    `explanation_mode` is the runtime's own verdict. A generation that the guard
    refused arrives here as DETERMINISTIC with the refusal in `fallback_reason`,
    and that is exactly what is stored -- the refusal is the result, not an
    error to be smoothed away.
    """
    return {
        "label": label,
        "identity": identity,
        "text": explanation.text,
        "explanation_mode": explanation.explanation_mode,
        "provider": explanation.provider,
        "fallback_reason": explanation.fallback_reason,
        "context_source": explanation.context_source,
        "claim_violations": list(getattr(explanation, "claim_violations", ()) or ()),
        "served": explanation.explanation_mode == "GENERATIVE",
    }


def _local_model_explanations(graph: Any) -> list[dict[str, Any]]:
    """Run each pinned local model through the same agent the runtime uses."""
    rows: list[dict[str, Any]] = []
    for model_id, revision in LOCAL_MODELS:
        print(f"    {model_id} @ {revision[:8]} ... ", end="", flush=True)
        try:
            provider = LocalQwenProvider(
                model_id, revision=revision, max_new_tokens=LOCAL_MAX_NEW_TOKENS
            )
        except ProviderUnavailable as error:
            print("unavailable")
            rows.append(
                {
                    "label": model_id,
                    "identity": {"model_id": model_id, "revision": revision},
                    "text": None,
                    "explanation_mode": None,
                    "provider": None,
                    "fallback_reason": None,
                    "context_source": None,
                    "claim_violations": [],
                    "served": None,
                    "unavailable_reason": str(error),
                }
            )
            continue
        started = time.perf_counter()
        explanation = PatientExplanationAgent(provider).explain(graph)
        elapsed = time.perf_counter() - started
        row = _explanation_row(
            explanation, label=model_id, identity=provider.identity.as_dict()
        )
        row["latency_seconds"] = round(elapsed, 3)
        rows.append(row)
        reason = explanation.fallback_reason
        print(
            f"{explanation.explanation_mode}"
            + (f"  ({reason})" if reason else "")
            + f"  [{elapsed:.1f} s]"
        )
    return rows


def _check(report: list[str], name: str, observed: Any, expected: Any) -> bool:
    if isinstance(expected, float) and isinstance(observed, (int, float)):
        ok = observed is not None and abs(float(observed) - expected) <= TOLERANCE
    else:
        ok = observed == expected
    report.append(
        f"  {'ok ' if ok else 'MISMATCH'}  {name:34s} "
        f"observed={observed!r} expected={expected!r}"
    )
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-local-models",
        action="store_true",
        help=(
            "also run each pinned, locally cached open-weight model through the "
            "same PatientExplanationAgent the runtime uses, and record what the "
            "guard did with each generation. Downloads nothing."
        ),
    )
    parser.add_argument(
        "--hf-cache",
        default=None,
        help="Hugging Face hub cache directory (sets HF_HUB_CACHE for this run).",
    )
    args = parser.parse_args()
    if args.hf_cache:
        os.environ["HF_HUB_CACHE"] = args.hf_cache
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

    print("CardioSentinel demo snapshot exporter")
    print(f"  repository root : {REPOSITORY_ROOT}")
    print(f"  record          : {RECORD_ID} channel {CHANNEL_INDEX}")
    print(f"  simulated       : {SIMULATED_SECONDS:.0f} s")
    print("  running the existing replay runtime ...")

    result = replay_record(
        RECORD_ID,
        channel_index=CHANNEL_INDEX,
        max_seconds=SIMULATED_SECONDS,
        source_root=SOURCE_ROOT,
        run_root=RUN_ROOT,
        feature_root=FEATURE_ROOT,
    )

    subject_id = subject_for_record(RECORD_ID)
    admitted = sum(o.memory_update_admitted for o in result.observations)
    evidence_agent = EvidenceAgent(result.provenance)

    alerts: list[dict[str, Any]] = []
    for index, alert in enumerate(result.alerts):
        record = evidence_agent.explain(alert, result.observations, index=index)
        graph = build_evidence_graph(record, run_root=RUN_ROOT)
        explanation = PatientExplanationAgent(None).explain(graph)
        local_rows: list[dict[str, Any]] = []
        if args.with_local_models:
            print(f"  guarded generation for {record.alert_id}:")
            local_rows = _local_model_explanations(graph)
        alerts.append(
            {
                "alert_id": record.alert_id,
                "opened_at": record.opened_at,
                "closed_at": record.closed_at,
                "opened_at_seconds": alert.opened_at_seconds,
                "closed_at_seconds": alert.closed_at_seconds,
                "duration_seconds": record.duration_seconds,
                "window_count": record.window_count,
                "peak_calibrated_probability": record.peak_calibrated_probability,
                "peak_temporal_evidence": record.peak_temporal_evidence,
                "max_memory_deviation": record.max_memory_deviation,
                "entered_from": alert.entered_from,
                "closed_into": alert.closed_into,
                "open": alert.open,
                "opening_gate": [
                    {
                        "condition": finding.condition,
                        "status": finding.status,
                        "meaning": finding.meaning,
                    }
                    for finding in record.gate
                ],
                "evidence_record": record.as_dict(),
                "lineage": list(summarise_lineage(graph, "measurement:p_t")),
                "explanation": {
                    "text": explanation.text,
                    "explanation_mode": explanation.explanation_mode,
                    "provider": explanation.provider,
                    "fallback_reason": explanation.fallback_reason,
                    "context_source": explanation.context_source,
                },
                "local_model_explanations": local_rows,
            }
        )

    # ---------------------------------------------------------------- contract
    report: list[str] = []
    ok = True
    ok &= _check(report, "record_id", RECORD_ID, CONTRACT["record_id"])
    ok &= _check(report, "subject_id", subject_id, CONTRACT["subject_id"])
    ok &= _check(report, "channel_index", CHANNEL_INDEX, CONTRACT["channel_index"])
    ok &= _check(
        report, "observations", len(result.observations), CONTRACT["observations"]
    )
    ok &= _check(report, "alerts", len(result.alerts), CONTRACT["alerts"])
    ok &= _check(
        report, "memory_updates_admitted", admitted, CONTRACT["memory_updates_admitted"]
    )
    if alerts:
        first = alerts[0]
        ok &= _check(report, "alert_id", first["alert_id"], CONTRACT["alert_id"])
        ok &= _check(report, "opened_at", first["opened_at"], CONTRACT["opened_at"])
        ok &= _check(report, "closed_at", first["closed_at"], CONTRACT["closed_at"])
        ok &= _check(
            report,
            "duration_seconds",
            first["duration_seconds"],
            CONTRACT["duration_seconds"],
        )
        ok &= _check(
            report, "window_count", first["window_count"], CONTRACT["window_count"]
        )
        ok &= _check(
            report,
            "peak_calibrated_probability",
            first["peak_calibrated_probability"],
            CONTRACT["peak_calibrated_probability"],
        )
        ok &= _check(
            report,
            "peak_temporal_evidence",
            first["peak_temporal_evidence"],
            CONTRACT["peak_temporal_evidence"],
        )
        ok &= _check(
            report,
            "max_memory_deviation",
            first["max_memory_deviation"],
            CONTRACT["max_memory_deviation"],
        )
        observed_gate = {
            item["condition"]: item["status"] for item in first["opening_gate"]
        }
        ok &= _check(report, "opening_gate", observed_gate, CONTRACT["opening_gate"])

    print("\ncontract check against the recorded demo scenario:")
    for line in report:
        print(line)

    if not ok:
        print(
            "\nCONTRACT MISMATCH. demo_snapshot.json was NOT written.\n"
            "The replay did not reproduce the contracted demonstration. This is a\n"
            "stop condition: the snapshot is not silently corrected, and the\n"
            "difference is investigated against the frozen record before any\n"
            "presentation layer renders it."
        )
        return 1

    # ---------------------------------------------------------------- waveform
    print("\n  reading the source waveform for display decimation ...")
    readable_seconds = (
        result.observations[-1].elapsed_stream_seconds if result.observations else 0.0
    )
    waveform = _display_waveform(readable_seconds)

    snapshot = {
        "meta": {
            "system": "CardioSentinel",
            "mode": "REPLAY SIMULATION",
            "record_id": RECORD_ID,
            "subject_id": subject_id,
            "channel": CHANNEL_INDEX,
            "simulated_seconds": SIMULATED_SECONDS,
            "window_seconds": WINDOW_SECONDS,
            "stride_seconds": STRIDE_SECONDS,
            "windows": len(result.observations),
            "wall_seconds": result.wall_seconds,
            "real_time_factor": result.real_time_factor,
            "wall_time_scope": "Snapshot generation on this host",
            "research_demonstrator": True,
            "diagnostic_system": False,
            "edge_hardware_validation": False,
            "memory_updates_admitted": admitted,
            "local_models_exercised": bool(args.with_local_models),
        },
        "waveform": waveform,
        "observations": [_observation_row(o) for o in result.observations],
        "alerts": alerts,
        "limitations": list(LIMITATIONS),
    }

    OUTPUT.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")

    explanation_mode = alerts[0]["explanation"]["explanation_mode"] if alerts else "n/a"
    provider = alerts[0]["explanation"]["provider"] if alerts else "n/a"
    print(f"\nwrote {OUTPUT.relative_to(REPOSITORY_ROOT)}"
          f"  ({OUTPUT.stat().st_size / 1024:.0f} KiB)")
    print("\nverification report")
    print(f"  record                     {RECORD_ID}")
    print(f"  subject                    {subject_id}")
    print(f"  observations               {len(result.observations)}")
    print(f"  alerts                     {len(result.alerts)}")
    if alerts:
        print(f"  event window               {alerts[0]['opened_at']} -> "
              f"{alerts[0]['closed_at']}  "
              f"({alerts[0]['duration_seconds']:.0f} s, "
              f"{alerts[0]['window_count']} windows)")
        print("  opening gate               " + "  ".join(
            f"{item['condition']} {item['status']}"
            for item in alerts[0]["opening_gate"]
        ))
    print(f"  memory updates admitted    {admitted}")
    print(f"  waveform source            {RECORD_ID} channel {CHANNEL_INDEX}, "
          f"{SAMPLING_FREQUENCY_HZ:.0f} Hz")
    print(f"  waveform display rate      {DISPLAY_SAMPLING_FREQUENCY_HZ:.0f} Hz "
          f"({waveform['samples']} samples, visualization only)")
    print(f"  explanation mode           {explanation_mode}")
    print(f"  explanation provider       {provider}")
    print(f"  replay execution           {result.wall_seconds:.1f} s wall, "
          f"{result.real_time_factor:.0f}x  (this host only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
