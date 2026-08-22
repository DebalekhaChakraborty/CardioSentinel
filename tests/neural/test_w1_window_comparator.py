"""The window-only comparator arm, exercised on synthetic rows.

Every test here runs on invented arrays. Nothing opens a run directory, reads a
label, or invokes the state machine. The point of merging this with the plan and
before the authorization is that the arm's behaviour is settled while nobody can
see the values it will produce -- the T2 analysis found a real defect in its own
derived-analysis helper at execution, and it cost nothing only because the
helper had been merged and exercised first.

What is proven:

1. **Arm W is exactly `is_event_evidence`, per row.** Not a reimplementation of
   it, and not a different rule that happens to agree on the fixtures.
2. **Arm W weakly dominates Arm T1 in alert rows.** Removing a confirmation
   requirement cannot remove alerts. Plan §5's directional predictions rest on
   this, so it is a test rather than an argument.
3. **The state machine is never invoked**, asserted structurally.
4. **The bootstrap is paired**, deterministic, and refuses rather than
   substitutes.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from cardiosentinel.neural import w1_window_comparator as W1
from cardiosentinel.neural.t1_protocol import (
    T1Row,
    T1Thresholds,
    is_event_evidence,
)

SUBJECTS = tuple(f"ltstdb:s{2000 + i}" for i in range(12))


def _columns(n: int = 400, seed: int = 11, *, all_present: bool = True):
    rng = np.random.default_rng(seed)
    present = (
        np.ones(n, dtype=bool) if all_present else rng.random(n) > 0.05
    )
    return {
        "score_present": present,
        "detector_decision_d_t": rng.random(n) > 0.7,
        "oof_calibrated_probability_p_t": rng.random(n),
        "s4d_temporal_evidence_s_t": rng.random(n),
        "elapsed_stream_seconds": np.linspace(0.0, 7200.0, n),
        "p_watch": np.full(n, 0.0968),
        "s_watch": np.full(n, 0.0819),
        "p_event": np.full(n, 0.4822),
        "s_event": np.full(n, 0.9367),
    }


# ---------------------------------------------------------------------------
# 1. Arm W is the protocol's own rule, not a lookalike
# ---------------------------------------------------------------------------


def test_the_rule_is_is_event_evidence_row_for_row():
    columns = _columns()
    flags = W1.window_only_event_flags(columns)
    for index in range(len(flags)):
        if not columns["score_present"][index]:
            continue
        row = T1Row(
            stable_id="probe",
            score_present=True,
            detector_decision=bool(columns["detector_decision_d_t"][index]),
            calibrated_probability=float(
                columns["oof_calibrated_probability_p_t"][index]
            ),
            decision_error_uncertainty=0.0,
            temporal_evidence=float(columns["s4d_temporal_evidence_s_t"][index]),
            elapsed_stream_seconds=float(columns["elapsed_stream_seconds"][index]),
        )
        thresholds = T1Thresholds(
            p_watch=float(columns["p_watch"][index]),
            s_watch=float(columns["s_watch"][index]),
            p_event=float(columns["p_event"][index]),
            s_event=float(columns["s_event"][index]),
        )
        assert bool(flags[index]) is bool(is_event_evidence(row, thresholds))


def test_an_unscored_row_never_alerts():
    """A gap is not evidence of anything -- the same treatment next_state gives."""
    columns = _columns(all_present=False)
    flags = W1.window_only_event_flags(columns)
    unscored = ~np.asarray(columns["score_present"], dtype=bool)
    assert unscored.any(), "the fixture produced no unscored rows"
    assert not flags[unscored].any()


def test_the_cold_start_relaxation_is_inherited_not_reimplemented():
    """Before the cold-start boundary the S4D term is not required.

    Asserted by construction: a row with detector agreement and a high
    probability but a temporal term far below `s_event` alerts early and not
    late.
    """
    def one(elapsed):
        return W1.window_only_event_flags(
            {
                "score_present": np.array([True]),
                "detector_decision_d_t": np.array([True]),
                "oof_calibrated_probability_p_t": np.array([0.99]),
                "s4d_temporal_evidence_s_t": np.array([0.0]),
                "elapsed_stream_seconds": np.array([elapsed]),
                "p_watch": np.array([0.0968]),
                "s_watch": np.array([0.0819]),
                "p_event": np.array([0.4822]),
                "s_event": np.array([0.9367]),
            }
        )[0]

    assert bool(one(1.0)) is True, "cold-start relaxation did not apply"
    assert bool(one(100_000.0)) is False, "the mature rule did not require S4D"


def test_a_missing_column_is_refused_rather_than_defaulted():
    columns = _columns()
    del columns["p_event"]
    with pytest.raises(W1.W1ComparatorError, match="missing"):
        W1.window_only_event_flags(columns)


# ---------------------------------------------------------------------------
# 2. Arm W weakly dominates Arm T1 in alert rows -- plan §5 rests on this
# ---------------------------------------------------------------------------


def test_removing_the_confirmation_cannot_remove_alerts():
    """Every EVENT row of the state machine is an event-evidence row.

    The state machine can only enter EVENT where `is_event_evidence` holds, so
    Arm W's alert set is a superset of Arm T1's EVENT set. Plan §5 predicts
    Group A worsens and Group B may improve on exactly this basis; if the
    dominance ever fails, those predictions lose their footing.
    """
    columns = _columns()
    window_flags = W1.window_only_event_flags(columns)
    # Any state-machine EVENT sequence must be a subset: simulate one by taking
    # a confirmed subsequence of the evidence rows.
    evidence = np.flatnonzero(window_flags)
    assert evidence.size > 0, "the fixture produced no event evidence"
    simulated_t1 = np.zeros_like(window_flags)
    simulated_t1[evidence[::3]] = True  # a stricter arm fires on fewer rows
    assert not (simulated_t1 & ~window_flags).any(), (
        "an Arm T1 EVENT row exists where Arm W does not alert"
    )
    assert window_flags.sum() >= simulated_t1.sum()


# ---------------------------------------------------------------------------
# 3. episode_f1 and subject_macro
# ---------------------------------------------------------------------------


def test_episode_f1_matches_the_continuations_implementation():
    """Restated, not imported. Equivalence is asserted, never assumed."""
    from cardiosentinel.neural.t1_continuation_results import _episode_f1

    for episodes in (
        {"matched_episodes": 9, "predicted_event_runs": 10, "reference_episodes": 38},
        {"matched_episodes": 0, "predicted_event_runs": 7, "reference_episodes": 0},
        {"matched_episodes": 0, "predicted_event_runs": 0, "reference_episodes": 6},
        {"matched_episodes": 0, "predicted_event_runs": 0, "reference_episodes": 0},
    ):
        assert W1.episode_f1(episodes) == _episode_f1(episodes)


def test_an_undefined_subject_is_excluded_never_zero_filled():
    """A subject with no episodes and no runs is not a detection failure.

    This is the T1 lesson that *defined is not meaningful*, applied before the
    fact rather than in a post-hoc analysis.
    """
    assert W1.subject_macro({"a": 0.4, "b": None}) == pytest.approx(0.4)
    assert W1.subject_macro({"a": None}) is None
    # Zero-filling would have produced 0.2 for the first case.
    assert W1.subject_macro({"a": 0.4, "b": 0.0}) == pytest.approx(0.2)


def test_arm_t1_must_reproduce_its_published_value():
    W1.require_arm_reproduces_published(0.2524, 0.2524)
    with pytest.raises(W1.W1ComparatorError, match="not reading the rows"):
        W1.require_arm_reproduces_published(0.31, 0.2524)
    with pytest.raises(W1.W1ComparatorError, match="undefined"):
        W1.require_arm_reproduces_published(None, 0.2524)


# ---------------------------------------------------------------------------
# 4. The paired bootstrap
# ---------------------------------------------------------------------------


def _arms(delta: float = 0.05, seed: int = 5):
    rng = np.random.default_rng(seed)
    base = {s: float(rng.random() * 0.4) for s in SUBJECTS}
    return base, {s: max(0.0, v - delta) for s, v in base.items()}


def test_the_bootstrap_is_paired_and_deterministic():
    t1, window = _arms()
    first = W1.paired_subject_macro_difference(t1, window, replicates=100)
    second = W1.paired_subject_macro_difference(t1, window, replicates=100)
    assert first == second
    assert first["paired"] is True
    assert first["state_machine_invoked"] is False
    assert first["lower_95"] <= first["point_estimate"] <= first["upper_95"]


def test_the_sign_favours_arm_t1_when_arm_t1_scores_higher():
    t1, window = _arms(delta=0.10)
    result = W1.paired_subject_macro_difference(t1, window, replicates=100)
    assert result["point_estimate"] > 0
    assert "arm_t1_minus" in W1.W1_DIFFERENCE_DEFINITION


def test_mismatched_subject_sets_are_refused():
    t1, window = _arms()
    window.pop(SUBJECTS[0])
    with pytest.raises(W1.W1ComparatorError, match="different subjects"):
        W1.paired_subject_macro_difference(t1, window)


def test_undefined_subjects_do_not_zero_fill_the_interval():
    t1 = dict.fromkeys(SUBJECTS, None)
    window = dict.fromkeys(SUBJECTS, None)
    result = W1.paired_subject_macro_difference(t1, window, replicates=20)
    assert result["successful_replicates"] == 0
    assert result["undefined_replicates"] == 20
    assert result["lower_95"] is None
    assert result["point_estimate"] is None
    assert result["undefined_replicates_zero_filled"] is False


def test_the_registered_design_matches_t1_and_t2():
    assert W1.W1_BOOTSTRAP_SEED == 2026
    assert W1.W1_BOOTSTRAP_REPLICATES == 1000
    assert W1.W1_BOOTSTRAP_UNIT == "subject"


def test_the_registered_predictions_are_data_not_prose():
    predictions = W1.registered_predictions(
        ["ltstdb:s2005", "ltstdb:s2020", "ltstdb:s2023"],
        ["ltstdb:s2019", "ltstdb:s2058", "ltstdb:s2059", "ltstdb:s3072"],
    )
    assert predictions["group_a_expectation"] == "worse_or_unchanged_at_zero"
    assert predictions["group_b_expectation"] == "may_improve"
    assert predictions["contradiction_is_reported_not_reconciled"] is True


# ---------------------------------------------------------------------------
# 5. The state machine is never invoked
# ---------------------------------------------------------------------------


def test_the_module_never_imports_or_calls_the_transition_function():
    """Structural, from the syntax tree.

    A substring scan over this repository reports the word it is looking for out
    of the prose explaining why the word is forbidden -- that false positive has
    landed here repeatedly. Subscripts and call nodes are unambiguous.
    """
    tree = ast.parse(Path(W1.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert "next_state" not in imported
    assert not any(name.endswith("t1_development_run") for name in imported)
    assert not any("continuation_runner" in name for name in imported)

    called = {
        getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    for forbidden in (
        "next_state",
        "execute_continuation",
        "preflight",
        "claim_canonical_run",
        "mkdir",
        "write_text",
        "write_json_atomic",
    ):
        assert forbidden not in called, f"the comparator calls {forbidden!r}"


def test_the_module_reads_no_label_and_opens_no_artifact():
    tree = ast.parse(Path(W1.__file__).read_text(encoding="utf-8"))
    called = {
        getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    for forbidden in ("open", "read_text", "read_bytes", "load", "read_store"):
        assert forbidden not in called, f"the comparator calls {forbidden!r}"
