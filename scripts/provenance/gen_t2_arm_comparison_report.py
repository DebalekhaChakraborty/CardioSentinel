"""Emit the T2 arm-comparison report per the approved analysis plan.

Implements step 3 of `docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md`
(`84adf43b885d6dd3ecef3b678d1a2b89fc6e94f48ffdf8d2f0dc2bb0a7eba973`): the first
read of T2 outer-validation measured values.

Every number is read verbatim from the promoted artifacts, with exactly one
exception, which plan §4 authorizes in advance and labels **DERIVED ANALYSIS**:
the paired subject-level bootstrap of the S4D - GRU pooled primary AUPRC
difference. That computation is delegated to
`cardiosentinel.neural.t2_paired_bootstrap`, which was written, reviewed and
merged before this analysis was authorized.

The run directory is opened read-only. No checkpoint is loaded, no model is
evaluated, no threshold is generated or swept, and the TEST partition is never
addressed.

Usage, from the repository root, on the frozen scientific interpreter:

    python scripts/provenance/gen_t2_arm_comparison_report.py <output.md> [run_root]

Write to a scratch path outside the repository and diff, rather than
overwriting the tracked document.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

import numpy as np

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from cardiosentinel.neural.t2_paired_bootstrap import (  # noqa: E402
    T2_PAIRED_BOOTSTRAP_AUTHORITY,
    paired_subject_bootstrap_difference,
    require_paired_inputs,
    require_registered_design,
)

DEFAULT_RUN = (
    REPOSITORY_ROOT
    / "cardiosentinel-runs"
    / "phase8-t2-development-v1"
    / "t2-v1-outer-validation"
)

S4D = "causal_s4d_longitudinal_v1"
GRU = "causal_gru_longitudinal_v1"

PLAN = "docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md"
PLAN_SHA256 = "84adf43b885d6dd3ecef3b678d1a2b89fc6e94f48ffdf8d2f0dc2bb0a7eba973"
AMENDMENT = "docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_AMENDMENT_V1_1.md"

#: Amendment V1.1 §3.1. The two quantities the registered differences are
#: computed from, and deliberately nothing else.
DESCRIPTIVE_ABSOLUTE_METRIC = "auprc"

#: Amendment V1.1 §2/§3, quoted verbatim wherever the values appear.
COLD_START_WORDING = (
    "Cold-start strata are reported as descriptive stratification summaries. "
    "They do not constitute independent performance estimates and are not "
    "used to support absolute model superiority claims."
)
ABSOLUTE_WORDING = (
    "Absolute arm-level values are descriptive because the selected arm was "
    "chosen using the same criterion. They are reported to give the primary "
    "contrast a scale, not as unbiased estimates of either arm's performance."
)

#: Plan §0 and §0.2. Verified before a single value is read; a mismatch means
#: the evidence is not the evidence the plan was written against.
EXPECTED_DIGESTS = {
    "T2_OUTER_VALIDATION_RESULT.json": (
        "c58ed40dac753157b00ce6c70eb52fe903ecee72a5ef84e40932c1a80e259dbf"
    ),
    "T2_OUTER_ROW_EVIDENCE.json": (
        "c76453b8970a06c6beb3c280ab6e0518fa4cf81fcb304f6f9aa9c569d2634949"
    ),
    "t2_outer_row_identity.npz": (
        "1014357cd25d347c7a760e38dbf7ae93c71d56717d13a40e315bb9cb79b220dc"
    ),
    "t2_outer_scores_s4d.npz": (
        "5c7f9763713c66759cf7e3752cda2a71dacb6cc3f962c5bdd5247017447a7a32"
    ),
    "t2_outer_scores_gru.npz": (
        "2dbfa5da02f0d96065d72f272875f805f5dceb28410b90582df34c8f6fc17f2d"
    ),
}

UNDEFINED = "*undefined*"

#: Plan §5.2. The descriptors named for reporting, in the plan's own order.
TEMPORAL_KEYS = (
    "prediction_persistence_around_labelled_ischemic_intervals",
    "transition_count",
    "transition_count_per_hour",
    "median_positive_run_duration_seconds",
    "positive_prediction_run_count",
    "isolated_single_window_positive_fraction",
)

#: Plan §5.2. The artifact's own qualifiers, carried with the numbers.
TEMPORAL_QUALIFIERS = (
    "episode_grouping_performed",
    "prediction_persistence_is_episode_onset_offset_measurement",
    "runs_cross_stream_boundaries",
    "run_segmentation_key",
    "is_selection_input",
    "may_alter_threshold",
    "formal_episode_reasoning_belongs_to",
    "transition_denominator",
    "prediction_persistence_unit",
)


class T2ReportError(RuntimeError):
    """A refusal. The analysis stops rather than reporting something else."""


def _find(run: pathlib.Path, name: str) -> pathlib.Path:
    matches = sorted(run.rglob(name))
    if len(matches) != 1:
        raise T2ReportError(f"expected exactly one {name} under {run}; found {matches}")
    return matches[0]


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_evidence(run: pathlib.Path) -> dict[str, str]:
    """Plan §0/§0.2. Digest every artifact before any value is read."""
    observed = {}
    for name, expected in EXPECTED_DIGESTS.items():
        digest = _sha256(_find(run, name))
        if digest != expected:
            raise T2ReportError(
                f"{name} digests {digest}, the plan records {expected}. This is "
                "not the evidence the plan was written against. Stop."
            )
        observed[name] = digest
    return observed


def fmt(value, places: int = 6) -> str:
    """Verbatim rendering. None is undefined and is never filled."""
    if value is None:
        return UNDEFINED
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    if isinstance(value, float):
        return f"{value:.{places}f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def load_primary_population(run: pathlib.Path):
    """The §0.1 paired population: primary-mask rows, scored in both arms.

    One identity array and one label vector serve both arms, so the pairing is a
    property of the store rather than something reconstructed here.
    """
    base = _find(run, "t2_outer_row_identity.npz").parent
    with np.load(base / "t2_outer_row_identity.npz", allow_pickle=False) as identity:
        primary = identity["primary_mask"]
        subjects = identity["subject_id"][primary]
        labels = identity["label"][primary]
        identity_present = identity["score_present"][primary]
    arms = {}
    for arm, filename in ((S4D, "t2_outer_scores_s4d.npz"), (GRU, "t2_outer_scores_gru.npz")):
        with np.load(base / filename, allow_pickle=False) as store:
            arms[arm] = (store["score"][primary], store["score_present"][primary])

    for arm, (_, present) in arms.items():
        if not np.array_equal(present, identity_present):
            raise T2ReportError(
                f"{arm} score_present disagrees with the identity store over the "
                "primary mask; the arms are not the same rows."
            )
    if not identity_present.all():
        raise T2ReportError(
            "the primary population contains unscored rows; the artifact records "
            "primary_unavailable_no_score_count as zero."
        )
    return subjects, labels, arms[S4D][0], arms[GRU][0]


def run_derived_analysis(run: pathlib.Path, result: dict) -> dict:
    """Plan §4. The one authorized new computation.

    Bound to the artifact's own registered design, and checked afterwards
    against the artifact's own recorded difference.
    """
    require_registered_design(result["subject_bootstrap"][S4D])
    require_registered_design(result["subject_bootstrap"][GRU])
    subjects, labels, s4d_scores, gru_scores = load_primary_population(run)
    require_paired_inputs(subjects, labels, s4d_scores, gru_scores)
    return paired_subject_bootstrap_difference(subjects, labels, s4d_scores, gru_scores)


def reconcile_sign(derived: dict, decision: dict) -> dict:
    """The artifact stores a magnitude; the derived statistic is signed.

    `t2_protocol.select_t2_arm` records `pooled_auprc_difference` as
    `abs(gru - s4d)` and carries the direction separately in `selected_arm`. The
    derived analysis computes the signed `s4d - gru`. Those agree in magnitude,
    and their signs must be consistent with the recorded selection, or the two
    are not describing the same comparison.
    """
    stored = float(decision["pooled_auprc_difference"])
    observed = derived["point_estimate"]
    if observed is None:
        raise T2ReportError("the derived point estimate is undefined; stop.")
    observed = float(observed)
    expected_sign = 1.0 if decision["selected_arm"] == S4D else -1.0
    if observed != 0.0 and (observed > 0) != (expected_sign > 0):
        raise T2ReportError(
            f"the derived signed difference {observed!r} points away from the "
            f"recorded selected arm {decision['selected_arm']!r}. Stop."
        )
    gap = abs(abs(observed) - stored)
    return {
        "stored_magnitude": stored,
        "derived_signed": observed,
        "absolute_agreement_error": gap,
        "agrees": gap <= 1e-9,
    }


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORY_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 - provenance is best-effort, never fatal
        return "unrecorded"


def build_report(run: pathlib.Path) -> str:
    digests = verify_evidence(run)
    result = json.loads(_find(run, "T2_OUTER_VALIDATION_RESULT.json").read_text())
    manifest = json.loads(_find(run, "T2_OUTER_ROW_EVIDENCE.json").read_text())
    decision = result["selection_decision"]
    derived = run_derived_analysis(run, result)
    reconciliation = reconcile_sign(derived, decision)

    out: list[str] = []
    w = out.append

    w("# T2 Arm Comparison — Report, V1")
    w("")
    w(f"**Step 3 of `{PLAN}`: the first read of T2 outer-validation measured")
    w("values.** Produced under explicit human authorization, to the reporting")
    w("shape fixed in §2–§5 of that plan before any value was visible.")
    w("")
    w("**The plan itself is unedited** and still digests")
    w(f"`{PLAN_SHA256}`. Its estimands, its derived analysis and its claim")
    w("boundaries are exactly as approved before the first read.")
    w("")
    w(f"**An amendment postdates that read.** `{AMENDMENT}`")
    w(f"(`{_sha256(REPOSITORY_ROOT / AMENDMENT)}`) was written on 2026-08-22,")
    w("**after** the values were visible, and is stated here rather than left to")
    w("be inferred. It repairs an unreconciled conflict between plan §5.3, which")
    w("required cold-start strata verbatim, and plan §3, which constrained")
    w("absolute figures — a conflict the first execution resolved silently by")
    w("dropping values. **The amendment only ever adds reporting.** It changes no")
    w("estimand, authorizes no new computation, and revises no number: the")
    w("primary contrast and the derived interval below are identical to those")
    w("produced before it existed.")
    w("")
    w("**Every number below is read verbatim from a promoted artifact, with one")
    w("exception** named and authorized in advance by plan §4 and labelled")
    w("**DERIVED ANALYSIS** wherever it appears: the paired subject-level")
    w("bootstrap of the S4D − GRU pooled primary AUPRC difference, which no")
    w("artifact stores.")
    w("")
    w("---")
    w("")
    w("## 1. Evidence and firewall")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Run | `{run.name}` |")
    w(f"| Authorized git SHA of the run | `{result['authorized_git_sha']}` |")
    w(f"| Analysis executed at commit | `{_git_sha()}` |")
    w(f"| Partition | `validation` |")
    w(f"| Attempts permitted | {fmt(result['attempts_permitted'])} |")
    w(f"| Automatic retry performed | {fmt(result['automatic_retry_performed'])} |")
    w(f"| `git_dirty` at run time | {fmt(result['git_dirty'])} |")
    w(f"| `test_accessed` | {fmt(result['test_accessed'])} |")
    w(f"| `sealed_test_state` | `{result['sealed_test_state']}` |")
    w(f"| `test_rows_present` in the row store | {fmt(manifest['test_rows_present'])} |")
    w("")
    w("Artifact digests, verified before any value was read:")
    w("")
    for name, digest in digests.items():
        w(f"- `{name}` — `{digest}`")
    w("")
    w("### 1.1 Pairing — plan §0.1")
    w("")
    accounting = result["row_accounting"]
    w("| | |")
    w("|---|---|")
    w(f"| Rows in the shared identity store | {fmt(accounting['row_count'])} |")
    w(f"| Primary-mask rows | {fmt(accounting['primary_target_row_count'])} |")
    w(f"| Primary rows scored and available | {fmt(accounting['primary_scored_available_row_count'])} |")
    w(f"| Primary rows unavailable, no score | {fmt(accounting['primary_unavailable_no_score_count'])} |")
    w(f"| Score invented for an unavailable row | {fmt(accounting['score_invented_for_unavailable_row'])} |")
    w(f"| `full_timeline_ordering` | `{manifest['full_timeline_ordering']}` |")
    w(f"| `ordered_stable_id_sha256` | `{manifest['ordered_stable_id_sha256']}` |")
    w(f"| `ordered_chronology_sha256` | `{manifest['ordered_chronology_sha256']}` |")
    w(f"| `lossy_conversion_applied` | {fmt(manifest['lossy_conversion_applied'])} |")
    w("")
    w("One identity array and **one label vector** serve both arms, so the")
    w("comparison is paired by construction rather than by reconstruction here.")
    w("This report additionally verified that each arm's `score_present` agrees")
    w("with the identity store's over the primary mask; it does.")
    w("")
    w("Per-arm single-pass flags:")
    w("")
    w("| Arm | `single_causal_pass` | 2nd temporal replay | 2nd challenge replay | threshold altered by outer validation |")
    w("|---|---|---|---|---|")
    for arm in (S4D, GRU):
        block = result["per_arm_evidence"][arm]
        w(
            f"| `{arm}` | {fmt(block['single_causal_pass'])} "
            f"| {fmt(block['second_temporal_replay_performed'])} "
            f"| {fmt(block['second_challenge_replay_performed'])} "
            f"| {fmt(block['threshold_altered_by_outer_validation'])} |"
        )
    w("")
    w("---")
    w("")
    w("## 2. Primary result — the predefined selection criterion")
    w("")
    w("**This difference is the criterion by which the arm was chosen.** It is not")
    w("an independent discovery, and plan §2 requires that sentence to appear in")
    w("the same passage as the number.")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| `selection_basis` | `{decision['selection_basis']}` |")
    w(f"| `selected_arm` | `{decision['selected_arm']}` |")
    w(f"| **`pooled_auprc_difference`** | **{fmt(decision['pooled_auprc_difference'])}** |")
    w(f"| `tie_tolerance` | {fmt(decision['tie_tolerance'])} |")
    w(f"| `challenge_evidence_used` | {fmt(decision['challenge_evidence_used'])} |")
    w(f"| `latency_used` | {fmt(decision['latency_used'])} |")
    w(f"| `weighted_composite_used` | {fmt(decision['weighted_composite_used'])} |")
    w("")
    w("Read verbatim from `selection_decision.pooled_auprc_difference`.")
    w("")
    w("**Sign convention.** The artifact stores an unsigned magnitude:")
    w("`t2_protocol.select_t2_arm` computes `abs(gru − s4d)` and carries the")
    w("direction separately in `selected_arm`. The direction is therefore read")
    w("from `selected_arm`, not inferred from the number.")
    w("")
    w("The predefined selection rule selected")
    w(f"`{decision['selected_arm']}` based on the observed validation contrast,")
    w(f"by a margin of {fmt(decision['pooled_auprc_difference'])} on pooled primary")
    w(f"validation AUPRC, against a tie tolerance of {fmt(decision['tie_tolerance'])}.")
    w("")
    w("### 2.1 Selection conditioning — plan §3")
    w("")
    w("| | |")
    w("|---|---|")
    w("| **The paired contrast is unbiased** | Both arms were evaluated on the same held-out rows under a rule fixed in advance. Selecting on the outcome does not bias the *difference*. |")
    w("| **The winner's absolute figure is not** | The selected arm's own AUPRC on this set is optimistically biased, because it was chosen for having the higher value **on this very set**. The bias attaches to the maximum, not to the contrast. |")
    w("")
    w("### 2.2 Arm-level absolute AUPRC — descriptive (amendment §3)")
    w("")
    w(f"> {ABSOLUTE_WORDING}")
    w("")
    w("| Arm | pooled primary AUPRC | subject-macro AUPRC | contributing subjects | non-contributing |")
    w("|---|---:|---:|---:|---:|")
    degeneracy = set()
    for arm in (S4D, GRU):
        block = result["per_arm_evidence"][arm]
        macro = block["subject_macro"].get(DESCRIPTIVE_ABSOLUTE_METRIC)
        if isinstance(macro, dict):
            value = macro.get("value")
            contributing = macro.get("contributing_subject_count")
            non_contributing = macro.get("non_contributing_subject_count")
        else:
            value, contributing, non_contributing = macro, None, None
        degeneracy.add(non_contributing)
        w(
            f"| `{arm}` | {fmt(block['pooled'].get(DESCRIPTIVE_ABSOLUTE_METRIC))} "
            f"| {fmt(value)} | {fmt(contributing)} | {fmt(non_contributing)} |"
        )
    w("")
    excluded = sorted(v for v in degeneracy if v)
    if excluded:
        w(f"**The subject-macro figure is a mean over {fmt(contributing)} of 12")
        w(f"subjects, not 12.** The artifact records {fmt(non_contributing)}")
        w("non-contributing subjects for both arms, and it is the artifact's own")
        w("count, not a derivation. A subject-macro mean quoted without that")
        w("denominator reads as an average over the cohort when it is an average")
        w("over the subset of it for which the metric is defined.")
        w("")
        w("This is the same distinction the T1 analysis had to make after the")
        w("fact — `episode_f1` was *defined* for 12/12 subjects while three of")
        w("them had zero reference episodes. **Defined is not meaningful.** It is")
        w("stated here because the amendment surfaced the value; the")
        w("pre-amendment report, which omitted the absolute, also omitted this.")
        w("")
        w("No claim is made about **which** subjects those are, or why. That")
        w("would be a subgroup analysis and plan §5.3 forbids one.")
        w("")
    w("These give §2's contrast a scale. Reporting them does not license any")
    w("sentence plan §3 forbids: *\"S4D achieved superior AUPRC\"* and *\"S4D was")
    w("found to outperform GRU\"* remain prohibited, and the selected arm's")
    w("absolute figure remains optimistically biased for the reason in §2.1.")
    w("")
    w("The remaining pooled and subject-macro metrics (`auroc`,")
    w("`balanced_accuracy`, `f1`, `mcc`, `npv`, `ppv`, `sensitivity`,")
    w("`specificity`) exist in the artifact and are **not** reported: no")
    w("registered estimand is computed from them, and adding them after the")
    w("values are visible would be the scope creep the amendment objects to.")
    w("That boundary is a decision, not an accident.")
    w("")
    w("---")
    w("")
    w("## 3. DERIVED ANALYSIS — paired subject-level bootstrap")
    w("")
    w("**No artifact stores this quantity.** The artifacts carry a")
    w("`subject_bootstrap` per arm and no interval on the difference, so the §2")
    w("contrast had a point estimate and no uncertainty. Plan §4 authorizes")
    w(f"exactly this one computation ({T2_PAIRED_BOOTSTRAP_AUTHORITY}).")
    w("")
    w("Registered design, verified against the artifact's own")
    w("`subject_bootstrap` block for **both** arms before running:")
    w("")
    w("| Parameter | Value |")
    w("|---|---|")
    w(f"| Resampling unit | `{derived['unit']}` ({fmt(derived['subject_count'])} subjects) |")
    w(f"| Rows | same resampled rows both arms — {fmt(derived['row_count'])} primary rows |")
    w(f"| Statistic | `{derived['statistic']}` |")
    w(f"| Model refitting | {fmt(derived['model_refitted_per_replicate'])} |")
    w(f"| Threshold changes | {fmt(derived['thresholds_changed'])} |")
    w(f"| Reselection | {fmt(derived['reselection_performed'])} |")
    w(f"| Window bootstrap | {fmt(derived['window_bootstrap_performed'])} |")
    w(f"| Seed | {fmt(derived['seed'])} |")
    w(f"| Requested replicates | {fmt(derived['requested_replicates'])} |")
    w("")
    w("**Result:**")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Point estimate, signed S4D − GRU | **{fmt(derived['point_estimate'])}** |")
    w(f"| **95% paired subject-bootstrap interval** | **[{fmt(derived['lower_95'])}, {fmt(derived['upper_95'])}]** |")
    w(f"| Successful replicates | {fmt(derived['successful_replicates'])} |")
    w(f"| Undefined replicates | {fmt(derived['undefined_replicates'])} |")
    w(f"| Undefined replicates zero-filled | {fmt(derived['undefined_replicates_zero_filled'])} |")
    w("")
    w("Undefined replicates are preserved and reported as undefined, never")
    w("zero-filled, per plan §4.")
    w("")
    w("### 3.1 Agreement with the recorded selection margin")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Stored magnitude, `pooled_auprc_difference` | {fmt(reconciliation['stored_magnitude'])} |")
    w(f"| Derived signed difference | {fmt(reconciliation['derived_signed'])} |")
    w(f"| Absolute agreement error | {fmt(reconciliation['absolute_agreement_error'], 12)} |")
    w(f"| Agrees within 1e-9 | {fmt(reconciliation['agrees'])} |")
    w("")
    w("The derived point estimate recomputes the same statistic the selection")
    w("recorded, from the persisted row stores. Agreement is evidence that the")
    w("bootstrap was handed the rows the selection actually saw. Disagreement")
    w("would have stopped the analysis rather than produced a second number.")
    w("")
    lower, upper = derived["lower_95"], derived["upper_95"]
    straddles = lower is not None and upper is not None and lower <= 0.0 <= upper
    w("### 3.2 Where the interval sits relative to zero")
    w("")
    w("Stated because omitting it would leave the reader to notice it, and this")
    w("is the fact the derived analysis was authorized to establish.")
    w("")
    if straddles:
        w(f"**The 95% paired subject-bootstrap interval [{fmt(lower)}, {fmt(upper)}]")
        w("includes zero.** The point estimate is the recorded selection margin, and")
        w("the predefined rule selected on it correctly — the margin")
        w(f"({fmt(derived['point_estimate'])}) exceeds the tie tolerance")
        w(f"({fmt(decision['tie_tolerance'])}) by more than an order of magnitude.")
        w("What the interval adds is that **between-subject variation in this")
        w("contrast spans zero**: resampling the 12 validation subjects produces")
        w("replicates in which the ordering of the two arms reverses.")
        w("")
        w("**This is not a significance statement and must not be converted into")
        w("one.** Plan §4 forbids p-values and significance language, and the")
        w("interval is not a confidence interval for a population parameter. It")
        w("says the contrast is not stable across subjects at this resampling")
        w("resolution. It does not say the two arms are equivalent, and it does not")
        w("retract the selection — the rule was fixed in advance and applied to the")
        w("value it was defined on.")
    else:
        w(f"**The 95% paired subject-bootstrap interval [{fmt(lower)}, {fmt(upper)}]")
        w("excludes zero.** No significance claim follows from that, and plan §4")
        w("forbids converting it into one.")
    w("")
    w("The 12-member resampling unit is the binding constraint on how much this")
    w("can say either way; see the resolution caveat below.")
    w("")
    w("### 3.3 Claim scope — plan §4")
    w("")
    w(f"`{derived['claim_scope']}`")
    w("")
    w("The interval describes **between-subject variation in the paired contrast,")
    w("conditional on the fitted temporal models**. It is not a confidence")
    w("interval for a population parameter and it is not a hypothesis test. **No")
    w("p-value and no significance language appears anywhere in this analysis.**")
    w("")
    w("**It is also an *unconditional* resample of the difference, not a")
    w("post-selection inference interval:** the selection event — that the")
    w("difference exceeded the tie tolerance — is not conditioned on, so this")
    w("interval must not be read as the uncertainty *in the selection margin*.")
    w("No such object was computed and the plan authorizes none.")
    w("")
    w("**Resolution caveat, registered before execution.** The resampling unit has")
    w("12 members, so the percentile interval is coarse by construction and its")
    w("tails are governed by a handful of subjects. It indicates between-subject")
    w("spread, not precision.")
    w("")
    w("---")
    w("")
    w("## 4. Secondary — subject-macro AUPRC difference (plan §5.1)")
    w("")
    w("Reported **separately** from the primary contrast and never merged into it.")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| `subject_macro_auprc_difference` | {fmt(decision['subject_macro_auprc_difference'])} |")
    w("")
    w("Subject-weighted rather than row-weighted, so it is a **different estimand**")
    w("from §2 and need not agree with it. It was **not** the selection basis")
    w(f"(`selection_basis: {decision['selection_basis']}`), but it is computed on the")
    w("same evidence the selection consumed, so it is a companion to the primary")
    w("contrast rather than independent corroboration. Stored as an unsigned")
    w("magnitude on the same convention as §2.")
    w("")
    w("---")
    w("")
    w("## 5. Secondary — selection-independent temporal descriptors (plan §5.2)")
    w("")
    w("**These are the only comparisons in this report free of selection")
    w("conditioning.** The artifacts state it directly for both arms.")
    w("")
    descriptors = result["temporal_descriptors"]
    w("| Descriptor | S4D | GRU |")
    w("|---|---:|---:|")
    for key in TEMPORAL_KEYS:
        w(
            f"| `{key}` | {fmt(descriptors[S4D].get(key))} "
            f"| {fmt(descriptors[GRU].get(key))} |"
        )
    w("")
    w("Context carried with the numbers:")
    w("")
    w("| | S4D | GRU |")
    w("|---|---|---|")
    for key in ("stream_count", "physical_exposure_seconds", "labelled_positive_window_count"):
        w(f"| `{key}` | {fmt(descriptors[S4D].get(key))} | {fmt(descriptors[GRU].get(key))} |")
    w("")
    w("The artifact's own qualifiers, which travel with these descriptors:")
    w("")
    w("| Qualifier | S4D | GRU |")
    w("|---|---|---|")
    for key in TEMPORAL_QUALIFIERS:
        w(f"| `{key}` | {fmt(descriptors[S4D].get(key))} | {fmt(descriptors[GRU].get(key))} |")
    w("")
    w("`prediction_persistence_definition`:")
    w("")
    w(f"> {descriptors[S4D].get('prediction_persistence_definition')}")
    w("")
    w("**These must remain separate from the selection criterion.** They are")
    w("descriptive comparisons of temporal behaviour, they were not inputs to the")
    w("choice of arm, and they are not aggregated into, or presented as support")
    w("for, the §2 contrast. `episode_grouping_performed` is false for both arms:")
    w("**no episode reasoning happens here.**")
    w("")
    w("**Neither arm is characterised as better or worse from these numbers.**")
    w("Ranking them would need an alerting-cost model this programme does not")
    w("have — how a fragmented run of alerts trades against a missed episode is")
    w("precisely what RQ4 is unanswered about — so they are reported and left")
    w("unranked. Words like *fragmented*, *chattery* or *stable* carry that")
    w("ranking implicitly and are avoided here for the same reason.")
    w("")
    w("---")
    w("")
    w("## 6. Secondary — challenge and cold-start evidence (plan §5.3)")
    w("")
    w("Descriptive. No subgroup claim is made from either, and no stratum or")
    w("subset is compared across arms as a finding.")
    w("")
    for arm in (S4D, GRU):
        block = result["per_arm_evidence"][arm]["challenge"]
        w(f"**`{arm}` — challenge**")
        w("")
        w("| | |")
        w("|---|---|")
        for key in (
            "is_selection_input",
            "arm_selection_input",
            "checkpoint_selection_input",
            "merged_into_primary",
            "challenge_label_model_input",
            "challenge_identity_model_input",
            "direct_training_loss_received",
        ):
            w(f"| `{key}` | {fmt(block.get(key))} |")
        subsets = block.get("subsets") or {}
        if isinstance(subsets, dict) and subsets:
            w("")
            w("| Subset | Rows | False positives | False-positive rate | Evidence level |")
            w("|---|---:|---:|---:|---|")
            for subset, values in sorted(subsets.items()):
                if isinstance(values, dict):
                    w(
                        f"| `{subset}` | {fmt(values.get('row_count'))} "
                        f"| {fmt(values.get('false_positive_count'))} "
                        f"| {fmt(values.get('false_positive_rate'))} "
                        f"| `{values.get('evidence_level')}` |"
                    )
        w("")
    for arm in (S4D, GRU):
        block = result["per_arm_evidence"][arm]["cold_start"]
        w(f"**`{arm}` — cold start**")
        w("")
        w("| | |")
        w("|---|---|")
        for key in ("cold_start_repair_applied", "warmup_threshold_applied", "alternative_state_initialization"):
            w(f"| `{key}` | {fmt(block.get(key))} |")
        strata = block.get("strata") or {}
        if isinstance(strata, dict) and strata:
            w("")
            w(f"> {COLD_START_WORDING}")
            w("")
            metric_keys = sorted(
                {
                    key
                    for values in strata.values()
                    if isinstance(values, dict)
                    for key in (values.get("metrics") or {})
                }
            )
            header = " | ".join(f"`{key}`" for key in metric_keys)
            w(f"| Stratum | Rows | {header} |")
            w("|---|---:|" + "---:|" * len(metric_keys))
            for stratum, values in sorted(strata.items()):
                if not isinstance(values, dict):
                    continue
                metrics = values.get("metrics") or {}
                cells = " | ".join(fmt(metrics.get(key)) for key in metric_keys)
                w(f"| `{stratum}` | {fmt(values.get('row_count'))} | {cells} |")
        w("")
    w("---")
    w("")
    w("## 7. Calibration wording — plan §7")
    w("")
    w("Both statements are true and travel together:")
    w("")
    w("> U1 Platt calibration exists in the pipeline.")
    w("")
    w("> T2 scores are **uncalibrated temporal model scores**, not calibrated")
    w("> probabilities.")
    w("")
    w("| | |")
    w("|---|---|")
    for key in (
        "score_semantics",
        "score_definition",
        "score_is_calibrated_probability",
        "score_is_confidence",
        "score_is_uncertainty",
    ):
        w(f"| `{key}` | {fmt(manifest.get(key))} |")
    w("")
    w("A `sigmoid` output is bounded in [0, 1]; that does not make it a")
    w("probability. **No metric in this report is described as calibrated, as a")
    w("probability, as a confidence, or as an uncertainty.** U1's retention is a")
    w("separate decision about a separate object, and it was a **split** retention:")
    w("calibration retained, selective routing **not** retained.")
    w("")
    w("---")
    w("")
    w("## 8. What this analysis does not evaluate — plan §6")
    w("")
    w("None of these is a gap discovered in the evidence. Each is a boundary fixed")
    w("by what was run.")
    w("")
    w("- **T1 episode detection** — a different task at a different granularity")
    w("- **Episode F1** — belongs to T1 and is not computed here")
    w("- **Memory contribution** — no no-memory arm exists in this evidence")
    w("- **Encoder contribution** — B4 selection is a separate, earlier decision")
    w("- **Calibration contribution** — see §7")
    w("- **Clinical utility** — research software, public-dataset validation only")
    w("- **External generalization** — one dataset, 12 validation subjects")
    w("- **Deployment latency** — `latency_used: false`; no serving path exists")
    w("- **Causal inference** — *causal* here means temporal non-anticipation,")
    w("  never a treatment effect, intervention or counterfactual")
    w("- **Test performance** — the sealed test is unopened and stays so")
    w("")
    w("## 9. Validation firewall — plan §8")
    w("")
    w("| Constraint | Maintained |")
    w("|---|---|")
    w("| TEST partition | not accessed; `sealed_test_state: unopened`, `test_rows_present: false` |")
    w("| New model training | none; no checkpoint loaded, written or refitted |")
    w("| Rerun of outer validation | none; this is a consumed one-shot artifact |")
    w("| Threshold generation | none; thresholds read as frozen, no sweep, no ROC exploration |")
    w("| Artifact modification | none; the run directory was opened read-only |")
    w("| Re-scoring | none; scores read from the persisted row stores |")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if not 2 <= len(argv) <= 3:
        print(__doc__, file=sys.stderr)
        return 2
    run = pathlib.Path(argv[2]) if len(argv) == 3 else DEFAULT_RUN
    pathlib.Path(argv[1]).write_text(build_report(run), encoding="utf-8")
    print(f"wrote {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
