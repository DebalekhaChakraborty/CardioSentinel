# CardioSentinel — handoff to session "ECG 14"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG14.md and continue.
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
Python `3.12.6`. Verified intact throughout ECG 13. Never install, upgrade or
downgrade anything in it.

**Verify that digest with `provenance.dependency_environment()`, not a pip-freeze
hash.**

**Shell state:** the Bash working directory silently resets. Always `cd`
explicitly. Never run `git add -A` anywhere near `/home/AI_POC`.

The remote prints "This repository moved" on every push. Noise, not an error.

---

## 1. THE HEADLINE — governance is closed; the next act is scientific

ECG 13 took the programme from *"the measurement exists but nobody has read it"*
to *"everything is published, frozen, backed up, and documented."* Six PRs merged,
zero open.

**The single remaining gate is the first read of T2 measured values.** It needs
explicit human authorization and has not been given. Do not open them casually.

```
master        c99c8a85a22dde07e9749b8f321b46d0d02b2343
open PRs      none
working tree  3 uncommitted files (§3)
```

### What merged in ECG 13

| PR | Subject |
|---|---|
| #60 | T1 analysis pre-registration + execution-commit record |
| #61 | **T1 descriptive report — the first read of measured values** |
| #62 | T1 post-hoc failure mode analysis |
| #63 | T2 arm-comparison pre-registration |
| #64 | `CURRENT_STATE.md` refresh |
| #65 | **Research Execution Handbook v1.2** |

---

## 2. The T1 result — published and frozen

`docs/T1_DESCRIPTIVE_REPORT_V1.md` is the authority. Restated with the labelling
its pre-registration requires:

| | |
|---|---|
| **Registered primary** — subject-macro mean `episode_f1` | **0.2524** |
| **95% subject-bootstrap interval** | **[0.0826, 0.4415]** |
| `pooled_episode_f1` — episode-weighted, **descriptive, not what the interval brackets** | 0.3423 |

Pooled: 163 reference episodes, 59 predicted runs, 38 matched, 21 unmatched;
473,897 primary windows. **Seven of twelve subjects score zero.**

**Those seven are two incomparable failure modes** (`T1_POST_HOC_ANALYSIS_V1.md`):

| Kind | Subjects | Ref ep. | Predicted runs |
|---|---|---|---|
| **A — episode-free** | `s2005`, `s2020`, `s2023` | 0 | 7, 8, 1 |
| **B — missed** | `s2019`, `s2058`, `s2059`, `s3072` | 6, 3, 47, 1 | 0, 0, 0, 1 |

Group A improves with *fewer* predicted runs, Group B with *more*. They push the
operating point in opposite directions and the mean cannot distinguish them.

The document chain, in creation order — **that ordering is the claim**:
`T1_EVIDENCE_ANALYSIS_PLAN_V1.md` → `T1_DESCRIPTIVE_REPORT_V1.md` →
`T1_POST_HOC_ANALYSIS_V1.md`.

---

## 3. Three uncommitted files — the first thing to do

```
 D docs/RESEARCH_EXECUTION_HANDBOOK_V1_2.md
?? docs/CardioSentinel_Research_Execution_Handbook_v1.2.md
?? docs/CardioSentinel_Research_Execution_Handbook_v1.2.docx
```

The human renamed the merged handbook to match the v1.0/v1.1 convention, and
ECG 13 generated the `.docx`. **Content is byte-identical to what merged**
(`7c7c42a3…`). The human said: *"we will add it with next pr."*

`v1.2.docx` = `af08c216445995fc8cf1d299d0891b9e3b3df3cba4e198311656524a27b99ef9`,
built with `python-docx` using **v1.1 as the style template** — `styles.xml` is
byte-identical to v1.1's, so fonts and theme are inherited, not recreated. There
is no `pandoc` or `libreoffice` on this box.

Worth raising with the human: keep the `.md` too. `.docx` does not diff in git,
and the markdown is what makes future revisions reviewable.

---

## 4. The T2 gate — DO NOT OPEN WITHOUT AUTHORIZATION

`docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md` (merged, `84adf43b…`) pre-registers
the S4D vs GRU comparison. **No T2 measured value has been read by anyone.**

The evidence supports it with **no new run**: `T2_OUTER_VALIDATION_RESULT.json`
carries `per_arm_evidence` for both arms, and the row stores are paired — one
492,904-row identity file and **one label vector** serve both arms, shared
ordering digests, thresholds frozen before outer validation, one causal pass per
arm.

**The load-bearing caveat.** The comparison **is** the selection rule
(`selection_basis: pooled_primary_validation_auprc`,
`selected_arm: causal_s4d_longitudinal_v1`). The **paired contrast is unbiased**;
**S4D's absolute figure on this set is not** — it was chosen for having the
higher value on this very set. Say *"the predefined selection rule selected S4D
based on the observed validation contrast"*, never *"S4D achieved superior
AUPRC"*.

The plan authorizes **exactly one** new computation, labelled `DERIVED ANALYSIS`:
a paired subject-level bootstrap of the S4D − GRU pooled primary AUPRC
difference — subject unit, same rows both arms, no refit, no threshold change, no
reselection, **seed 2026, 1000 replicates** (bound to the artifact's own
registered design). The artifacts carry a per-arm bootstrap and **no interval on
the difference**.

### The exact prompt to use, when the human authorizes it

```
T2 Analysis Execution — Authorized First Read

I authorize step 3 of docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md:
the first read of T2 outer-validation measured values.

Execute strictly to the registered plan:
- report the primary contrast verbatim from selection_decision.pooled_auprc_difference,
  labelled as the predefined selection criterion (§2, §3)
- run ONLY the authorized DERIVED ANALYSIS: paired subject-level bootstrap of the
  S4D - GRU pooled primary AUPRC difference, subject unit, same rows both arms,
  no refit, no threshold change, no reselection, seed 2026, 1000 replicates (§4)
- report secondary analyses separately from the criterion (§5)
- no unbiased absolute S4D performance claim; use the registered phrasing (§3)
- no calibration language attached to T2 scores (§7)
- no TEST access, no retraining, no rerun, no threshold generation (§8)

Produce docs/T2_ARM_COMPARISON_REPORT_V1.md and open the next PR.
Do not modify the plan.
```

---

## 5. Preservation — DONE, and this changes the risk picture

23.08 GiB / 785 files, gitignored, previously on one disk. Now mirrored:

```
s3://cardiosentinel-evidence-341181499761/snapshot-2026-08-22-1bbbd47/
786 objects · 24,779,296,980 bytes
manifest dd42385631ded57320116f82d14124c99d3ffb25ea4c6ec046c69b0d13d377f6
```

Versioning · **Object Lock GOVERNANCE 365 days** · SSE-S3 · public access
blocked. Verified: per-tree object counts 4/4, byte total exact, manifest
round-trip identical, **16/16 sample re-hash passed** (including
`T1_OOF_RESULT.json`, the continuation attestation,
`T2_OUTER_VALIDATION_RESULT.json`, `t2_outer_scores_s4d.npz`).

**Restoring bytes is not restoring evidence state.** S3 assigns its own
`LastModified`, and immutability here is asserted in timestamps ("20 files at
`2026-08-21T19:57:57`"). The manifest carries `sha256 size mtime path`; a restore
must replay them:

```bash
while read -r sha size mtime path; do touch -d "@$mtime" "$path"; done < MANIFEST_SHA256.txt
```

**Credentials.** AWS is a **root session via `aws login`** — MFA enabled, and
`AccountAccessKeysPresent = 0`, so no static root keys exist. The session is
time-limited; it will need re-auth. **GCS was blocked**: the VM service account
carries `devstorage.read_only`. The human chose AWS explicitly; do not re-litigate.

---

## 6. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- **No M2 rerun. No U1 rerun. No T2 rerun. No T1 fold retry. No second
  continuation.** T1's authorization is spent; the flag is `True` on disk but is a
  **spent token, not a live permission**.
- The consumed attempt directory and the continuation directory are both
  **immutable**.
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

| File | SHA-256 |
|---|---|
| `t1_protocol.py` | `b0df6ea2ade450037e94e5ab3b193694fea980337851a2458b3f43873450b192` |
| `t1_execution_spec.py` | `edb0cbf1afe43dee48b5d2d0ed190e0939530fc026fd2f09d3312b929ab1fbe3` |
| `t1_evidence_store.py` | `464ca1607191aa02042a6dcbb8cfeda4d4f3aced1eae2e29ae4b77be8cf6d39c` |
| `t1_development_run.py` | `ad08035d33a1f421cf5a6a18df33e9a7ed55fad29074e7581bbe3ba796b90a8e` |
| `t1_persistence.py` | `77c0e0a40efa7056777ef8d3bb13983ae4cd1bb9493d3c6c7eb11c7faebd68ad` |
| amendment V1.1 | `d3ea7734c93be8f59796e03e8c0210778716327f7adc033cb2d3dcfff7f92c96` |

Fast check — **bare filenames, in this order, run from
`src/cardiosentinel/neural/`** — `sha256sum` them and `md5sum` the result →
`4107286307d147d542ff15e916225315`. Running it with `src/…` paths gives a
different md5 and means nothing.

T1 continuation artifacts (7/7 verified repeatedly in ECG 13):
`T1_OOF_RESULT 9309b00b…` · `T1_SUBJECT_EVIDENCE 6695dd36…` ·
`T1_BOOTSTRAP 57ba6655…` · `T1_CHALLENGE_EVIDENCE 0eb8e684…` ·
`T1_FINAL_CONFIGURATION 37411429…` · `T1_EXPERIMENT_LOCK bcbdfdb0…` ·
`T1_V1_CONTINUATION_EXECUTION_ATTESTATION b5a557dd…`

T2: `T2_OUTER_VALIDATION_RESULT.json c58ed40dac753157…`

Handbooks: `v1.0 669aecc2…` · `v1.1 9a35813a…` · `v1.2.docx af08c216…`

---

## 8. Hard-won lessons from ECG 13

- **"It does not exist" is a claim about a moment, not a fact.** An exhaustive
  `find` for `*handbook*` returned zero, and a full reconstruction was written on
  that basis — then v1.0 and v1.1 `.docx` appeared in `docs/` and the premise
  collapsed. **Say "not found as of <time>", never "unrecoverable".** The draft
  was caught only because the files showed up before the PR opened.
- **A citation can be legitimate while the wording is not the source's.**
  `B4_GLOBAL_ENCODER_SELECTION_V1.md:18` cites "Handbook v1.1 §10.2" then lists
  three ranked criteria. v1.1 §10.2 is actually a **Pareto rule**. The list is the
  selection document's own operationalization. ECG 13 reported it as "verbatim"
  and had to withdraw that in handbook §0.2.
- **Substring false positives, now roughly nine times.** Banned phrases inside a
  prohibition table; `b4d` inside a SHA hex; an escaped `\|` inside a Markdown
  cell; a case-sensitive grep missing a capitalized match; `7.10` matching a
  decimal scan. **Always print the context line before believing a hit.**
- **`awk '{s+=$2} END {printf "%d", s}'` overflows at 2^31.** A 24.7 GB byte sum
  printed as `2147483647`. Use `%.0f`.
- **`find -name "*EXPERIMENT_LOCK*.json"` returns 14 and silently misses the four
  classical runs**, which use lowercase `experiment_lock.json`. Lock audits must
  be case-insensitive.
- **A pytest run started before a branch switch is invalid.** The tree changed
  underneath it. Stop it and re-run on the committed tree.
- **The bootstrap's estimand was found by reading code, not values.**
  `build_bootstrap` averages per-subject `episode_f1`; the report's headline was
  pooled. Different estimands, and printing them adjacently would have made a
  false claim. Read the implementation before trusting a metric's name.
- **Defined is not meaningful.** Availability analysis asked "is this metric
  defined?" and got 12/12 for `episode_f1` — but three subjects have zero
  reference episodes, so their `0.0` is a false-alarm penalty, not a detection
  failure. Check degeneracy as well as definedness.
- **`gh pr view` can transiently report `mergeable: false`** right after the base
  branch moves. Check `mergeStateStatus` and run `git merge-tree` before
  rebasing — ECG 13 avoided an unnecessary force-push that way.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`
  and pin the wait to a specific head SHA so a stale check cannot report green for
  the wrong commit.
- **`--body-file` works on `gh pr create` but not `gh pr edit`.** Use
  `gh api -X PATCH repos/…/pulls/N -F body=@file`.
- **Check `ListAgents` and `git worktree list` before starting.**

---

## 9. Facts that are easy to get wrong

- **U1 is a SPLIT retention.** Platt calibration retained; the selective router
  at `c_star = 0.90` carries `retained: false`. Any doc claiming edge/cloud
  routing is complete is wrong. `IMPLEMENTATION_PLAN.md` items **6, 7 and 8 are
  still factually wrong** and were deliberately left for a later PR.
- **"TEST is sealed" is half true.** B0–B3 consumed their one-shot access in
  Phase 3B-1. Only the **B4/neural** chain is unopened, and it is the last
  firewall.
- **B4-C does not satisfy T2.** B4-C recurs *inside* one 10-second window and
  discards state at the boundary; T2 carries state across windows.
- **B4-D is withdrawn unless reauthorized** — zero code, absent from
  `CANDIDATE_SELECTORS = {"b4b","b4c"}`. **U2 was declared optional and never
  begun** — a recorded decision, not an omission. **E1 never started**;
  benchmark-host latency numbers are **not** edge measurements.
- **T2 scores are uncalibrated** — `score_is_calibrated_probability: false`. A
  bounded sigmoid is not a probability. Never attach calibration language to a T2
  metric.
- **The leakage guarantee is inherited, not re-enforced.** The continuation
  invokes no transition function, so `T1_FORBIDDEN_TRANSITION_INPUTS` does not run
  in its process; the guarantee comes from the predecessor via the digest-verified
  state trace `cf74f00a…`.
- **`stable_id` is in `T1_ALLOWED_ROW_INPUTS` and is still not a feature.**
  `next_state` never reads it; its only other use is threshold tie-breaking. State
  both halves or the allow-list reads as a contradiction.
- **`FORBIDDEN_MODULES` (6) and `NEVER_LOADED_MODULES` (5) differ by exactly one
  member** — `t1_development_run`, which the §16 label authority legitimately
  drags into the process.
- **Handbook phase numbers ≠ run-directory phase numbers.** v1.1 Phase 5B is
  `phase6-m2-*`; Phase 6 is `phase7-u1-*`; Phase 7 spans `phase8-t2-*` and
  `phase9-t1-*`. Cite run directories by path.
- **No research question is affirmatively answered.** RQ3 is answered
  *negatively* — the router was evaluated and rejected. That is a real result.
- **v1.1 §25.3 specified false alarms per hour and temporal IoU. Neither was ever
  computed.** Handbook Appendix A claim 21 forbids reporting them.

---

## 10. Open defects — recorded, not resolved

1. **13 stale tests.** They assert `cardiosentinel-runs/phase9-t1-continuation-v1`
   does **not** exist. It has since 2026-08-22 16:18. **CI is green** because
   `/cardiosentinel-runs/` is gitignored (`.gitignore:33`) and a fresh checkout
   never sees it — so the suite is **green in CI and permanently red on any
   machine holding the evidence**. A local run can no longer signal a regression.
   All 13 are in `tests/neural`; that directory alone reports 2,840 passed / 13
   failed. Full suite: 3,048 passed, 13 failed, 1 skipped in ~16½ min.
2. **The T1 report generator is untracked**, living only in a scratch directory.
   Regenerating from a stale copy would silently revert the §9.2 latency
   correction merged in #62. **Fix this before producing the T2 report**, or the
   T2 report inherits the same gap.
3. **`IMPLEMENTATION_PLAN.md` items 6/7/8 and `README.md` :69/:71** still carry
   the stale routing and "zero T1 attempts" claims.
4. The three uncommitted handbook files (§3).

---

## 11. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG 3
handoff. **M1-v2 remains the canonical frozen M1 development evidence.** The
ECG 3 outer-repo index reconstruction was **reconstructed, not recovered**.

M2 recovery2, the U1 canonical run, the T2 canonical TRAIN run and the T2
one-shot outer VALIDATION all ran clean against the frozen 335-package digest.

**The canonical T1 development attempt was executed on 2026-08-21 at commit
`c538181` and failed post-claim at stage 24. That attempt is consumed and its
directory is immutable. The single authorized measurement continuation was
executed on 2026-08-22 at commit `61704aa` under authorization `b40b4ac`, and it
completed. Its directory is immutable on the same terms. TEST was never opened by
either. No further continuation is authorized.**

---

## 12. Open items for ECG 14

1. **PR: the handbook rename + `.docx`** (§3) — the human deferred it to "the
   next PR".
2. **T2 analysis execution** (§4) — highest scientific value available, zero new
   runs, **gated on explicit human authorization**.
3. **Track the report generator** (§10.2) — ideally before #2.
4. **Repair the 13 stale tests** (§10.1).
5. **Fix `IMPLEMENTATION_PLAN.md` / `README.md` drift** (§10.3).
6. **Calibration reliability analysis** — ECE/Brier from existing U1 artifacts,
   no new runs; addresses the weakest maturity score.
7. **External validation strategy** — the milestone that decides whether any of
   this generalizes. EDB is provably contaminated
   (`CROSS_DATASET_PROVENANCE.md`); a candidate cohort needs a contamination
   audit **before** data reaches disk.
8. **Paper.** Handbook §50 recommends framing this as an **auditable-methodology
   paper with an ECG case study**, not a performance paper — §24 shows no research
   question is affirmatively answered, so the performance framing has no headline
   to carry. Related Work and Discussion do not exist in any form.
9. The ECG 3 outer-repo index reconstruction still merits a human glance.

---

**The danger has shifted again.** ECG 11 was over-engineering before running.
ECG 12 was haste. ECG 13 was **premature interpretation**, and the discipline
held: the numbers were read only after the plan was merged, the post-hoc layer
was labelled, and the weak result was reported without rescue.

What is dangerous now is **momentum**. Governance is finished, the backup is
done, and the obvious next move is to open the T2 numbers. That read is
one-way — and the honest framing of this programme has never depended on what
those numbers say.
