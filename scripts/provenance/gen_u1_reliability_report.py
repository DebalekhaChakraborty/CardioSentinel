"""Emit the U1 calibration reliability report per the approved plan.

Reads `docs/U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md` §3 as its
specification. Every number is read verbatim from a promoted artifact except the
signed gap named in §3.1, which is the one arithmetic derivation the plan
authorizes. No `.npz` store is opened, no metric is recomputed, and nothing is
written into any run directory.

Usage, from the repository root, on the frozen scientific interpreter:

    python scripts/provenance/gen_u1_reliability_report.py <output.md>

Run it to a scratch path outside the repository and diff, rather than
overwriting a tracked document.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
RUN = (
    REPOSITORY_ROOT
    / "cardiosentinel-runs"
    / "phase7-u1-development-v1"
    / "u1-v1-development"
)

RETAINED = "platt_logistic_on_recovered_logit"
BASELINE = "uncalibrated_baseline"
REJECTED = "temperature_only_on_recovered_logit"
FAMILY_ORDER = (RETAINED, REJECTED, BASELINE)

ARTIFACTS = (
    "U1_OOF_CALIBRATION.json",
    "U1_FAMILY_SELECTION.json",
    "U1_OOF_RESULT.json",
    "U1_EXPERIMENT_LOCK.json",
)

#: Plan §3.3. A bin below this carries too few rows to read its positive
#: fraction as anything but noise; the count is reported either way.
SPARSE_BIN_ROWS = 30

UNDEFINED = "*undefined*"

ECE_KEY = "expected_calibration_error"


def _run_label(root: pathlib.Path) -> str:
    """Repository-relative where possible; absolute otherwise.

    A synthetic fixture root lives outside the repository, and a generator
    that raises on it is a generator that cannot be tested without the
    evidence -- which is the gap this whole exercise exists to close.
    """
    try:
        return str(root.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(root)


def load(root: pathlib.Path, name: str) -> dict:
    return json.loads((root / name).read_text(encoding="utf-8"))


def digest(root: pathlib.Path, name: str) -> str:
    return hashlib.sha256((root / name).read_bytes()).hexdigest()


def fmt(value, places: int = 6) -> str:
    """Verbatim rendering. None is undefined and is never filled."""
    if value is None:
        return UNDEFINED
    if isinstance(value, float):
        return f"{value:.{places}f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def signed_gap(empirical, mean_probability):
    """Plan §3.1: `empirical - mean`. Positive means under-confident."""
    if empirical is None or mean_probability is None:
        return None
    return float(empirical) - float(mean_probability)


def bin_rows(reliability: dict) -> list[dict]:
    return list(reliability.get("bins") or ())


def degeneracy(reliability: dict) -> dict:
    """Plan §3.3. Defined is not meaningful; report the shape of the mass."""
    counts = [int(entry.get("count", 0)) for entry in bin_rows(reliability)]
    return {
        "bin_count": len(counts),
        "empty_bins": sum(1 for value in counts if value == 0),
        "sparse_bins": sum(1 for value in counts if 0 < value < SPARSE_BIN_ROWS),
        "smallest": min(counts) if counts else None,
        "largest": max(counts) if counts else None,
    }


def bin_table(out: list, reliability: dict) -> None:
    out.append("| Bin | Rows | Mean probability | Empirical positive fraction | Gap |")
    out.append("|---|---:|---:|---:|---:|")
    for index, entry in enumerate(bin_rows(reliability)):
        gap = signed_gap(
            entry.get("empirical_positive_fraction"), entry.get("mean_probability")
        )
        out.append(
            f"| {index} | {fmt(entry.get('count'))} "
            f"| {fmt(entry.get('mean_probability'))} "
            f"| {fmt(entry.get('empirical_positive_fraction'))} "
            f"| {fmt(gap)} |"
        )
    out.append("")


def degeneracy_table(out: list, calibration: dict) -> None:
    out.append("| Family | Binning | Bins | Empty | Sparse | Smallest | Largest |")
    out.append("|---|---|---:|---:|---:|---:|---:|")
    for family in FAMILY_ORDER:
        block = calibration["families"][family]
        for binning in ("reliability_equal_width", "reliability_equal_mass"):
            shape = degeneracy(block[binning])
            label = binning.removeprefix("reliability_").replace("_", "-")
            out.append(
                f"| `{family}` | {label} | {shape['bin_count']} "
                f"| {shape['empty_bins']} | {shape['sparse_bins']} "
                f"| {fmt(shape['smallest'])} | {fmt(shape['largest'])} |"
            )
    out.append("")


def build_report(root: pathlib.Path, *, git_sha: str = "unrecorded") -> str:
    calibration = load(root, "U1_OOF_CALIBRATION.json")
    selection = load(root, "U1_FAMILY_SELECTION.json")
    oof = load(root, "U1_OOF_RESULT.json")
    families = calibration["families"]

    out: list[str] = []
    w = out.append

    w("# U1 Calibration Reliability — Descriptive Report, V1")
    w("")
    w("**Step 3 of `docs/U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md`: the")
    w("first read of the per-bin reliability evidence.** The reporting shape was")
    w("fixed in §3 and §4 of that plan before any bin was visible, and nothing in")
    w("the plan was changed after the values became readable.")
    w("")
    w("Every number is read verbatim from a promoted artifact, with the single")
    w("exception plan §3.1 names and authorizes in advance: the signed gap")
    w("`empirical − mean`, arithmetic on two published numbers. No `.npz` store")
    w("was opened and no metric was recomputed.")
    w("")
    w("**This report changes nothing.** The U1 retention decision is frozen and")
    w("was taken on evidence that already included these bins' summary. Reading")
    w("the bins adds description, not support. The retention remains **split**:")
    w("Platt calibration retained, the selective router at `c_star = 0.90` **not**")
    w("retained.")
    w("")
    w("---")
    w("")
    w("## 1. Provenance")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Run | `{_run_label(root)}` |")
    w(f"| Selected family | `{selection.get('selected_family')}` |")
    w(f"| Selection criterion | `{selection.get('criterion')}` |")
    w(f"| Out-of-fold | `{str(calibration.get('out_of_fold')).lower()}` |")
    w(f"| Development evidence | `{str(oof.get('development_evidence')).lower()}` |")
    optimistic = str(oof.get("development_optimistic")).lower()
    w(f"| Development optimistic | `{optimistic}` |")
    w(f"| `test_accessed` | `{str(oof.get('test_accessed')).lower()}` |")
    w(f"| `sealed_test_state` | `{oof.get('sealed_test_state')}` |")
    w(f"| Generated at commit | `{git_sha}` |")
    w("")
    for name in ARTIFACTS:
        w(f"- `{name}` — SHA-256 `{digest(root, name)}`")
    w("")
    note = oof.get("development_optimism_note")
    if note:
        w(f"> {note}")
        w("")
    w("---")
    w("")
    w("## 2. Family-level scalars — all three families")
    w("")
    w("Restated from the retention decision as context for the bins, not as a new")
    w("finding. The uncalibrated baseline is the raw score treated as a")
    w("probability, which is what makes the comparison answerable.")
    w("")
    w("| Family | NLL | Brier | ECE equal-width | ECE equal-mass | Rows |")
    w("|---|---:|---:|---:|---:|---:|")
    for family in FAMILY_ORDER:
        block = families[family]
        w(
            f"| `{family}` | {fmt(block.get('negative_log_likelihood'))} "
            f"| {fmt(block.get('brier'))} "
            f"| {fmt(block['reliability_equal_width'].get(ECE_KEY))} "
            f"| {fmt(block['reliability_equal_mass'].get(ECE_KEY))} "
            f"| {fmt(block.get('row_count'))} |"
        )
    w("")
    w("**Improved ECE alone is not a success criterion.** The U1 protocol §16 says")
    w("so, and the family selection used NLL, not ECE: `ece_used` is")
    w(f"`{str(selection.get('ece_used')).lower()}` and `brier_used` is")
    w(f"`{str(selection.get('brier_used')).lower()}` in the frozen decision.")
    w("")
    w("---")
    w("")
    w("## 3. Per-bin reliability — the retained calibrator")
    w("")
    w(f"`{RETAINED}`. Fifteen bins per binning, constructed exactly as U1 protocol")
    w("§10.3 froze in advance. Gap is `empirical − mean`; **positive means the")
    w("observed positive rate exceeded the predicted probability**, i.e. the")
    w("calibrator was under-confident in that bin.")
    w("")
    w("### 3.1 Equal-width")
    w("")
    bin_table(out, families[RETAINED]["reliability_equal_width"])
    w("### 3.2 Equal-mass")
    w("")
    bin_table(out, families[RETAINED]["reliability_equal_mass"])
    w("---")
    w("")
    w("## 4. Per-bin reliability — the uncalibrated baseline")
    w("")
    w("Plan §4 rule 3: a calibration number without its baseline is not")
    w("interpretable, so the baseline is reported at the same resolution.")
    w("")
    w("### 4.1 Equal-width")
    w("")
    bin_table(out, families[BASELINE]["reliability_equal_width"])
    w("### 4.2 Equal-mass")
    w("")
    bin_table(out, families[BASELINE]["reliability_equal_mass"])
    w("---")
    w("")
    w("## 5. Bin degeneracy — plan §3.3")
    w("")
    w("An ECE whose weight sits in two bins says something different from one")
    w("spread across fifteen. Bins below")
    w(f"{SPARSE_BIN_ROWS} rows are counted as sparse: their empirical positive")
    w("fraction is reported, and it should not be read as an estimate.")
    w("")
    degeneracy_table(out, calibration)
    w("This is the U1 analogue of the T1 lesson that **defined is not meaningful**.")
    w("")
    w("---")
    w("")
    w("## 6. What this report does not support")
    w("")
    w("- **Nothing about TEST.** `test_accessed` is false and the B4/neural sealed")
    w("  test is unopened.")
    w("- **No generalisation claim.** Development, out-of-fold, one cohort, and the")
    w("  artifact records its own optimism. Subject-disjoint folds control for")
    w("  subject leakage within LTSTDB and say nothing about another cohort.")
    w("- **No clinical safety claim.** U1 protocol §16 forbids it explicitly.")
    w("- **No routing claim.** The selective router is not retained. Reliability of")
    w("  a probability and the behaviour of a policy built on it are different")
    w("  questions.")
    w("- **No support for the retention decision.** It was already taken on")
    w("  evidence including these bins' summary.")
    w("- **No T2 calibration language.** T2 scores carry")
    w("  `score_is_calibrated_probability: false`; a bounded sigmoid is not a")
    w("  probability, and nothing in this report may be attached to one.")
    w("")
    w("## 7. Excluded analyses — plan §3.5")
    w("")
    w("Not done, and not to be done as a follow-up without a separate decision:")
    w("")
    w("- Re-deriving any metric from the `.npz` evidence stores")
    w("- Any re-binning, alternative bin count or third binning scheme")
    w("- Any recalibration, refit, temperature search or clamp-delta variation")
    w("- Any routing, coverage or `c_star` analysis")
    w("- Any per-subject reliability decomposition")
    w("- Any comparison to B0–B3, B4 or T2 scores")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    destination = pathlib.Path(argv[1])
    destination.write_text(build_report(RUN), encoding="utf-8")
    print(f"wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
