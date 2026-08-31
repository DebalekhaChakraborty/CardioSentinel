"""Emit the U1 calibration reliability report per the approved plan.

Reads `docs/experiments/u1/U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md` §3 as its
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
import subprocess
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


def _git_sha() -> str:
    """Plan §3.4 requires the commit the report was generated at.

    Best-effort and never fatal, matching the T2 and W1 generators: a report
    that fails to render because `git` is unavailable is worse than one that
    records the commit as unrecorded.
    """
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORY_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 - provenance is best-effort, never fatal
        return "unrecorded"


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


def fmt_exact(value) -> str:
    """Verbatim for values `fmt` would flatten -- `clamp_delta` is 1e-07."""
    if value is None:
        return UNDEFINED
    return repr(value)


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


def _contiguous(indices: list[int]) -> str:
    """`[0, 1, 2]` -> `0-2`; a gap in the run is spelled out."""
    if not indices:
        return "none"
    runs, start, previous = [], indices[0], indices[0]
    for value in indices[1:]:
        if value != previous + 1:
            runs.append((start, previous))
            start = value
        previous = value
    runs.append((start, previous))
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)


def direction_note(reliability: dict) -> dict:
    """Plan §3.1 fixed the sign convention so direction is reported, not left
    to the reader to subtract. This reads the sign of the authorized gap; it
    introduces no new quantity."""
    entries = bin_rows(reliability)
    gaps = [
        (
            index,
            signed_gap(
                entry.get("empirical_positive_fraction"), entry.get("mean_probability")
            ),
            int(entry.get("count", 0)),
        )
        for index, entry in enumerate(entries)
    ]
    defined = [(i, g, c) for i, g, c in gaps if g is not None]
    positive = [i for i, g, _ in defined if g > 0]
    negative = [i for i, g, _ in defined if g < 0]
    widest = max(defined, key=lambda row: abs(row[1]), default=None)
    heaviest = max(gaps, key=lambda row: row[2], default=None)
    counts = [count for _, _, count in gaps]
    return {
        "positive": _contiguous(positive),
        "negative": _contiguous(negative),
        "widest_index": None if widest is None else widest[0],
        "widest_gap": None if widest is None else widest[1],
        "widest_rows": None if widest is None else widest[2],
        "heaviest_index": None if heaviest is None else heaviest[0],
        "heaviest_rows": None if heaviest is None else heaviest[2],
        "lightest_rows": min(counts) if counts else None,
    }


def direction_paragraph(out: list, reliability: dict, row_count) -> None:
    note = direction_note(reliability)
    out.append(
        f"Gap is positive in bin(s) **{note['positive']}** — observed positive "
        f"rate above predicted probability — and negative in bin(s) "
        f"**{note['negative']}**. The widest gap is {fmt(note['widest_gap'])} at "
        f"bin {note['widest_index']}, which carries {fmt(note['widest_rows'])} "
        f"rows. Bin counts run from {fmt(note['lightest_rows'])} to "
        f"{fmt(note['heaviest_rows'])} across the family's {fmt(row_count)} "
        f"rows, the heaviest being bin {note['heaviest_index']}."
    )
    out.append("")


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
    w("Restated from the retention decision as context for the bins, not as a")
    w("new finding. The uncalibrated baseline is the raw score treated as a")
    w("probability; it is what the question \"did calibration help?\" is asked")
    w("against, subject to the qualification recorded immediately below.")
    w("")
    w(
        "| Family | NLL | Brier | ECE equal-width | ECE equal-mass | Rows "
        "| `clamp_delta` | `out_of_fold` |"
    )
    w("|---|---:|---:|---:|---:|---:|---:|---|")
    for family in FAMILY_ORDER:
        block = families[family]
        w(
            f"| `{family}` | {fmt(block.get('negative_log_likelihood'))} "
            f"| {fmt(block.get('brier'))} "
            f"| {fmt(block['reliability_equal_width'].get(ECE_KEY))} "
            f"| {fmt(block['reliability_equal_mass'].get(ECE_KEY))} "
            f"| {fmt(block.get('row_count'))} "
            f"| {fmt_exact(block.get('clamp_delta'))} "
            f"| `{str(block.get('out_of_fold')).lower()}` |"
        )
    w("")
    w("**The baseline row is not a matched comparison, and the retention")
    w("decision already said so.** `U1_OOF_CALIBRATION.json` carries the")
    w("qualification in the artifact itself:")
    w("")
    semantics = families[BASELINE].get("baseline_semantics")
    w(f"> `uncalibrated_baseline.baseline_semantics` — {semantics}")
    w("")
    w(
        "Its `out_of_fold` and `development_evidence` are both "
        f"`{str(families[BASELINE].get('out_of_fold')).lower()}`, against "
        f"`{str(families[RETAINED].get('out_of_fold')).lower()}` for the "
        "retained family. Every comparison below inherits that asymmetry."
    )
    w("")
    w(
        "The temperature-only row is **approximate**: `comparator_is_approximate` "
        f"is `{str(calibration.get('comparator_is_approximate')).lower()}` and "
        "`true_logit_temperature_scaling_performed` is "
        f"`{str(calibration.get('true_logit_temperature_scaling_performed')).lower()}`,"
    )
    w("because true logits were never persisted. Its two ECEs are identical for")
    w("the reason the retention decision recorded: it over-predicts in every bin")
    w("of both binnings, so both collapse to the same global mean gap.")
    w("")
    w("### 2.1 Protocol §16 condition 2 — restated, not re-decided")
    w("")
    w("Plan §3.2 requires the prespecified condition to appear beside the bins as")
    w("context. U1 protocol §16 condition 2 is that **pooled OOF Brier and NLL")
    w("are both lower than the uncalibrated baseline**.")
    w("")
    retained_block = families[RETAINED]
    baseline_block = families[BASELINE]
    w("| Scalar | Retained Platt | Uncalibrated baseline | Condition 2 |")
    w("|---|---:|---:|---|")
    for label, key in (
        ("NLL", "negative_log_likelihood"),
        ("Brier", "brier"),
    ):
        left = retained_block.get(key)
        right = baseline_block.get(key)
        holds = UNDEFINED if left is None or right is None else (
            "lower" if float(left) < float(right) else "not lower"
        )
        w(f"| {label} | {fmt(left)} | {fmt(right)} | {holds} |")
    w("")
    w("Both scalars are already published in")
    w("`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` §3, and the human")
    w("retention decision recorded in its §2 was taken with them in hand:")
    w("**calibration retained, the selective router at `c_star = 0.90` not")
    w("retained.** This table restates that record. It does not re-decide it, and")
    w("the baseline asymmetry noted above applies to both rows.")
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
    retained_rows = families[RETAINED].get("row_count")
    w("### 3.1 Equal-width")
    w("")
    bin_table(out, families[RETAINED]["reliability_equal_width"])
    direction_paragraph(
        out, families[RETAINED]["reliability_equal_width"], retained_rows
    )
    w("### 3.2 Equal-mass")
    w("")
    bin_table(out, families[RETAINED]["reliability_equal_mass"])
    direction_paragraph(
        out, families[RETAINED]["reliability_equal_mass"], retained_rows
    )
    w("---")
    w("")
    w("## 4. Per-bin reliability — the uncalibrated baseline")
    w("")
    w("Plan §4 rule 3: a calibration number without its baseline is not")
    w("interpretable, so the baseline is reported at the same resolution.")
    w("")
    baseline_rows = families[BASELINE].get("row_count")
    w("### 4.1 Equal-width")
    w("")
    bin_table(out, families[BASELINE]["reliability_equal_width"])
    direction_paragraph(
        out, families[BASELINE]["reliability_equal_width"], baseline_rows
    )
    w("### 4.2 Equal-mass")
    w("")
    bin_table(out, families[BASELINE]["reliability_equal_mass"])
    direction_paragraph(
        out, families[BASELINE]["reliability_equal_mass"], baseline_rows
    )
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
    w("## 6. A limitation of the shape this plan fixed")
    w("")
    w("Plan §5 step 4: if the shape fixed in advance turns out to be wrong, that")
    w("is recorded here as a limitation, not repaired by editing the plan. The")
    w("plan is not modified.")
    w("")
    equal_width = degeneracy(families[RETAINED]["reliability_equal_width"])
    w(
        "Plan §3.3 chose four degeneracy statistics — empty bins, bins under "
        f"{SPARSE_BIN_ROWS} rows, smallest and largest — to surface the fact "
        "that equal-width binning on a low-prevalence detector score "
        "concentrates mass at one end. On the retained calibrator's equal-width "
        f"binning those statistics read {equal_width['empty_bins']} empty and "
        f"{equal_width['sparse_bins']} sparse, which on its own reads as a "
        "healthy curve. The concentration is visible only in the smallest and "
        f"largest columns: {fmt(equal_width['smallest'])} rows against "
        f"{fmt(equal_width['largest'])}."
    )
    w("")
    w("**A count of sparse bins is the wrong summary for this evidence.** The")
    w("share of mass in the heaviest bin would have been the right one, and the")
    w("plan did not name it. It is not added here: choosing a statistic after")
    w("seeing the values is the error the plan exists to prevent, and the two")
    w("numbers a reader needs are both already in the table above. This is")
    w("recorded so a future plan names the share in advance.")
    w("")
    w("---")
    w("")
    w("## 7. What this report does not support")
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
    w("## 8. Excluded analyses — plan §3.5")
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
    destination.write_text(
        build_report(RUN, git_sha=_git_sha()), encoding="utf-8"
    )
    print(f"wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
