"""The demo is contracted by `docs/explanation/DEMO_SCENARIO.md`, and the contract is
checked.

A demonstration that quietly stops matching its description is the same failure
this repository has already had four times -- a lost disclaimer (#84), a stale
handbook section (#88), a test lost to a merge race (#90/#91), a keyword
collision (#87/#92) -- with an audience watching.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "explanation" / "DEMO_SCENARIO.md"
BUNDLE = ROOT / "reproducibility" / "demo_bundle"
SOURCE = ROOT / "cardiosentinel-data" / "ltstdb" / "1.0.0"

RECORD = "s20201"
SUBJECT = "ltstdb:s2020"
SECONDS = 2400.0


def test_the_contract_document_exists_and_states_its_limits():
    text = CONTRACT.read_text(encoding="utf-8")
    for required in (
        "Simulation only",
        "Not a diagnosis",
        "Not deployment validation",
        "machine-checked",
    ):
        assert required in text, required


def test_the_console_limitations_match_the_contract():
    """Runs without any evidence: the constant is importable on its own."""
    from cardiosentinel.edge.console import LIMITATIONS

    text = CONTRACT.read_text(encoding="utf-8")
    assert len(LIMITATIONS) == 5
    for item in LIMITATIONS:
        assert item in text, f"console states {item!r} and the contract does not"


@pytest.mark.skipif(
    not SOURCE.is_file() and not (SOURCE / f"{RECORD}.hea").is_file(),
    reason=(
        f"{RECORD} absent from cardiosentinel-data. The ECG record is fetched "
        "from PhysioNet per reproducibility/DATA_ACCESS.md."
    ),
)
class TestScenarioOutcome:
    """§2-§4 of the contract, executed against the committed demo bundle."""

    @pytest.fixture(scope="class")
    def report(self):
        from cardiosentinel.edge.console import render

        return render(
            RECORD,
            seconds=SECONDS,
            source_root=SOURCE,
            run_root=BUNDLE / "runs",
            feature_root=BUNDLE / "features",
        )

    def test_expected_outcome(self, report):
        assert report.subject_id == SUBJECT
        assert report.windows >= 400
        assert report.alerts == 1, "the contract specifies exactly one EVENT run"
        assert report.memory_updates_admitted == 0

    def test_expected_alert_values(self, report):
        text = report.text
        assert "00:17:05 -> 00:27:45" in text
        assert "640 s across 129 windows" in text
        assert "0.545613" in text

    def test_expected_gate_pattern(self, report):
        assert (
            "G1 PASS   G2 PASS   G3 PASS   G4 BLOCK   G5 BLOCK   G6 PASS"
            in report.text
        )
        assert "contamination control working" in report.text

    def test_expected_provenance(self, report):
        p = report.provenance
        assert p["encoder_architecture"] == "B4BTransformerCNN"
        assert p["m2_arm"] == "M2-G"
        assert p["u1_family"] == "platt_logistic_on_recovered_logit"
        assert p["t2_arm"] == "CausalS4DLongitudinal"
        assert p["t1_policy_id"] == "qw0.9_qe0.99_FAST"
        assert p["t1_held_out_subject"] == SUBJECT
        assert p["sealed_test_state"] == "unopened"

    def test_the_explanation_declares_its_mode(self, report):
        assert "mode=DETERMINISTIC" in report.text
        assert "no provider configured" in report.text

    def test_every_limitation_is_printed(self, report):
        from cardiosentinel.edge.console import LIMITATIONS

        for item in LIMITATIONS:
            assert item in report.text, f"console omitted: {item}"

    def test_the_research_panel_explains_a_selection_without_recommending(
        self, report
    ):
        text = report.text
        assert "RESEARCH LINEAGE" in text
        assert "Lifecycle:" in text
        assert "S4D outperforms GRU" in text  # listed as a FORBIDDEN claim

    def test_the_evidence_panel_traverses_to_a_lock(self, report):
        assert "U1 Platt calibration experiment lock" in report.text

    def test_the_console_output_respects_the_claim_boundary(self, report):
        from cardiosentinel.agents import claims

        # The console quotes forbidden claims in order to disclaim them: its
        # own LIMITATIONS block, the explanation's closing sentence, and the
        # architecture panel's "does NOT support" list. Declared, per §53.
        from cardiosentinel.edge.console import LIMITATIONS

        quoting = [
            *LIMITATIONS,
            claims.SYSTEM_BEHAVIOUR_ONLY,
            "S4D outperforms GRU",
            "S4D is the better architecture",
            "the difference is statistically significant",
        ]
        violations = claims.audit(report.text, quoting=quoting)
        assert violations == (), [str(v) for v in violations]
