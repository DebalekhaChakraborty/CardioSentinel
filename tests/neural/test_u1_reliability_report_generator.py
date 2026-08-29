"""The U1 reliability report generator, exercised on a synthetic artifact set.

The real per-bin values are unread until
`docs/experiments/u1/U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md` §5 step 2, which
follows
that plan being merged. So the generator is proven here against a fixture whose
shape matches the promoted artifacts and whose numbers are invented.

What is proven: the plan's reporting rules are properties of the code, not
intentions in a document.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = REPOSITORY_ROOT / "scripts" / "provenance" / "gen_u1_reliability_report.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("gen_u1_reliability", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN = _load_generator()


def _bins(count: int = 15, *, empty_at=(), sparse_at=()):
    out = []
    for index in range(count):
        if index in empty_at:
            rows, mean, empirical = 0, None, None
        elif index in sparse_at:
            rows, mean, empirical = 5, index / count, (index + 1) / count
        else:
            rows, mean, empirical = 400, index / count, (index + 0.5) / count
        out.append(
            {
                "count": rows,
                "minimum_probability": mean,
                "maximum_probability": mean,
                "mean_probability": mean,
                "empirical_positive_fraction": empirical,
            }
        )
    return out


def _bin(rows: int, mean, empirical) -> dict:
    return {
        "count": rows,
        "mean_probability": mean,
        "empirical_positive_fraction": empirical,
    }


def _family(name: str, *, nll: float, brier: float, **kwargs):
    return {
        "name": name,
        "evidence_class": "u1_oof_calibration_family",
        "out_of_fold": True,
        "development_evidence": True,
        "clamp_delta": 1e-7,
        "row_count": 6000,
        "negative_log_likelihood": nll,
        "brier": brier,
        "reliability_equal_width": {
            "binning": "equal_width",
            "bin_count": 15,
            "row_count": 6000,
            "expected_calibration_error": 0.0123,
            "bins": _bins(**kwargs),
        },
        "reliability_equal_mass": {
            "binning": "equal_mass",
            "bin_count": 15,
            "row_count": 6000,
            "expected_calibration_error": 0.0119,
            "bins": _bins(),
        },
    }


@pytest.fixture
def run_root(tmp_path):
    root = tmp_path / "u1-v1-development"
    root.mkdir()
    (root / "U1_OOF_CALIBRATION.json").write_text(
        json.dumps(
            {
                "artifact_class": "u1_oof_calibration",
                "out_of_fold": True,
                "families": {
                    GEN.RETAINED: _family(
                        GEN.RETAINED,
                        nll=0.21,
                        brier=0.05,
                        empty_at=(0,),
                        sparse_at=(1,),
                    ),
                    GEN.REJECTED: _family(GEN.REJECTED, nll=0.24, brier=0.06),
                    GEN.BASELINE: _family(GEN.BASELINE, nll=0.98, brier=0.19),
                },
            }
        )
    )
    (root / "U1_FAMILY_SELECTION.json").write_text(
        json.dumps(
            {
                "selected_family": GEN.RETAINED,
                "criterion": "pooled_oof_nll",
                "ece_used": False,
                "brier_used": False,
            }
        )
    )
    (root / "U1_OOF_RESULT.json").write_text(
        json.dumps(
            {
                "development_evidence": True,
                "development_optimistic": True,
                "development_optimism_note": "Development evidence is optimistic.",
                "test_accessed": False,
                "sealed_test_state": "unopened",
            }
        )
    )
    (root / "U1_EXPERIMENT_LOCK.json").write_text(json.dumps({"locked": True}))
    return root


def test_the_report_renders(run_root):
    assert GEN.build_report(run_root).startswith(
        "# U1 Calibration Reliability — Descriptive Report, V1"
    )


def test_the_signed_gap_convention_is_empirical_minus_mean():
    """Positive means under-confident. Fixed before any value was visible."""
    assert GEN.signed_gap(0.60, 0.50) == pytest.approx(0.10)
    assert GEN.signed_gap(0.40, 0.50) == pytest.approx(-0.10)


def test_an_undefined_bin_is_never_filled():
    assert GEN.signed_gap(None, 0.5) is None
    assert GEN.signed_gap(0.5, None) is None
    assert GEN.fmt(None) == GEN.UNDEFINED


def test_the_baseline_is_reported_at_the_same_resolution(run_root):
    """Plan §4 rule 3: a calibration number without its baseline is not readable."""
    report = GEN.build_report(run_root)
    assert "## 4. Per-bin reliability — the uncalibrated baseline" in report
    assert report.count("### 4.1 Equal-width") == 1
    assert report.count("### 4.2 Equal-mass") == 1
    # Both families' bin tables are present at full depth.
    assert report.count("| 14 |") == 4


def test_all_three_families_appear_in_the_scalar_table(run_root):
    report = GEN.build_report(run_root)
    for family in (GEN.RETAINED, GEN.REJECTED, GEN.BASELINE):
        assert f"| `{family}` |" in report


def test_bin_degeneracy_is_reported(run_root):
    """Defined is not meaningful; the shape of the mass is reported."""
    shape = GEN.degeneracy(
        {"bins": _bins(empty_at=(0, 2), sparse_at=(1,))}
    )
    assert shape["bin_count"] == 15
    assert shape["empty_bins"] == 2
    assert shape["sparse_bins"] == 1
    assert shape["smallest"] == 0
    assert shape["largest"] == 400
    assert "## 5. Bin degeneracy" in GEN.build_report(run_root)


def test_the_report_states_what_it_cannot_support(run_root):
    report = GEN.build_report(run_root)
    for required in (
        "Nothing about TEST",
        "No generalisation claim",
        "No clinical safety claim",
        "No routing claim",
        "No support for the retention decision",
        "score_is_calibrated_probability: false",
        "Improved ECE alone is not a success criterion",
    ):
        assert required in report, f"the report omits {required!r}"


def test_the_split_retention_is_restated(run_root):
    report = GEN.build_report(run_root)
    assert "Platt calibration retained" in report
    assert "not**\nretained" in report or "**not**" in report


def test_every_artifact_read_is_digested(run_root):
    report = GEN.build_report(run_root)
    for name in GEN.ARTIFACTS:
        assert f"`{name}` — SHA-256 " in report


def test_the_generator_opens_no_npz_store():
    """Structural, from the syntax tree rather than a substring scan."""
    import ast

    tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
    called = {
        getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    for forbidden in ("load_npz", "read_store", "savez", "mkdir", "makedirs"):
        assert forbidden not in called, f"the generator calls {forbidden!r}"
    assert "npz" not in {
        node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
    }


def test_the_commit_reaches_the_report(run_root):
    """Plan §3.4 requires the commit the report was generated at."""
    report = GEN.build_report(run_root, git_sha="0123456789abcdef")
    assert "| Generated at commit | `0123456789abcdef` |" in report


def test_main_records_the_commit_rather_than_leaving_it_unrecorded(
    run_root, tmp_path, monkeypatch
):
    """The default is `unrecorded`; `main` must not ship it.

    Hermetic: the run root and the SHA lookup are both stubbed, so this
    proves the wiring without reading the promoted artifacts.
    """
    monkeypatch.setattr(GEN, "RUN", run_root)
    monkeypatch.setattr(GEN, "_git_sha", lambda: "deadbeefcafe")
    destination = tmp_path / "report.md"
    assert GEN.main(["gen", str(destination)]) == 0
    written = destination.read_text(encoding="utf-8")
    assert "`deadbeefcafe`" in written
    assert "unrecorded" not in written


def test_the_sha_lookup_resolves_in_this_repository():
    sha = GEN._git_sha()
    assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha), sha


def test_clamp_delta_is_reported_and_not_flattened(run_root):
    """Plan §3.1 names `clamp_delta`; six-place float rendering shows 0.000000."""
    report = GEN.build_report(run_root)
    assert "`clamp_delta`" in report
    assert GEN.fmt_exact(1e-07) == "1e-07"
    assert GEN.fmt_exact(None) == GEN.UNDEFINED


def test_protocol_condition_two_is_restated_with_its_verdict(run_root):
    """Plan §3.2 requires the prespecified condition beside the bins."""
    report = GEN.build_report(run_root)
    assert "## 2.1 Protocol §16 condition 2" in report
    assert "pooled OOF Brier and NLL" in report
    assert "restates that record" in report


def test_the_baseline_asymmetry_is_carried_forward(run_root):
    """The artifact says the baseline is a reference, not OOF evidence."""
    report = GEN.build_report(run_root)
    assert "not a matched comparison" in report
    assert "baseline_semantics" in report


def test_the_direction_of_the_gap_is_read_from_the_sign(run_root):
    note = GEN.direction_note(
        {
            "bins": [
                _bin(100, 0.1, 0.2),
                _bin(900, 0.5, 0.1),
                _bin(10, 0.9, None),
            ]
        }
    )
    assert note["positive"] == "0"
    assert note["negative"] == "1"
    assert note["widest_index"] == 1
    assert note["heaviest_index"] == 1 and note["heaviest_rows"] == 900
    assert note["lightest_rows"] == 10
    assert "Gap is positive in bin(s)" in GEN.build_report(run_root)


def test_contiguous_runs_are_collapsed():
    assert GEN._contiguous([0, 1, 2]) == "0-2"
    assert GEN._contiguous([0, 2, 3, 7]) == "0, 2-3, 7"
    assert GEN._contiguous([]) == "none"


def test_no_section_number_is_used_twice(run_root):
    """ECG 14 shipped a report carrying two `## 5.` headings."""
    import re

    report = GEN.build_report(run_root)
    numbers = re.findall(r"^## (\d+)\.", report, flags=re.MULTILINE)
    assert numbers == sorted(numbers, key=int), numbers
    assert len(numbers) == len(set(numbers)), numbers


def test_the_fixed_shape_limitation_is_recorded(run_root):
    """Plan §5 step 4: record it in the report, do not edit the plan."""
    report = GEN.build_report(run_root)
    assert "## 6. A limitation of the shape this plan fixed" in report
    assert "wrong summary for this evidence" in report


def test_the_widest_gap_is_by_magnitude_not_by_minimum():
    """An all-positive column has no minimum that is a widest negative gap."""
    note = GEN.direction_note(
        {
            "bins": [
                _bin(10, 0.1, 0.15),
                _bin(10, 0.2, 0.60),
            ]
        }
    )
    assert note["negative"] == "none"
    assert note["widest_index"] == 1


def test_even_binnings_are_not_described_as_concentrated(run_root):
    """Equal-mass bins are even by construction; the range says so."""
    report = GEN.build_report(run_root)
    assert "Bin counts run from" in report
    assert "widest negative gap" not in report
