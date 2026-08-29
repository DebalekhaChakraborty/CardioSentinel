# CardioSentinel — handoff to session "ECG 15"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG15.md and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use for CardioSentinel) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/…-ECG-Signal` (renamed `CardioSentinel-AI`) |

`tactics` holds the frozen 335-package set,
`installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`,
Python `3.12.6`. Verified intact throughout ECG 14. Never install, upgrade or
downgrade anything in it.

**Verify that digest with `provenance.dependency_environment()`, not a pip-freeze
hash.**

**Shell state:** the Bash working directory silently resets. Always `cd`
explicitly. Never run `git add -A` anywhere near `/home/AI_POC`.

The remote prints "This repository moved" on every push. Noise, not an error.

---

## 1. THE HEADLINE — the evidence layer is closed, and RQ4 is answered

ECG 13 published T1. **ECG 14 opened T2, executed W1, and audited the external
validation question.** Eleven PRs merged, one open.

```
master        d5a86ce0a2577a6b03c4ebd33c1706deaac90f63
open PRs      none
working tree  clean
```

**A second session (`ai-poc-5f`) was active in this repository during ECG 14
and may still be.** It holds Handbook v1.3 and `CURRENT_STATE.md`, neither of
which has landed. Check `ListAgents` and `git worktree list` before claiming
either.

**RQ4 is the programme's first affirmatively answered research question.** It is
bounded, and the bound is load-bearing — see §4.

### What merged in ECG 14

| PR | Subject |
|---|---|
| #66 | Handbook v1.2 rename + `.docx` |
| #67 | Track the document generators (closed the untracked-generator gap) |
| #68 | Correct `IMPLEMENTATION_PLAN` items 6/7/8 and `README` drift |
| #69 | Repair 13 stale continuation assertions + 3 stale firewall docstrings |
| #70 | T2 paired subject bootstrap — implementation only, no values |
| #71 | U1 calibration reliability **plan + generator** (report NOT yet produced) |
| #72 | **T2 arm-comparison report — the first read of T2 measured values** |
| #73 | W1 window-comparator pre-registration + arm |
| #74 | **W1 report — RQ4 answered** |
| #75 | External validation strategy |
| #76 | W1 report section renumber (fix that missed #74's merge window) |
| #77 | README + `IMPLEMENTATION_PLAN` + `REPO_AUDIT` brought up to master |
| #78 | **U1 per-bin calibration reliability report — the last free analysis** |

---

## 2. The results, as published

### T2 — the contrast is real and its interval crosses zero

`docs/T2_ARM_COMPARISON_REPORT_V1.md`, executed at merged commit `4018435`
under explicit authorization.

| | |
|---|---|
| `selection_basis` | `pooled_primary_validation_auprc` |
| `selected_arm` | `causal_s4d_longitudinal_v1` |
| **`pooled_auprc_difference`** | **0.093215** (tie tolerance 0.002) |
| **95% paired subject-bootstrap** | **[-0.015229, 0.148951]** — **includes zero** |
| pooled primary AUPRC, descriptive | S4D 0.388085 · GRU 0.294870 |
| subject-macro AUPRC, descriptive | S4D 0.428152 · GRU 0.409737 |

**The subject-macro figure is a mean over 9 of 12 subjects**, both arms — the
artifact's own `non_contributing_subject_count` is 3. T1's *defined is not
meaningful* lesson, repeating.

**This difference IS the selection criterion.** Never write "S4D achieved
superior AUPRC". Use "the predefined selection rule selected S4D based on the
observed validation contrast."

### W1 — episode reasoning helps, at one operating point

`docs/W1_WINDOW_COMPARATOR_REPORT_V1.md`, executed at merged commit `f998bf5`
under a §6 authorization to re-open held-out labels.

| | |
|---|---|
| Arm T1 subject-macro `episode_f1` | **0.2524** (reproduces the published value exactly) |
| Arm W subject-macro `episode_f1` | **0.0603** |
| **Difference (T1 − W)** | **0.1921** |
| **95% paired subject-bootstrap** | **[0.0505, 0.3455]** — **excludes zero** |

**The bound that matters.** Both arms ran at thresholds selected *with the state
machine in the loop*: the promoted policy `qw0.9_qe0.99_FAST` binds the quantiles
together with the `FAST` persistence profile, whose `event_confirm_windows = 2`
is a state-machine parameter. A well-tuned memoryless rule was never tested. The
RQ4 row should read **"Supported (bounded)"**, never "Supported".

**Two registered predictions were refuted and reported as refuted:**
1. The alert-row dominance limb was false — T1's `EVENT` hysteresis marks rows
   where the event condition does not hold, so T1 has *more* alert rows in
   *fewer, longer* runs. The run-dominance limb held.
2. The "near-zero difference expected" prediction was wrong. It reasoned only
   about the seven zero-scoring subjects and ignored the five that actually
   score, where Arm W's flood of runs collapses the score.

### External validation — the finding is negative

`docs/EXTERNAL_VALIDATION_STRATEGY_V1.md`. **No drop-in independent cohort
exists in the public record.** PhysioNet's `st-segment` index returns
essentially only LTSTDB; EDB is the only other ST-episode resource and is
partly contaminated. STAFF III has gold-standard occlusion timing but fails on
five axes (1000 Hz, 12-lead, ~5-min segments, inflation instants not episodes,
induced not spontaneous).

**EDB contamination work is already done and enforced in code** —
`evaluation/provenance.py`, 15 exclusions, `overlap_clean` = 75 records, and
`validate_edb_secondary_evaluation_policy` rejects the full cohort for
LTSTDB-trained models. It is a **secondary** cohort and may never be called
external.

**The cold-start trap:** T2's strata show 95.5% of validation rows sit past the
first hour, and `0_5_minutes` scores AUPRC **0.0015**. EDB records are ~2-hour
excerpts against LTSTDB's ~24 hours, so roughly half of every EDB record would
fall in the warm-up regime. **Any EDB evaluation must be cold-start stratified
and pre-registered, or the number is uninterpretable.**

---

## 3. Concurrent session — read before claiming anything

A second session, `ai-poc-5f`, is working in this repository. Coordinated split
as of `eb3de5c`:

| Item | Holder | State |
|---|---|---|
| **#78** U1 per-bin reliability report | `ai-poc-5f` | **MERGED** at `d5a86ce` |
| **Handbook v1.3** | `ai-poc-5f` | in flight, **not landed** |
| **`CURRENT_STATE.md`** | `ai-poc-5f` | in flight, still pinned to `1bbbd47` |
| Evidence map · paper outline | `ai-poc-5f` | planned, new files |
| README · `IMPLEMENTATION_PLAN` · `REPO_AUDIT` | **done** (#77) | merged |

**#78 branched from `4bdf180`, before #77**, and merged cleanly without
reverting it — confirmed on master after the fact: the RQ4 line and the
`REPO_AUDIT` historical header both survive. A two-point
`git diff --stat master..branch` *looked* like a revert; that was master being
ahead, not the branch modifying those files. Check what a branch's own commits
touched (`git diff merge-base branch`) before raising an alarm — this produced
one false alarm in ECG 14.

### The U1 result (#78, merged)

| Family | NLL | Brier | `out_of_fold` |
|---|---:|---:|---|
| Platt (retained) | **0.143708** | **0.040344** | `true` |
| uncalibrated baseline | 0.231705 | 0.063567 | **`false`** |

Protocol §16 condition 2 holds — both lower than baseline. **But the baseline is
not an out-of-fold artifact** and the artifact says so; a side-by-side table
without that flag implies a matched comparison the evidence denies.

**Platt's low ECE is carried by the near-zero region.** Equal-width bin 0 holds
**398,513 of 473,897 rows — 84.1%**. The signed gap turns negative from bin 3 up:
the retained calibrator **over-predicts at high probability**, −0.770848 at bin 13
(128 rows) and −0.941428 at bin 14 (16 rows, sparse by the plan's own threshold,
so not an estimate).

**A registered statistic was the wrong one.** Plan §3.3's degeneracy census
(empty / sparse / smallest / largest) reports "0 empty, 1 sparse", which reads as
a healthy curve while 84% of mass sits in one bin. **Share-of-mass in the
heaviest bin** was the statistic that tells the story. `ai-poc-5f` recorded this
as a limitation under plan §5 step 4 rather than adding it — correctly, because
choosing a statistic after seeing values is what pre-registration prevents. If it
becomes a paper headline it needs a **new** pre-registration, not a retrofit.

Nothing in #78 re-decides the U1 retention. It stays **split**.

---

## 4. Consumed vs available — the section that constrains everything

| One-shot budget | State |
|---|---|
| B0–B3 sealed test | **CONSUMED** (Phase 3B-1) |
| **B4 / neural sealed test** | **AVAILABLE — the last one.** No `TEST_ATTEMPT.json` anywhere; every artifact reads `sealed_test_state: unopened` |
| T1 canonical attempt | CONSUMED (failed stage 24, no lock) |
| T1 measurement continuation | CONSUMED (completed, locked) |
| T2 training · T2 outer validation | CONSUMED |
| M1-v2 · M2 recovery2 · U1 | CONSUMED |
| T1 held-out label re-read | **spent for W1** |

**Exactly one irreversible budget remains.** With #78 open, **every derived
analysis that needed no new authorization has now been run.** There is no
remaining cheap move: anything further requires either a new authorization, a
re-scoring run, or data the project does not have.

**Do not open the B4 sealed test.** The headline T2 contrast spans zero, no
cohort exists to corroborate a test number, and the handbook's own §43 argument
is now backed by evidence rather than caution.

---

## 5. Open items for ECG 15, in priority order

1. **Handbook v1.3 — the critical path to the paper.** v1.2 is now the stalest
   artifact in the repo and it is the "source of truth". Human's requested
   structure: executive summary (RQ3 negative / RQ4 affirmative-bounded / RQ2
   partial / rest open), an **experiment ledger with a consumed column**, and a
   replaced RQ table. §24, §39, §48–§50 and Appendix A all contradict merged
   evidence.
2. **Refresh `CURRENT_STATE.md`.** Still pinned to `1bbbd47` (PR #63) — it
   predates T1's report, all of T2, and all of W1. Held by `ai-poc-5f`.
3. **Evidence Map** — the human asked for a one-page map splitting Methodology
   (leakage controls, pre-registration, one-shot gates, provenance) from
   Scientific Findings (T1 positive, T2 uncertain, U1 negative, RQ4 bounded).
4. **Paper outline.** Related Work and Discussion do not exist in any form.
5. **RQ1 no-memory ablation — protocol first.** It cannot reuse the W1 trick: a
   memory ablation changes `m2g_detector_score` itself, so it needs **re-scoring**
   — a run, not a derived analysis. Pre-register before touching anything.
6. **EDB `overlap_clean`** as a pre-registered, cold-start-stratified secondary
   evaluation, if the human decides to spend the effort.

---

## 6. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- **No M2 rerun. No U1 rerun. No T2 rerun. No T1 fold retry. No second
  continuation.** T1's authorization is spent; the flag is `True` on disk but is
  a **spent token, not a live permission**. The same is now true of
  `T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED`, which is `True` and whose run is
  consumed — **the re-run guard is the persistence claim, not the flag.**
- The consumed attempt and continuation directories are both **immutable**.
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- Keep scratch files **outside the repo**.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; it is NEVER a
  predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

---

## 7. Frozen digests

Fast check — **bare filenames, in this order, run from
`src/cardiosentinel/neural/`** — `sha256sum` them and `md5sum` the result →
`4107286307d147d542ff15e916225315`. Running it with `src/…` paths gives a
different md5 and means nothing.

```
t1_protocol.py  t1_execution_spec.py  t1_evidence_store.py
t1_development_run.py  t1_persistence.py
```

| Artifact | SHA-256 |
|---|---|
| T2 analysis plan V1 | `84adf43b885d6dd3ecef3b678d1a2b89fc6e94f48ffdf8d2f0dc2bb0a7eba973` |
| T2 amendment V1.1 | `859b07c15d160cd5610a52f1b101f4b63fe45efffb32c3938f98cef30fbf52fb` |
| `T2_OUTER_VALIDATION_RESULT.json` | `c58ed40dac753157b00ce6c70eb52fe903ecee72a5ef84e40932c1a80e259dbf` |
| `t2_outer_row_identity.npz` | `1014357cd25d347c7a760e38dbf7ae93c71d56717d13a40e315bb9cb79b220dc` |
| `t2_outer_scores_s4d.npz` | `5c7f9763713c66759cf7e3752cda2a71dacb6cc3f962c5bdd5247017447a7a32` |
| `t2_outer_scores_gru.npz` | `2dbfa5da02f0d96065d72f272875f805f5dceb28410b90582df34c8f6fc17f2d` |
| `t1_oof_state_evidence.npz` | `72f13a8b29eafdd99801bb64dbf8b61f19717f3d7af777d74f21c9709dd28232` |
| amendment V1.1 (T1 recovery) | `d3ea7734c93be8f59796e03e8c0210778716327f7adc033cb2d3dcfff7f92c96` |

---

## 8. Hard-won lessons from ECG 14

- **`gh pr view` reports a stale head after a push.** #74 merged at 23:00:50Z;
  a numbering fix pushed at ~23:03 never landed and the API still reported the
  pre-fix head as green for minutes afterward. **Pin every CI wait to an
  expected SHA** — `scratchpad/ciwait_pinned.py` does this; the unpinned waiter
  certified the wrong commit all session and only got away with it by luck.
- **Substring greps produce false positives roughly ten times now.** A check for
  the word "proved" in the W1 report returned 6 hits, every one from
  **"Provenance"** and **"improved"**. Word-boundary match gives zero. Always
  `grep -w`, and always print the context line.
- **Synthetic tests that pass lists do not exercise numpy paths.** All 27 tests
  for the T2 paired bootstrap passed Python lists; the first real call raised
  `ValueError: truth value of an array … is ambiguous` from `if not subjects`.
  It failed pre-claim and cost nothing *only because the helper was merged and
  exercised first.*
- **Dry-run the render path with a stubbed expensive step.** The T2 report took
  9 minutes per run and needed five runs; a stub that exercised formatting in
  seconds caught a raw-dict dump that would have cost another nine.
- **Omission conceals more than it protects.** Dropping the T2 absolute AUPRC to
  avoid a selection-conditioned claim also hid that the subject-macro mean
  covers 9 of 12 subjects. Publishing with explicit framing was strictly better.
- **A pre-registration's *reasoning* can be wrong even when its discipline is
  right.** W1's §5 mechanism claim was half false and its aggregate prediction
  was refuted. Both were reported as written, which is the only thing that makes
  a prediction worth registering.
- **Verify a policy claim by calling it.** `validate_edb_secondary_evaluation_policy`
  looked like it took a bool; it takes a tuple. The first call raised `TypeError`,
  not the domain error, and asserting "it rejects" from that would have been wrong.
- **A pinned CI wait is not optional.** The unpinned waiter reports green on
  whatever head the API returns. `scratchpad/ciwait_pinned.py` refuses until the
  head matches an expected SHA, and it will TIME OUT (exit 2) rather than pass on
  the wrong commit — a loud failure instead of a silent wrong answer. That is the
  correct behaviour; do not "fix" it.
- **`git diff --stat A B` shows B relative to A, not what B's commits did.** A
  branch cut before a doc PR looks like it reverts that PR. Check
  `git diff merge-base branch` for what the branch actually touched, and simulate
  with `git merge-tree` before warning anyone. Raised one false alarm this way.
- **Check `ListAgents` and `git worktree list` before starting.** Two sessions
  worked this repo concurrently in ECG 14 and the split had to be negotiated by
  message. It worked, but only because both sides declared what they were taking
  before touching `docs/`.

---

## 9. Facts that are easy to get wrong

- **RQ4 is answered, and the bound is not optional.** "Supported (bounded)". The
  operating point was selected with the state machine in the loop.
- **T2's interval includes zero; W1's excludes it.** Different experiments,
  different estimands. Neither licenses a claim about the other.
- **`s4d_temporal_evidence_s_t` feeds BOTH W1 arms**, so W1 says nothing about
  what the S4D architecture contributed. That question — the one a reviewer will
  actually ask — remains unanswered and needs re-scoring, not a derived analysis.
- **U1 is a SPLIT retention.** Platt retained; the selective router at
  `c_star = 0.90` carries `retained: false`. RQ3 is answered **negatively**.
- **"TEST is sealed" is half true.** B0–B3 consumed theirs; only B4/neural is
  unopened.
- **B4-C does not satisfy T2.** B4-C recurs inside one 10-second window and
  discards state at the boundary.
- **T2 scores are uncalibrated.** `score_is_calibrated_probability: false`. A
  bounded sigmoid is not a probability.
- **Handbook phase numbers ≠ run-directory phase numbers.** Cite run directories
  by path.
- **v1.1 §25.3 specified false alarms per hour and temporal IoU. Neither was ever
  computed.** Appendix A claim 21 forbids reporting them.
- The four packages `edge/`, `episodes/`, `personalization/`, `uncertainty/` are
  **empty docstring-only stubs**; the real implementations live in `neural/`
  under experiment-ID prefixes.

---

## 10. Open defects — recorded, not resolved

1. **AWS session EXPIRED — the S3 evidence mirror is UNVERIFIED.** As of
   2026-08-23 `aws sts get-caller-identity` fails and the snapshot at
   `s3://cardiosentinel-evidence-341181499761/snapshot-2026-08-22-1bbbd47/`
   could not be re-listed. The snapshot exists and Object Lock GOVERNANCE at 365
   days was confirmed when it was created; that is a statement about 2026-08-22,
   not about now. **Re-authenticate and re-verify 786 objects /
   24,779,296,980 bytes before recording it as backed up.** An expired
   credential degrading silently into an unverified backup claim is how a
   preservation guarantee rots — nothing fails, the sentence just stops being
   true.
2. **Handbook v1.2 contradicts merged evidence** in §17.3, §24, §39, §50 and
   Appendix A claim 6. It is the declared source of truth and it is wrong.
3. **`CURRENT_STATE.md` is pinned to `1bbbd47`**, fourteen merges behind.
4. **`scripts/provenance/README.md`** — verify the generator list and digests
   match after #78 lands; entries have been added by three separate PRs.
5. **Seven scratch worktrees** remain registered from ECG 14, all on merged
   branches with no uncommitted work. Prune with `git worktree remove --force`
   once no session is mid-flight.
6. **The four empty packages** `edge/`, `episodes/`, `personalization/`,
   `uncertainty/` are docstring-only stubs advertising an architecture the code
   does not use — two of them describe work that is complete inside `neural/`.
7. The ECG 3 outer-repo index reconstruction still merits a human glance.

---

**The danger has shifted again.** ECG 11 was over-engineering before running.
ECG 12 was haste. ECG 13 was premature interpretation. **ECG 14 was
merge-race and stale state** — a fix that missed its window by three minutes, a
CI waiter certifying the wrong commit, and a source-of-truth document that
quietly stopped being true.

What is dangerous now is **the handbook**. It is what a paper will be written
from, it says no research question is affirmatively answered, and that is no
longer true. Fix it before drafting anything.

**Second danger: two sessions, one repository.** ECG 14 ended with a coordinated
split that held — but only because both sides declared their claims before
editing. Do not assume a quiet repo is an idle one.
