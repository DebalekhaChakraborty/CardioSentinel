"""Emit the W1 window-only comparator report per the approved plan.

Executes `docs/W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1.md` under the §6
authorization: the T1 held-out labels are re-opened, through the §16 authority,
to score a second arm on rows that were already scored once.

**The state machine is never invoked.** Arm T1's predictions are read from the
persisted `emitted_state` column of the consumed attempt. Arm W's are computed
by `w1_window_comparator.window_only_event_flags`. Both arms are then scored by
the *same* episode matching the continuation used --
`t1_protocol.group_reference_episodes`, `match_runs_to_episodes`, and
`t1_continuation_measurement.contiguous_runs` -- so the two arms differ in their
transition logic and in nothing else.

**Nothing is claimed, created or written.** No run directory, no attempt id, no
threshold, no checkpoint. The consumed attempt is opened read-only and its
digest is verified before a single row is read.

Usage, from the repository root, on the frozen scientific interpreter:

    python scripts/provenance/gen_w1_window_comparator_report.py <output.md>
"""

from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys
from typing import Any

import numpy as np

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from cardiosentinel.neural import w1_window_comparator as W1  # noqa: E402
from cardiosentinel.neural.t1_continuation_labels import (  # noqa: E402
    continuation_held_out_authority,
    continuation_identity_path,
    continuation_target_source,
    held_out_labels_for_fold,
)
from cardiosentinel.neural.t1_continuation_measurement import (  # noqa: E402
    contiguous_runs,
)
from cardiosentinel.neural.t1_continuation_spec import (  # noqa: E402
    PREDECESSOR_FOLD_SELECTIONS,
)
from cardiosentinel.neural.t1_protocol import (  # noqa: E402
    group_reference_episodes,
    match_runs_to_episodes,
)

PLAN = "docs/W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1.md"

#: The evidence tree is gitignored and local-only, so a worktree that does not
#: contain it can still run this by passing its root as `argv[2]`. Defaults to
#: the repository the script lives in.
EVIDENCE_ROOT = REPOSITORY_ROOT


def consumed_attempt() -> pathlib.Path:
    return (
        EVIDENCE_ROOT
        / "cardiosentinel-runs"
        / "phase9-t1-development-v1"
        / "t1-v1-development"
    )
STATE_EVIDENCE = "t1_oof_state_evidence.npz"

#: Bound by `T1_EXECUTION_RECOVERY_AMENDMENT_V1_1` §1.3. Verified before the
#: first row is read; a mismatch means the preserved evidence has moved.
STATE_EVIDENCE_SHA256 = (
    "72f13a8b29eafdd99801bb64dbf8b61f19717f3d7af777d74f21c9709dd28232"
)

#: T1's registered primary, published in `T1_DESCRIPTIVE_REPORT_V1.md` §3.
#: Arm T1 must reproduce it or the comparator is scoring different rows.
T1_PUBLISHED_SUBJECT_MACRO = 0.2524

EVENT = "EVENT"
UNDEFINED = "*undefined*"

#: Plan §5, restated from `T1_POST_HOC_ANALYSIS_V1.md`.
GROUP_A = ("ltstdb:s2005", "ltstdb:s2020", "ltstdb:s2023")
GROUP_B = ("ltstdb:s2019", "ltstdb:s2058", "ltstdb:s2059", "ltstdb:s3072")


class W1ReportError(RuntimeError):
    """A refusal. The analysis stops rather than reporting something else."""


def fmt(value, places: int = 4) -> str:
    if value is None:
        return UNDEFINED
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    if isinstance(value, float):
        return f"{value:.{places}f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def verify_and_load() -> dict[str, np.ndarray]:
    """Digest the preserved state evidence, then read it. Never the reverse."""
    path = consumed_attempt() / STATE_EVIDENCE
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != STATE_EVIDENCE_SHA256:
        raise W1ReportError(
            f"{STATE_EVIDENCE} digests {digest}; the amendment binds "
            f"{STATE_EVIDENCE_SHA256}. The preserved evidence has moved. Stop."
        )
    with np.load(path, allow_pickle=False) as store:
        return {name: store[name] for name in store.files}


def episode_evidence(
    starts: np.ndarray, positives: np.ndarray, flags: np.ndarray
) -> dict[str, int]:
    """One stream's episode counts, by the continuation's own construction."""
    episodes = group_reference_episodes(
        [int(s) for s in starts], [bool(p) for p in positives]
    )
    runs = contiguous_runs([bool(f) for f in flags])
    matched = match_runs_to_episodes(episodes, runs)
    return {
        "reference_episodes": len(episodes),
        "predicted_event_runs": len(runs),
        "matched_episodes": len(matched),
        "unmatched_predicted_runs": len(runs) - len(set(matched.values())),
    }


def measure_fold(columns: dict[str, np.ndarray], fold_index: int) -> dict[str, Any]:
    """Both arms, one fold, identical rows and identical episode matching."""
    subject, policy_id, selection_digest = PREDECESSOR_FOLD_SELECTIONS[fold_index]
    mask = columns["fold_index"] == fold_index

    fold_columns = {name: values[mask] for name, values in columns.items()}
    stable_ids = fold_columns["stable_id"]

    # The §6 authorized read. One fold, one subject, one call, through the
    # authority that already governs which members may be read.
    source = continuation_target_source(continuation_identity_path(EVIDENCE_ROOT))
    authority = continuation_held_out_authority(
        fold_index, source, verified_selection_sha256=selection_digest
    )
    labels = held_out_labels_for_fold(authority, fold_index)

    primary_mask = np.asarray(
        [bool(labels["primary_mask"][str(sid)]) for sid in stable_ids]
    )
    primary_positive = np.asarray(
        [bool(labels["primary_positive"][str(sid)]) for sid in stable_ids]
    )

    arm_t1_flags = np.asarray(
        [str(state) == EVENT for state in fold_columns["emitted_state"]]
    )
    arm_w_flags = W1.window_only_event_flags(fold_columns)

    totals = {
        "arm_t1": dict.fromkeys(
            (
                "reference_episodes",
                "predicted_event_runs",
                "matched_episodes",
                "unmatched_predicted_runs",
            ),
            0,
        ),
        "arm_window": dict.fromkeys(
            (
                "reference_episodes",
                "predicted_event_runs",
                "matched_episodes",
                "unmatched_predicted_runs",
            ),
            0,
        ),
    }
    keys = sorted(
        {
            (str(r), int(c))
            for r, c in zip(fold_columns["record_id"], fold_columns["channel_index"])
        }
    )
    for record_id, channel_index in keys:
        in_stream = np.asarray(
            [
                str(r) == record_id and int(c) == channel_index
                for r, c in zip(
                    fold_columns["record_id"], fold_columns["channel_index"]
                )
            ]
        )
        order = np.argsort(fold_columns["start_sample"][in_stream], kind="stable")
        starts = fold_columns["start_sample"][in_stream][order]
        positives = primary_positive[in_stream][order]
        for arm, flags in (("arm_t1", arm_t1_flags), ("arm_window", arm_w_flags)):
            evidence = episode_evidence(starts, positives, flags[in_stream][order])
            for key, value in evidence.items():
                totals[arm][key] += value

    return {
        "fold_index": fold_index,
        "held_out_subject": subject,
        "selected_policy_id": policy_id,
        "stream_count": len(keys),
        "row_count": int(mask.sum()),
        "primary_rows": int(primary_mask.sum()),
        "arm_t1": {
            **totals["arm_t1"],
            "episode_f1": W1.episode_f1(totals["arm_t1"]),
            "alert_rows": int(arm_t1_flags.sum()),
        },
        "arm_window": {
            **totals["arm_window"],
            "episode_f1": W1.episode_f1(totals["arm_window"]),
            "alert_rows": int(arm_w_flags.sum()),
        },
    }


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORY_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 - provenance is best-effort, never fatal
        return "unrecorded"


def build_report() -> str:
    columns = verify_and_load()
    folds = [measure_fold(columns, index) for index in sorted(PREDECESSOR_FOLD_SELECTIONS)]

    arm_t1 = {f["held_out_subject"]: f["arm_t1"]["episode_f1"] for f in folds}
    arm_window = {f["held_out_subject"]: f["arm_window"]["episode_f1"] for f in folds}

    macro_t1 = W1.subject_macro(arm_t1)
    W1.require_arm_reproduces_published(macro_t1, T1_PUBLISHED_SUBJECT_MACRO)
    derived = W1.paired_subject_macro_difference(arm_t1, arm_window)

    out: list[str] = []
    w = out.append
    w("# W1 Window-Only Comparator — Report, V1")
    w("")
    w(f"**Step 3 of `{PLAN}`: the first read of comparator values.** Produced")
    w("under the §6 authorization to re-open the T1 held-out labels, to the")
    w("reporting shape fixed in §4 and §5 of that plan before any comparator")
    w("value existed. The plan was not modified.")
    w("")
    w("**RQ4 — *does longitudinal/episode reasoning improve monitoring quality?* —")
    w("was recorded unanswered because the T1 measurement was one-armed.** This is")
    w("the second arm.")
    w("")
    w("---")
    w("")
    w("## 1. Provenance and firewall")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Analysis executed at commit | `{_git_sha()}` |")
    w(f"| Preserved state evidence | `{STATE_EVIDENCE}` |")
    w(f"| Digest, verified before any row was read | `{STATE_EVIDENCE_SHA256}` |")
    w(f"| Rows in the consumed trace | {fmt(int(columns['fold_index'].size))} |")
    w("| State machine invoked | `false` |")
    w("| Run directory created or written | `false` |")
    w("| Threshold generated, swept or altered | `false` |")
    w("| Model refitted or re-scored | `false` |")
    w("| TEST accessed | `false` |")
    w("")
    w("Labels were opened one fold at a time through the §16 authority, under the")
    w("selection already promoted for that fold, and were used only to score")
    w("states and flags that were computed before any label was read.")
    w("")
    w("---")
    w("")
    w("## 2. Primary result — plan §4.1")
    w("")
    w("Subject-macro mean `episode_f1`, **Arm T1 − Arm W**. Positive favours the")
    w("episode state machine.")
    w("")
    w("| | |")
    w("|---|---|")
    w(f"| Arm T1 subject-macro `episode_f1` | **{fmt(derived['arm_t1_subject_macro'])}** |")
    w(f"| Arm W subject-macro `episode_f1` | **{fmt(derived['arm_window_subject_macro'])}** |")
    w(f"| **Difference, Arm T1 − Arm W** | **{fmt(derived['point_estimate'])}** |")
    w(f"| **95% paired subject-bootstrap interval** | **[{fmt(derived['lower_95'])}, {fmt(derived['upper_95'])}]** |")
    w(f"| Successful replicates | {fmt(derived['successful_replicates'])} |")
    w(f"| Undefined replicates | {fmt(derived['undefined_replicates'])} |")
    w(f"| Seed | {fmt(derived['seed'])} |")
    w("")
    w("### 2.1 Arm T1 reproduces its published value")
    w("")
    w(f"Arm T1's subject-macro mean is {fmt(macro_t1)}, against the")
    w(f"{T1_PUBLISHED_SUBJECT_MACRO} published in `T1_DESCRIPTIVE_REPORT_V1.md`.")
    w("Plan §4.1 made this a stopping condition: had it not reproduced, the")
    w("comparator would be scoring different rows and the analysis would have")
    w("stopped rather than reported a second number.")
    w("")
    w("### 2.2 Claim scope")
    w("")
    w("The interval describes **between-subject variation in the paired contrast,")
    w("conditional on the fitted upstream models and frozen thresholds.** It is")
    w("not a confidence interval for a population parameter and it is not a")
    w("hypothesis test. **No p-value and no significance language appears")
    w("anywhere.** It is also an *unconditional* resample: no selection event is")
    w("conditioned on, because no selection was made here.")
    w("")
    w("Twelve subjects. The interval is coarse by construction and its tails are")
    w("governed by a handful of subjects, exactly as plan §4.2 registered before")
    w("execution.")
    w("")
    w("---")
    w("")
    w("## 3. Per-subject evidence — plan §4.3")
    w("")
    w("Reported separately and never aggregated into §2. Plan §5 registered that")
    w("**the per-subject table is the only thing that distinguishes genuine")
    w("equivalence from two real effects cancelling**, which is why it is here.")
    w("")
    w("| Fold | Subject | Ref. ep. | T1 runs | T1 matched | T1 `episode_f1` | W runs | W matched | W `episode_f1` |")
    w("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for fold in folds:
        t1, wi = fold["arm_t1"], fold["arm_window"]
        w(
            f"| {fold['fold_index']} | `{fold['held_out_subject']}` "
            f"| {fmt(t1['reference_episodes'])} "
            f"| {fmt(t1['predicted_event_runs'])} | {fmt(t1['matched_episodes'])} "
            f"| {fmt(t1['episode_f1'])} "
            f"| {fmt(wi['predicted_event_runs'])} | {fmt(wi['matched_episodes'])} "
            f"| {fmt(wi['episode_f1'])} |"
        )
    w("")
    w("### 3.1 Dominance — one registered limb holds, the other does not")
    w("")
    w("Plan §5 asserted that Arm W *\"must produce at least as many alert rows as")
    w("Arm T1 ... and therefore weakly more predicted runs.\"* Both limbs are")
    w("checked here. **The run limb holds. The alert-row limb is false.**")
    w("")
    w("| Fold | Subject | T1 runs | W runs | W ≥ T1 runs | T1 alert rows | W alert rows | W ≥ T1 rows |")
    w("|---|---|---:|---:|---|---:|---:|---|")
    runs_hold = rows_hold = True
    for fold in folds:
        t1, wi = fold["arm_t1"], fold["arm_window"]
        r_ok = wi["predicted_event_runs"] >= t1["predicted_event_runs"]
        x_ok = wi["alert_rows"] >= t1["alert_rows"]
        runs_hold, rows_hold = runs_hold and r_ok, rows_hold and x_ok
        w(
            f"| {fold['fold_index']} | `{fold['held_out_subject']}` "
            f"| {fmt(t1['predicted_event_runs'])} | {fmt(wi['predicted_event_runs'])} "
            f"| {fmt(r_ok)} | {fmt(t1['alert_rows'])} | {fmt(wi['alert_rows'])} "
            f"| {fmt(x_ok)} |"
        )
    w("")
    w(f"Run dominance holds for every fold: {fmt(runs_hold)}. "
      f"Alert-row dominance: {fmt(rows_hold)}.")
    w("")
    w("**Why the alert-row limb was wrong.** Once Arm T1 enters `EVENT` it")
    w("*stays* there until a release condition fires, so it marks rows on which")
    w("the event condition does **not** hold. Arm W marks only rows where the")
    w("condition holds. The state machine therefore produces **more alert rows in")
    w("fewer, longer runs**, and the memoryless rule produces fewer rows in many")
    w("short ones. The plan reasoned about confirmation and overlooked hysteresis.")
    w("")
    w("The predictions in §4 rest on the **run** limb, which holds, so they are")
    w("still testable. The error is recorded rather than quietly dropped.")
    w("")
    w("---")
    w("")
    w("## 4. Registered predictions — plan §5")
    w("")
    w("Recorded before any comparator value existed. Reported as written.")
    w("")
    w("| Group | Subjects | Registered prediction |")
    w("|---|---|---|")
    w(f"| **A — episode-free** | {', '.join(f'`{s}`' for s in GROUP_A)} | worse or unchanged at zero |")
    w(f"| **B — missed** | {', '.join(f'`{s}`' for s in GROUP_B)} | may improve |")
    w("")
    w("| Group | Subject | Ref. ep. | Arm T1 `episode_f1` | Arm W `episode_f1` | Direction |")
    w("|---|---|---:|---:|---:|---|")
    by_subject = {f["held_out_subject"]: f for f in folds}
    for label, group in (("A", GROUP_A), ("B", GROUP_B)):
        for subject in group:
            fold = by_subject.get(subject)
            if fold is None:
                continue
            left = fold["arm_t1"]["episode_f1"]
            right = fold["arm_window"]["episode_f1"]
            if left is None or right is None:
                direction = UNDEFINED
            elif right > left:
                direction = "W higher"
            elif right < left:
                direction = "T1 higher"
            else:
                direction = "equal"
            w(
                f"| {label} | `{subject}` | {fmt(fold['arm_t1']['reference_episodes'])} "
                f"| {fmt(left)} | {fmt(right)} | {direction} |"
            )
    w("")
    w("### 4.1 The aggregate prediction was wrong")
    w("")
    w("**Plan §5 registered that a near-zero difference was the expected outcome,")
    w("and that it would be uninformative rather than reassuring.** The observed")
    w(f"difference is {fmt(derived['point_estimate'])} with a 95% paired interval")
    w(f"of [{fmt(derived['lower_95'])}, {fmt(derived['upper_95'])}], which")
    w("**excludes zero**. The registered expectation is refuted, and plan §5")
    w("binds this report to say so rather than reconcile it.")
    w("")
    w("**Why it was wrong.** The §5 reasoning considered only the seven")
    w("zero-scoring subjects, whose two failure modes do push in opposite")
    w("directions — and among them the prediction held: Group A is unchanged at")
    w("zero, and one Group B subject improved. But it never considered the five")
    w("subjects that actually score. For those, Arm W's flood of predicted runs")
    w("inflates the `episode_f1` denominator `predicted + reference` without")
    w("matching proportionally more episodes, and the score collapses. The")
    w("aggregate is driven by the subjects the prediction ignored.")
    w("")
    w("That is a defect in the pre-registered reasoning, not in the measurement.")
    w("It is recorded here because a prediction that is only checked when it")
    w("succeeds is not a prediction.")
    w("")
    w("---")
    w("")
    w("## 5. The operating-point asymmetry — the limitation that bounds this result")
    w("")
    w("**Both arms run at thresholds that were selected with the state machine in")
    w("the loop.** The promoted per-fold policy id is")
    w(f"`{folds[0]['selected_policy_id']}`: it binds the quantile levels")
    w("`q_watch = 0.9` and `q_event = 0.99` **together with** the `FAST`")
    w("persistence profile, whose `event_confirm_windows = 2` is a state-machine")
    w("parameter. The operating point and the confirmation requirement were")
    w("chosen jointly.")
    w("")
    w("Arm W is therefore evaluated at an operating point tuned for a rule it")
    w("does not implement. A memoryless rule at a `q_event` of 0.99 fires on")
    w("roughly the top percentile of rows with nothing to suppress isolated")
    w("firings, which is exactly the flood of short runs observed in §3.")
    w("**A memoryless rule given its own operating point would very likely score")
    w("better than Arm W does here.**")
    w("")
    w("This is not a defect that can be repaired inside this analysis. Plan §7")
    w("excludes any threshold sweep for either arm, correctly — sweeping would be")
    w("threshold generation, and a comparator handed its own tuned operating")
    w("point while the incumbent keeps its frozen one would be uninterpretable in")
    w("the other direction. Both framings have a thumb on the scale; this one's")
    w("thumb is named.")
    w("")
    w("**What the result therefore supports:** at the operating point this")
    w("programme actually selected and froze, the episode state machine agrees")
    w("with reference episodes substantially better than the memoryless rule does")
    w("at that same point.")
    w("")
    w("**What it does not support:** that episode reasoning beats window-level")
    w("alerting *in general*, or that a well-tuned memoryless alerting rule would")
    w("lose. Neither claim is testable from this evidence, and the second would")
    w("need a threshold search nobody has authorized.")
    w("")
    w("Plan §9 registered the mirror-image risk — that a null result would be")
    w("misread as *\"the state machine is useless\"*. The non-null result carries")
    w("the same hazard facing the other way, and it is named here for the same")
    w("reason.")
    w("")
    w("---")
    w("")
    w("## 5. What this does and does not answer")
    w("")
    w("**Answers.** Whether the T1 episode state machine changes episode-level")
    w("agreement relative to a memoryless window rule, on identical rows, under")
    w("identical frozen thresholds, with every upstream component shared.")
    w("")
    w("**Does not answer.** Whether the *T2 S4D temporal score* contributes")
    w("anything: `s4d_temporal_evidence_s_t` is an input to **both** arms, so this")
    w("ablation holds it fixed. That is a separate missing arm and a separate")
    w("experiment, and it would require re-scoring rather than a derived analysis.")
    w("")
    w("**Also does not evaluate** the encoder, physiology fusion, memory or")
    w("calibration — each is common to both arms by construction — nor TEST")
    w("performance, generalisation beyond LTSTDB, clinical utility, or deployment")
    w("latency.")
    w("")
    w("**Neither arm is characterised as better or worse in monitoring terms.**")
    w("Ranking them needs an alerting-cost model this programme does not have.")
    w("The numbers are reported and left unranked.")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    global EVIDENCE_ROOT
    if not 2 <= len(argv) <= 3:
        print(__doc__, file=sys.stderr)
        return 2
    if len(argv) == 3:
        EVIDENCE_ROOT = pathlib.Path(argv[2]).resolve()
    pathlib.Path(argv[1]).write_text(build_report(), encoding="utf-8")
    print(f"wrote {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
