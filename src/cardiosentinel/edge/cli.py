"""`cardiosentinel edge simulate` -- run the laptop edge simulation.

Prints a live state stream and an alert summary, then the frozen provenance of
everything that produced them. The provenance block is not decoration: it is
the thing that lets a reader check that the demo ran the retained pipeline and
not a lookalike.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from .artifacts import DEFAULT_FEATURE_ROOT, DEFAULT_RUN_ROOT, DEFAULT_SOURCE_ROOT

STATE_MARK = {
    "NORMAL": ".",
    "WATCH": "w",
    "EVENT": "E",
    "RECOVERY": "r",
}


def add_edge_commands(subparsers: Any) -> None:  # noqa: ANN401 - argparse action
    parser = subparsers.add_parser("edge", help="Laptop edge simulation.")
    commands = parser.add_subparsers(dest="edge_command", required=True)

    simulate = commands.add_parser(
        "simulate", help="Replay an LTSTDB record as a live ECG stream."
    )
    simulate.add_argument("record", help="LTSTDB record id, e.g. s20041.")
    simulate.add_argument("--channel", type=int, default=0)
    simulate.add_argument(
        "--seconds",
        type=float,
        default=600.0,
        help="Simulated ECG seconds to replay (default 600).",
    )
    simulate.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    simulate.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    simulate.add_argument("--feature-root", default=str(DEFAULT_FEATURE_ROOT))
    simulate.add_argument(
        "--json", action="store_true", help="Emit observations and alerts as JSON."
    )

    console = commands.add_parser(
        "console", help="The IPS demonstration console (terminal, no UI deps)."
    )
    console.add_argument("record")
    console.add_argument("--channel", type=int, default=0)
    console.add_argument("--seconds", type=float, default=2400.0)
    console.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    console.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    console.add_argument("--feature-root", default=str(DEFAULT_FEATURE_ROOT))
    console.add_argument(
        "--ask",
        default="Why was S4D selected?",
        help="Research question for the lineage panel.",
    )

    subjects = commands.add_parser(
        "subjects", help="List the replayable held-out subjects."
    )
    subjects.add_argument("--json", action="store_true")


def run_edge_command(args: argparse.Namespace) -> int:
    if args.edge_command == "subjects":
        return _subjects(args)
    if args.edge_command == "console":
        return _console(args)
    return _simulate(args)


def _subjects(args: argparse.Namespace) -> int:
    from ..neural.t1_protocol import T1_VALIDATION_SUBJECTS

    if args.json:
        print(json.dumps(list(T1_VALIDATION_SUBJECTS), indent=2))
        return 0
    print("Replayable subjects -- each has a leave-one-subject-out T1 policy:")
    for subject in T1_VALIDATION_SUBJECTS:
        print(f"  {subject}")
    print(
        "\nAny other record has no validated operating point and is refused, "
        "rather than served another subject's thresholds."
    )
    return 0


def _simulate(args: argparse.Namespace) -> int:
    from .artifacts import EdgeArtifactError
    from .replay import replay_record

    try:
        result = replay_record(
            args.record,
            channel_index=args.channel,
            max_seconds=args.seconds,
            source_root=args.source_root,
            run_root=args.run_root,
            feature_root=args.feature_root,
        )
    except EdgeArtifactError as error:
        print(f"refused: {error}")
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "provenance": result.provenance,
                    "observations": [o.as_dict() for o in result.observations],
                    "alerts": [a.as_dict() for a in result.alerts],
                },
                indent=2,
                default=str,
            )
        )
        return 0

    marks = "".join(STATE_MARK.get(o.state, "?") for o in result.observations)
    for offset in range(0, len(marks), 72):
        print(f"  {marks[offset:offset + 72]}")
    print()
    print(f"  record            {args.record} channel {args.channel}")
    print(f"  windows           {len(result.observations)}")
    print(
        f"  simulated ECG     {result.simulated_seconds / 60:.1f} min in "
        f"{result.wall_seconds:.1f} s wall "
        f"({result.real_time_factor:.0f}x real time)"
    )
    admitted = sum(o.memory_update_admitted for o in result.observations)
    print(f"  memory updates    {admitted}/{len(result.observations)} admitted")
    print(f"  alerts            {len(result.alerts)}")
    for alert in result.alerts:
        span = (
            "still open"
            if alert.open
            else f"{alert.duration_seconds:.0f} s"
        )
        peak = alert.peak_calibrated_probability
        print(
            f"    EVENT {alert.opened_at} -> "
            f"{alert.closed_at or '(open)'} [{span}] "
            f"{alert.window_count} windows, peak p_t "
            f"{'n/a' if peak is None else f'{peak:.4f}'}"
        )
    print()
    print("  provenance:")
    for key in (
        "encoder_architecture",
        "m2_arm",
        "u1_family",
        "t2_arm",
        "t1_policy_id",
        "t1_held_out_subject",
        "detector_threshold",
        "sealed_test_state",
    ):
        if key in result.provenance:
            print(f"    {key:26s} {result.provenance[key]}")
    print(
        "\n  This is a laptop simulation replaying a stored recording. It is "
        "not an\n  acquisition path, and no sealed test data was accessed."
    )
    return 0


def _console(args: argparse.Namespace) -> int:
    from .artifacts import EdgeArtifactError
    from .console import render

    try:
        report = render(
            args.record,
            channel_index=args.channel,
            seconds=args.seconds,
            source_root=args.source_root,
            run_root=args.run_root,
            feature_root=args.feature_root,
            architecture_question=args.ask,
        )
    except EdgeArtifactError as error:
        print(f"refused: {error}")
        return 2
    print(report.text)
    return 0
