"""The evidence graph: provenance you can traverse instead of read.

`EvidenceRecord` is a flat dict. It answers *"what produced this alert?"* only
if you already know which key to look at, and it cannot answer *"which frozen
artifacts feed the calibrated probability, and what locked them?"* at all --
that relationship exists in the researchers' heads and in prose.

Here it is a graph. Nodes are the things that exist -- the alert, each measured
quantity, each admission condition, each retained component, each artifact and
the experiment lock that froze it. Edges are typed relations between them, so
lineage is a traversal rather than a recollection.

**Why this sits between the Evidence Agent and any language model.** A flat dict
handed to an LLM invites it to narrate correlations it can see in the values. A
graph hands it *structure*: this probability came from that calibrator, which
was locked by that experiment, which never touched TEST. The model's job
collapses from "explain the alert" to "put this path into a sentence", which is
the difference between a translator and a scientist.

Nothing here computes anything. Every value is copied from an `EvidenceRecord`
or read from a frozen lock file.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..edge.artifacts import DEFAULT_RUN_ROOT
from ..neural.integrity import canonical_sha256, verify_experiment_lock
from .evidence import EvidenceRecord

#: What a node is. Kinds are closed: an unknown kind means the graph builder
#: learned about something it was never designed to describe.
NODE_KINDS = (
    "alert",       # the event itself
    "measurement", # a quantity the run recorded
    "gate",        # one G1-G6 admission condition
    "component",   # a retained pipeline stage
    "artifact",    # a checkpoint, transform or calibrator, with its digest
    "lock",        # the experiment lock that froze an artifact
    "policy",      # the T1 operating point
    "constraint",  # something the alert does not establish
)

#: How nodes relate. Read edges as `source -> relation -> target`.
EDGE_RELATIONS = (
    "raised_from",   # alert  -> measurement
    "admitted_by",   # alert  -> gate
    "produced_by",   # measurement -> component
    "realised_by",   # component -> artifact
    "frozen_by",     # artifact -> verified lock
    "provenance_unavailable",  # artifact -> absent or unverifiable record
    "operated_at",   # alert -> policy
    "bounded_by",    # alert -> constraint
)


class EvidenceGraphError(RuntimeError):
    """The graph cannot be built or traversed as asked."""


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    kind: str
    label: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in NODE_KINDS:
            raise EvidenceGraphError(
                f"Unknown node kind {self.kind!r}. Kinds are closed: "
                f"{', '.join(NODE_KINDS)}."
            )


@dataclass(frozen=True)
class EvidenceEdge:
    source: str
    relation: str
    target: str

    def __post_init__(self) -> None:
        if self.relation not in EDGE_RELATIONS:
            raise EvidenceGraphError(
                f"Unknown relation {self.relation!r}. Relations are closed: "
                f"{', '.join(EDGE_RELATIONS)}."
            )


class EvidenceGraph:
    """A directed provenance graph rooted at one alert."""

    def __init__(self, root: str) -> None:
        self._root = root
        self._nodes: dict[str, EvidenceNode] = {}
        self._edges: list[EvidenceEdge] = []

    @property
    def root(self) -> str:
        return self._root

    @property
    def nodes(self) -> tuple[EvidenceNode, ...]:
        return tuple(self._nodes.values())

    @property
    def edges(self) -> tuple[EvidenceEdge, ...]:
        return tuple(self._edges)

    def add_node(self, node: EvidenceNode) -> EvidenceNode:
        self._nodes[node.node_id] = node
        return node

    def add_edge(self, source: str, relation: str, target: str) -> EvidenceEdge:
        for endpoint in (source, target):
            if endpoint not in self._nodes:
                raise EvidenceGraphError(
                    f"Edge endpoint {endpoint!r} is not a node. The graph never "
                    "invents a node to satisfy an edge."
                )
        edge = EvidenceEdge(source=source, relation=relation, target=target)
        self._edges.append(edge)
        return edge

    def node(self, node_id: str) -> EvidenceNode:
        if node_id not in self._nodes:
            raise EvidenceGraphError(f"No node {node_id!r} in this graph.")
        return self._nodes[node_id]

    def successors(self, node_id: str) -> tuple[tuple[str, EvidenceNode], ...]:
        return tuple(
            (edge.relation, self._nodes[edge.target])
            for edge in self._edges
            if edge.source == node_id
        )

    def of_kind(self, kind: str) -> tuple[EvidenceNode, ...]:
        return tuple(node for node in self._nodes.values() if node.kind == kind)

    def lineage(self, node_id: str) -> tuple[EvidenceNode, ...]:
        """Everything reachable downstream of a node, breadth-first.

        Answers *"what produced this?"*. Cycle-safe: the graph is acyclic by
        construction, but a malformed builder should not hang a demo.
        """
        self.node(node_id)
        seen = {node_id}
        order: list[EvidenceNode] = []
        frontier = [node_id]
        while frontier:
            current = frontier.pop(0)
            for _, node in self.successors(current):
                if node.node_id in seen:
                    continue
                seen.add(node.node_id)
                order.append(node)
                frontier.append(node.node_id)
        return tuple(order)

    def as_dict(self) -> dict[str, Any]:
        """The serialisation a language model receives. Structure, not prose."""
        return {
            "root": self._root,
            "nodes": [asdict(node) for node in self._nodes.values()],
            "edges": [asdict(edge) for edge in self._edges],
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.as_dict(), indent=indent, default=str)

    @staticmethod
    def _mermaid_id(node_id: str) -> str:
        """Mermaid identifiers cannot contain `:` or `-`.

        Node ids deliberately do (`component:encoder`, `EVT-s20201-0000`)
        because they are readable in JSON, which is the substrate that matters.
        The diagram gets a sanitised alias; the JSON keeps the real id.
        """
        return "".join(
            character if character.isalnum() else "_" for character in node_id
        )

    def to_mermaid(self) -> str:
        """A diagram of the same graph, for a paper figure or a dashboard."""
        shape = {
            "alert": ('["', '"]'),
            "measurement": ('("', '")'),
            "gate": ('{{"', '"}}'),
            "component": ('["', '"]'),
            "artifact": ('[/"', '"/]'),
            "lock": ('[("', '")]'),
            "policy": ('>"', '"]'),
            "constraint": ('["', '"]'),
        }
        lines = ["graph TD"]
        for node in self._nodes.values():
            open_mark, close_mark = shape[node.kind]
            safe = node.label.replace('"', "'")
            lines.append(
                f"  {self._mermaid_id(node.node_id)}{open_mark}{safe}{close_mark}"
            )
        for edge in self._edges:
            lines.append(
                f"  {self._mermaid_id(edge.source)} -->|{edge.relation}| "
                f"{self._mermaid_id(edge.target)}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Building the graph from one alert
# ---------------------------------------------------------------------------

#: The retained pipeline, in execution order, with the provenance key that names
#: each component's realisation and the run that locked it. This table is the
#: one place the runtime's flat provenance is mapped onto research lineage.
COMPONENT_LINEAGE: tuple[tuple[str, str, str, str | None], ...] = (
    (
        "encoder",
        "B4-B encoder",
        "encoder_architecture",
        "phase3b2-architecture-v1/B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json",
    ),
    (
        "physiology",
        "P1-B physiology fusion",
        "physiology_transform_sha256",
        "phase4-p1-physiology-v1/P1B_phys_fusion_v1/EXPERIMENT_LOCK.json",
    ),
    (
        "memory",
        "M1L long memory / M2-G gated update",
        "m2_arm",
        "phase6-m2-development-v1/"
        "m2-v1-development-two-arm-recovery2__M2-G/M2_EXPERIMENT_LOCK.json",
    ),
    (
        "calibration",
        "U1 Platt calibration",
        "u1_family",
        "phase7-u1-development-v1/u1-v1-development/U1_EXPERIMENT_LOCK.json",
    ),
    (
        "temporal",
        "T2 causal S4D",
        "t2_arm",
        "phase8-t2-development-v1/t2-v1-training/T2_S4D_CHECKPOINT_LOCK.json",
    ),
    (
        "episode",
        "T1 episode state machine",
        "t1_policy_id",
        "phase9-t1-continuation-v1/"
        "t1-v1-measurement-continuation/T1_EXPERIMENT_LOCK.json",
    ),
)

#: Which component produced each measured quantity. The mapping is the pipeline,
#: not a guess: p_t comes out of the calibrator, s_t out of the temporal arm.
MEASUREMENT_SOURCES: tuple[tuple[str, str, str, str], ...] = (
    ("p_t", "calibrated probability", "peak_calibrated_probability", "calibration"),
    ("s_t", "temporal evidence", "peak_temporal_evidence", "temporal"),
    ("d_long", "memory deviation", "max_memory_deviation", "memory"),
    ("u_t", "decision error uncertainty", "decision_error_uncertainty", "calibration"),
)

_LOCK_KEYS = (
    "experiment_id",
    "locked_inference_model",
    "checkpoint_sha256",
    "trainable_parameter_count",
    "test_accessed",
    "sealed_test_state",
    "selection_performed_here",
    "thresholds_generated_here",
)


def _lock_evidence(run_root: Path, relative: str | None) -> dict[str, Any]:
    """Read the interesting fields of an experiment lock, if it is present.

    Absence is recorded rather than raising: the graph must still build on a
    machine that has the code but not the gitignored evidence tree.
    """
    if relative is None:
        return {"lock_available": False, "lock_verified": False}
    path = Path(run_root) / relative
    if not path.is_file():
        return {
            "lock_available": False,
            "lock_verified": False,
            "lock_path": relative,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "lock_available": True,
            "lock_verified": False,
            "lock_path": relative,
            "verification_error": type(error).__name__,
        }
    mechanism = None
    verified = False
    if "experiment_lock_sha256" in payload:
        mechanism = "experiment_lock_self_digest"
        verified = verify_experiment_lock(payload)
    elif "checkpoint_lock_sha256" in payload:
        mechanism = "checkpoint_lock_self_digest"
        recorded = payload.get("checkpoint_lock_sha256")
        body = {
            key: value
            for key, value in payload.items()
            if key != "checkpoint_lock_sha256"
        }
        verified = isinstance(recorded, str) and recorded == canonical_sha256(body)
    evidence: dict[str, Any] = {
        "lock_available": True,
        "lock_verified": verified,
        "lock_path": relative,
        "verification_mechanism": mechanism,
    }
    evidence.update(
        {key: payload[key] for key in _LOCK_KEYS if key in payload}
    )
    return evidence


def _runtime_artifacts_for_component(
    provenance: dict[str, Any], component: str
) -> tuple[dict[str, Any], ...]:
    aliases = {"memory": {"memory", "standardizer"}}
    names = aliases.get(component, {component})
    records = provenance.get("runtime_artifacts")
    if not isinstance(records, list):
        return ()
    return tuple(
        dict(item)
        for item in records
        if isinstance(item, dict) and item.get("component") in names
    )


def build_evidence_graph(
    record: EvidenceRecord,
    *,
    run_root: Path | str = DEFAULT_RUN_ROOT,
    include_research_lineage: bool = True,
) -> EvidenceGraph:
    """Turn one `EvidenceRecord` into a traversable provenance graph."""
    graph = EvidenceGraph(record.alert_id)
    provenance = record.provenance

    graph.add_node(
        EvidenceNode(
            node_id=record.alert_id,
            kind="alert",
            label=f"{record.decision} on {record.record_id}",
            evidence={
                "subject_id": record.subject_id,
                "record_id": record.record_id,
                "channel_index": record.channel_index,
                "entered_from": record.entered_from,
                "closed_into": record.closed_into,
                "opened_at": record.opened_at,
                "closed_at": record.closed_at,
                "still_open": record.still_open,
                "window_count": record.window_count,
                "duration_seconds": record.duration_seconds,
            },
        )
    )

    # Components, their realisations, and the locks that froze them.
    for key, label, provenance_key, lock_path in COMPONENT_LINEAGE:
        component_id = f"component:{key}"
        graph.add_node(
            EvidenceNode(node_id=component_id, kind="component", label=label)
        )
        realisation = provenance.get(provenance_key)
        if realisation is not None:
            runtime_records = _runtime_artifacts_for_component(provenance, key)
            if runtime_records:
                artifact_nodes = []
                for index, runtime_record in enumerate(runtime_records):
                    suffix = "" if index == 0 else f":{runtime_record['component']}"
                    artifact_id = f"artifact:{key}{suffix}"
                    artifact_nodes.append(artifact_id)
                    graph.add_node(
                        EvidenceNode(
                            node_id=artifact_id,
                            kind="artifact",
                            label=str(runtime_record["logical_artifact_id"]),
                            evidence=runtime_record,
                        )
                    )
                    graph.add_edge(component_id, "realised_by", artifact_id)
            else:
                artifact_id = f"artifact:{key}"
                artifact_nodes = [artifact_id]
                graph.add_node(
                    EvidenceNode(
                        node_id=artifact_id,
                        kind="artifact",
                        label=str(realisation),
                        evidence={provenance_key: realisation},
                    )
                )
                graph.add_edge(component_id, "realised_by", artifact_id)
            if include_research_lineage:
                lock_id = f"lock:{key}"
                lock_evidence = _lock_evidence(Path(run_root), lock_path)
                lock_status = (
                    "verified"
                    if lock_evidence["lock_verified"]
                    else "unavailable"
                    if not lock_evidence["lock_available"]
                    else "unverified"
                )
                graph.add_node(
                    EvidenceNode(
                        node_id=lock_id,
                        kind="lock",
                        label=f"{label} experiment lock ({lock_status})",
                        evidence=lock_evidence,
                    )
                )
                relation = (
                    "frozen_by"
                    if lock_evidence["lock_verified"]
                    else "provenance_unavailable"
                )
                for artifact_id in artifact_nodes:
                    graph.add_edge(artifact_id, relation, lock_id)

    # Measured quantities, each attributed to the component that produced it.
    for key, label, attribute, component in MEASUREMENT_SOURCES:
        value = getattr(record, attribute, None)
        measurement_id = f"measurement:{key}"
        graph.add_node(
            EvidenceNode(
                node_id=measurement_id,
                kind="measurement",
                label=label,
                evidence={
                    "symbol": key,
                    "value": value,
                    "defined": value is not None,
                    # s_t is a bounded sigmoid. Saying so here means a model
                    # reading this graph cannot mistake it for a probability.
                    "is_calibrated_probability": key == "p_t",
                },
            )
        )
        graph.add_edge(record.alert_id, "raised_from", measurement_id)
        graph.add_edge(measurement_id, "produced_by", f"component:{component}")

    # The admission gate, condition by condition.
    for condition in record.gate:
        gate_id = f"gate:{condition.condition}"
        graph.add_node(
            EvidenceNode(
                node_id=gate_id,
                kind="gate",
                label=f"{condition.condition} {condition.status}",
                evidence={
                    "condition": condition.condition,
                    "status": condition.status,
                    "passed": condition.passed,
                    "meaning": condition.meaning,
                },
            )
        )
        graph.add_edge(record.alert_id, "admitted_by", gate_id)
        graph.add_edge(gate_id, "produced_by", "component:memory")

    # The operating point, and the fact that it was not chosen here.
    policy_id = "policy:t1"
    graph.add_node(
        EvidenceNode(
            node_id=policy_id,
            kind="policy",
            label=str(provenance.get("t1_policy_id", "unknown policy")),
            evidence={
                key: provenance[key]
                for key in (
                    "t1_policy_id",
                    "t1_held_out_subject",
                    "t1_persistence_profile",
                    "t1_threshold_population",
                    "t1_thresholds_generated_here",
                    "t1_held_out_labels_opened",
                    "detector_threshold",
                    "detector_threshold_selected_here",
                )
                if key in provenance
            },
        )
    )
    graph.add_edge(record.alert_id, "operated_at", policy_id)
    graph.add_edge(policy_id, "produced_by", "component:episode")

    # What the alert does not establish, as first-class nodes rather than a
    # footnote: a model reading the graph should see the boundary as structure.
    for index, statement in enumerate(record.cannot_support):
        constraint_id = f"constraint:{index}"
        graph.add_node(
            EvidenceNode(
                node_id=constraint_id,
                kind="constraint",
                label=statement,
                evidence={"does_not_establish": statement},
            )
        )
        graph.add_edge(record.alert_id, "bounded_by", constraint_id)

    return graph


def summarise_lineage(graph: EvidenceGraph, node_id: str) -> Iterable[str]:
    """One line per hop, for a human or a prompt."""
    for node in graph.lineage(node_id):
        detail = ""
        if node.kind == "artifact" and node.evidence.get("verification_status"):
            mechanism = str(
                node.evidence.get("verification_mechanism", "unknown mechanism")
            ).replace("_", " ")
            detail = f" [digest verified via {mechanism}]"
        elif node.kind == "lock":
            if not node.evidence.get("lock_available"):
                detail = " [experiment lock unavailable]"
            elif not node.evidence.get("lock_verified"):
                detail = " [experiment lock present but unverified]"
            else:
                detail = " [experiment lock verified]"
        yield f"{node.kind:11s} {node.label}{detail}"
