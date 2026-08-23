"""The evidence graph: structure, traversal, and the vocabularies it closes."""

from __future__ import annotations

import json

import pytest

from cardiosentinel.agents.evidence import EvidenceAgent
from cardiosentinel.agents.graph import (
    EDGE_RELATIONS,
    NODE_KINDS,
    EvidenceGraph,
    EvidenceGraphError,
    EvidenceNode,
    build_evidence_graph,
    summarise_lineage,
)
from cardiosentinel.edge.alerts import AlertBuilder
from cardiosentinel.edge.session import EdgeObservation

PROVENANCE = {
    "encoder_architecture": "B4BTransformerCNN",
    "m2_arm": "M2-G",
    "u1_family": "platt_logistic_on_recovered_logit",
    "t2_arm": "CausalS4DLongitudinal",
    "t1_policy_id": "qw0.9_qe0.99_FAST",
    "t1_held_out_subject": "ltstdb:s2004",
    "t1_thresholds_generated_here": False,
    "physiology_transform_sha256": "cc6bd3a3",
    "detector_threshold": 0.7554003000259399,
    "detector_threshold_selected_here": False,
    "sealed_test_state": "unopened",
}
GATE = {
    "g1_available": True,
    "g2_finite_representation": True,
    "g3_sqi_admissible": True,
    "g4_normal_evidence": False,
    "g5_not_in_refractory": False,
    "g6_morphology_computable": True,
    "past_observed_count_before": 203,
    "past_update_count_before": 0,
}


def observation(state: str, seconds: float, before: str):
    return EdgeObservation(
        stable_id=f"ltstdb:s20041:0:{int(seconds * 250)}:0",
        record_id="s20041",
        subject_id="ltstdb:s2004",
        channel_index=0,
        start_sample=int(seconds * 250),
        elapsed_stream_seconds=seconds,
        score_present=True,
        detector_score=0.81,
        detector_decision=True,
        calibrated_probability=0.55,
        decision_error_uncertainty=0.45,
        temporal_evidence=0.72,
        memory_deviation=1.31,
        state_before=before,
        state=state,
        streaks={},
        memory_update_admitted=False,
        gate=dict(GATE),
        contains_filter_warmup=False,
    )


@pytest.fixture
def graph(tmp_path):
    builder = AlertBuilder(PROVENANCE)
    observations, previous, alert = [], "NORMAL", None
    for index, state in enumerate(["NORMAL", "WATCH", "EVENT", "EVENT", "NORMAL"]):
        item = observation(state, index * 5.0, previous)
        previous = state
        observations.append(item)
        emitted = builder.observe(item)
        if emitted is not None:
            alert = emitted
    assert alert is not None
    record = EvidenceAgent(PROVENANCE).explain(alert, observations)
    # tmp_path has no lock files: the graph must still build.
    return build_evidence_graph(record, run_root=tmp_path)


def test_the_graph_is_rooted_at_the_alert(graph):
    assert graph.root.startswith("EVT-")
    assert graph.node(graph.root).kind == "alert"


def test_every_pipeline_stage_appears_with_its_artifact_and_lock(graph):
    assert len(graph.of_kind("component")) == 6
    assert len(graph.of_kind("artifact")) == 6
    assert len(graph.of_kind("lock")) == 6


def test_lineage_answers_what_produced_this_measurement(graph):
    """The question a flat provenance dict cannot answer."""
    lineage = [node.node_id for node in graph.lineage("measurement:p_t")]
    assert lineage == ["component:calibration", "artifact:calibration",
                       "lock:calibration"]
    lines = list(summarise_lineage(graph, "measurement:s_t"))
    assert any("T2 causal S4D" in line for line in lines)


def test_the_temporal_score_is_marked_as_not_a_probability(graph):
    """Structure, not a footnote: a model reading this cannot mistake it."""
    assert graph.node("measurement:s_t").evidence["is_calibrated_probability"] is False
    assert graph.node("measurement:p_t").evidence["is_calibrated_probability"] is True


def test_all_six_gate_conditions_are_nodes(graph):
    gates = {node.evidence["condition"] for node in graph.of_kind("gate")}
    assert gates == {"G1", "G2", "G3", "G4", "G5", "G6"}
    status = {
        node.evidence["condition"]: node.evidence["status"]
        for node in graph.of_kind("gate")
    }
    assert status["G4"] == "BLOCK" and status["G5"] == "BLOCK"


def test_the_claim_boundary_is_structure_not_a_footnote(graph):
    constraints = graph.of_kind("constraint")
    assert len(constraints) >= 5
    assert all(
        edge.relation == "bounded_by"
        for edge in graph.edges
        if edge.target.startswith("constraint:")
    )


def test_the_policy_records_that_it_was_not_chosen_here(graph):
    policy = graph.node("policy:t1")
    assert policy.evidence["t1_thresholds_generated_here"] is False
    assert policy.evidence["detector_threshold_selected_here"] is False


def test_a_missing_lock_tree_is_recorded_not_raised(graph):
    """The graph must build on a machine with the code but not the evidence."""
    assert graph.node("lock:calibration").evidence["lock_available"] is False


def test_node_kinds_and_relations_are_closed_vocabularies():
    graph = EvidenceGraph("root")
    with pytest.raises(EvidenceGraphError, match="Unknown node kind"):
        graph.add_node(EvidenceNode(node_id="x", kind="speculation", label="x"))
    graph.add_node(EvidenceNode(node_id="a", kind="alert", label="a"))
    graph.add_node(EvidenceNode(node_id="b", kind="gate", label="b"))
    with pytest.raises(EvidenceGraphError, match="Unknown relation"):
        graph.add_edge("a", "probably_caused", "b")
    assert len(NODE_KINDS) == 8 and len(EDGE_RELATIONS) == 7


def test_an_edge_never_invents_its_endpoints():
    graph = EvidenceGraph("root")
    graph.add_node(EvidenceNode(node_id="a", kind="alert", label="a"))
    with pytest.raises(EvidenceGraphError, match="is not a node"):
        graph.add_edge("a", "raised_from", "measurement:ghost")


def test_the_json_substrate_round_trips(graph):
    """This is what a language model receives."""
    payload = json.loads(graph.to_json())
    assert payload["root"] == graph.root
    assert len(payload["nodes"]) == len(graph.nodes)
    assert len(payload["edges"]) == len(graph.edges)
    assert {edge["relation"] for edge in payload["edges"]} <= set(EDGE_RELATIONS)


def test_mermaid_identifiers_are_sanitised(graph):
    """Node ids carry `:` and `-`; mermaid identifiers cannot."""
    diagram = graph.to_mermaid()
    assert diagram.startswith("graph TD")
    for line in diagram.split("\n")[1:]:
        identifier = line.strip().split("[")[0].split("{")[0].split(">")[0]
        identifier = identifier.split(" ")[0]
        assert ":" not in identifier, line
    assert "component_calibration" in diagram


def test_lineage_of_an_unknown_node_is_refused(graph):
    with pytest.raises(EvidenceGraphError, match="No node"):
        graph.lineage("measurement:invented")
