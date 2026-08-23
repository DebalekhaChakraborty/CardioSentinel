"""`cardiosentinel agent explain` -- provenance-backed alert explanations."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ..edge.artifacts import DEFAULT_FEATURE_ROOT, DEFAULT_RUN_ROOT, DEFAULT_SOURCE_ROOT


def add_agent_commands(subparsers: Any) -> None:  # noqa: ANN401 - argparse action
    parser = subparsers.add_parser("agent", help="Evidence-grounded agents.")
    commands = parser.add_subparsers(dest="agent_command", required=True)

    explain = commands.add_parser(
        "explain", help="Replay a record and explain every alert it raises."
    )
    explain.add_argument("record")
    explain.add_argument("--channel", type=int, default=0)
    explain.add_argument("--seconds", type=float, default=2400.0)
    explain.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    explain.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    explain.add_argument("--feature-root", default=str(DEFAULT_FEATURE_ROOT))
    explain.add_argument("--json", action="store_true")

    graph = commands.add_parser(
        "graph", help="Emit the provenance graph for a record's alerts."
    )
    graph.add_argument("record")
    graph.add_argument("--channel", type=int, default=0)
    graph.add_argument("--seconds", type=float, default=2400.0)
    graph.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    graph.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    graph.add_argument("--feature-root", default=str(DEFAULT_FEATURE_ROOT))
    graph.add_argument(
        "--format",
        choices=("json", "mermaid", "lineage"),
        default="json",
        help="json is the language-model substrate; mermaid is a figure.",
    )
    graph.add_argument(
        "--of",
        default="measurement:p_t",
        help="Node to trace with --format lineage.",
    )

    explain_why = commands.add_parser(
        "why", help="Explain a record's alerts in language, with the mode declared."
    )
    explain_why.add_argument("record")
    explain_why.add_argument("--channel", type=int, default=0)
    explain_why.add_argument("--seconds", type=float, default=2400.0)
    explain_why.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    explain_why.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    explain_why.add_argument("--feature-root", default=str(DEFAULT_FEATURE_ROOT))
    explain_why.add_argument(
        "--no-generative",
        action="store_true",
        help="Force the deterministic renderer even if a provider is configured.",
    )
    explain_why.add_argument("--json", action="store_true")

    boundary = commands.add_parser(
        "check-claims", help="Check text against the publication claim boundary."
    )
    boundary.add_argument("text", help="Text to check.")


def run_agent_command(args: argparse.Namespace) -> int:
    if args.agent_command == "check-claims":
        return _check_claims(args)
    if args.agent_command == "graph":
        return _graph(args)
    if args.agent_command == "why":
        return _why(args)
    return _explain(args)


def _check_claims(args: argparse.Namespace) -> int:
    from .claims import find_violations

    violations = find_violations(args.text)
    if not violations:
        print("clean: no Appendix A violation found.")
        print(
            "  (lexical guard -- it cannot catch a novel sentence that means "
            "the same thing)"
        )
        return 0
    print(f"{len(violations)} violation(s):")
    for violation in violations:
        print(f"  - {violation}")
    return 1


def _explain(args: argparse.Namespace) -> int:
    from ..edge.artifacts import EdgeArtifactError
    from ..edge.replay import replay_record
    from .evidence import EvidenceAgent

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

    agent = EvidenceAgent(result.provenance)
    records = [
        agent.explain(alert, result.observations, index=index)
        for index, alert in enumerate(result.alerts)
    ]

    if args.json:
        print(json.dumps([r.as_dict() for r in records], indent=2, default=str))
        return 0

    if not records:
        print(
            f"{args.record}: {len(result.observations)} windows, no alert raised. "
            "Nothing to explain."
        )
        return 0
    for index, record in enumerate(records):
        if index:
            print("\n" + "-" * 72 + "\n")
        print(agent.render(record))
    return 0


def _graph(args: argparse.Namespace) -> int:
    from ..edge.artifacts import EdgeArtifactError
    from ..edge.replay import replay_record
    from .evidence import EvidenceAgent
    from .graph import build_evidence_graph, summarise_lineage

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

    if not result.alerts:
        print(f"{args.record}: no alert raised, so there is no graph to build.")
        return 0

    agent = EvidenceAgent(result.provenance)
    graphs = [
        build_evidence_graph(
            agent.explain(alert, result.observations, index=index),
            run_root=args.run_root,
        )
        for index, alert in enumerate(result.alerts)
    ]

    for index, graph in enumerate(graphs):
        if index:
            print()
        if args.format == "json":
            print(graph.to_json())
        elif args.format == "mermaid":
            print(graph.to_mermaid())
        else:
            print(f"{graph.root}  lineage of {args.of}:")
            for line in summarise_lineage(graph, args.of):
                print(f"  {line}")
    return 0


def _why(args: argparse.Namespace) -> int:
    import textwrap

    from ..edge.artifacts import EdgeArtifactError
    from ..edge.replay import replay_record
    from .evidence import EvidenceAgent
    from .explain import PatientExplanationAgent
    from .graph import build_evidence_graph
    from .providers import default_provider

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

    if not result.alerts:
        print(f"{args.record}: no alert raised, so there is nothing to explain.")
        return 0

    provider = None if args.no_generative else default_provider()
    agent = PatientExplanationAgent(provider)
    evidence = EvidenceAgent(result.provenance)

    explanations = []
    for index, alert in enumerate(result.alerts):
        graph = build_evidence_graph(
            evidence.explain(alert, result.observations, index=index),
            run_root=args.run_root,
        )
        explanations.append(agent.explain(graph))

    if args.json:
        print(json.dumps([e.as_dict() for e in explanations], indent=2, default=str))
        return 0

    for index, explanation in enumerate(explanations):
        if index:
            print()
        print(f"[{index + 1}/{len(explanations)}]  mode={explanation.explanation_mode}"
              f"  provider={explanation.provider}"
              f"  source={explanation.context_source}")
        if explanation.fallback_reason:
            print(f"  fell back because: {explanation.fallback_reason}")
        for violation in explanation.claim_violations:
            print(f"    rejected: {violation}")
        print()
        print(textwrap.fill(explanation.text, 76, initial_indent="  ",
                            subsequent_indent="  "))
    return 0
