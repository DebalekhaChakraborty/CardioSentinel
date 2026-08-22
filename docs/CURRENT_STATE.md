# Current State

This is a living document, not a frozen protocol record. Unlike the `_V1`
documents elsewhere in this folder, it carries no digest and no freeze ritual —
it is meant to be regenerated wholesale, not amended. Do not hand-edit the
data sections; ask Claude to refresh this file (a fresh read-only pass against
`git`, `gh`, and `cardiosentinel-runs/`) and it will be rewritten in place.
Commentary can go in a `Notes` subsection if needed, but treat everything else
here as disposable output, not source of truth — **the repository is the
source of truth; this file is a cache of it.**

`docs/IMPLEMENTATION_PLAN.md` and `docs/RESEARCH_SCOPE.md` are the project's
narrative plan and have not been revised since 2026-08-07. This file exists
because those two drifted far enough from reality that a 2026-08-21 audit had
to reconstruct actual state from `cardiosentinel-runs/` and git history by
hand. Read this file for "where are we," and the `_V1` docs for "what did we
decide and why."

---

**As of:** `origin/master` `1bbbd47` (merge of PR #63), 2026-08-22
**Working tree:** clean
**Open PRs:** 0
**Canonical T1 attempt:** **CONSUMED** — failed post-claim at stage 24
**T1 measurement continuation:** **COMPLETED** — the single authorization is spent
**Sealed B4/neural TEST:** unopened

---

## Live flag — the T1 attempt is gone, and no second one exists

The previous refresh of this file said *"the single canonical T1 attempt is
**not** consumed."* **That is now false, and it was the most dangerous sentence
this cache has ever carried.** Anything that reads a stale copy and plans around
an available attempt is planning around something that no longer exists.

```
Canonical attempt   t1-v1-development       executed 2026-08-21 at c538181
                                            FAILED post-claim at stage 24
                                            consumed, directory immutable
Continuation        t1-v1-measurement-continuation
                                            executed 2026-08-22 at 61704aa
                                            under authorization b40b4ac
                                            COMPLETED in 10 seconds
                                            authorization spent, directory immutable
```

**§14 of the recovery amendment authorizes no second continuation, and none is
predeclared.** `T1_CONTINUATION_AUTHORIZED` is `True` on disk but it is a spent
token, not a live permission. There is no remaining T1 execution budget of any
kind.

The continuation took **two launches**. The first raised
`TypeError: git_provenance() missing 1 required positional argument` at
`runner.py:282`, six lines before `_claim()` at `runner.py:288`, so per §25 the
attempt was **not** consumed and the authorization survived. PR #59 fixed the
argument and added the seam test that should have preceded the first launch. Do
not read that as a near miss handled well; read it as the same defect class that
consumed the canonical attempt at stage 24 — stages tested, junctions not.

---

## 1. Repository identity

| | |
|---|---|
| Repository | `tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` (GitHub: `DebalekhaChakraborty/…`, renamed `CardioSentinel-AI`) |
| `origin/master` | `1bbbd47020099327ae08cf0acab8ba5dc764c07a` — merge of PR #63, 2026-08-22 |
| Working tree | clean |
| Open PRs | **0** — #39 was **closed unmerged** 2026-08-21T19:23Z and replaced by #47 |
| Outer repo (`/home/AI_POC`) | HEAD `086ee2813`, untouched by this pass |
| Scientific interpreter | `/home/AI_POC/venvs/tactics/bin/python`, Python 3.12.6, 335 packages, `installed_packages_sha256 = b0fd6ea…` |

### Recent history (last 12 commits)

```
1bbbd47  Merge PR #63 — T2 preregistered S4D vs GRU analysis plan
b79185f  T2: preregistered S4D vs GRU outer validation analysis plan
73358bc  Merge PR #62 — T1 post-hoc failure mode analysis
c337404  T1: post-hoc failure mode analysis and interpretation
9a03735  Merge PR #61 — T1 preregistered evidence report
16c96f6  T1: generate the preregistered evidence report
a878405  Merge PR #60 — analysis pre-registration + execution record
6742291  Fix the primary estimate, the latency wording, and the exclusion list
8a0132c  Pin the bootstrap's estimand before the values are read
086161f  Add endpoint and claim hierarchy to the T1 analysis plan
08152c8  Record T1 analysis pre-registration and continuation execution
61704aa  Merge PR #59 — T1 claim-to-lock seam hardening  [continuation ran at this commit]
```

### PRs merged since the last refresh

| PR | Subject |
|---|---|
| #46 | Docs sync — plan, scope, README |
| #47 | Authorize canonical development execution (replaced the closed #39) |
| #48–#50 | Recovery amendment V1.1 · diagnosable failure · held-out persistence |
| #51–#52 | Attempt tripwires · recovery prerequisites and reconstructed receipt |
| #53–#54 | Continuation safety framework · continuation evidence contract |
| #55–#56 | Gated measurement execution engine · label authority integration |
| #57–#58 | Pre-authorization record · **the authorization itself** |
| #59 | Seam hardening — fixed the pre-claim `TypeError` |
| #60 | Analysis pre-registration + execution-commit record |
| #61 | **T1 descriptive report — first read of measured values** |
| #62 | T1 post-hoc failure mode analysis |
| #63 | T2 arm-comparison pre-registration |

## 2. Where this stands vs. the plan docs

`docs/IMPLEMENTATION_PLAN.md` and `docs/RESEARCH_SCOPE.md` remain unrevised
since 2026-08-07 and are now further behind than at the last refresh.

| # | Item | Doc says | Reality |
|---|---|---|---|
| 1–3 | Ingestion · signal pipeline · baselines B0–B3 | complete | matches |
| 4 | Patient-adaptive memory | future work | **done** — M1L retained, M2-G retained |
| 5 | Physiology-guided model | future work | **done** — P1-B retained |
| 6 | Uncertainty calibration | future work | **partial** — Platt retained, **router NOT retained** |
| 7 | Temporal episode reasoning | future work | **done** — T2 selected, T1 executed and measured |
| 8 | Edge/cloud routing | future work | **NOT done** — the router was explicitly rejected |
| 9 | Edge benchmarking | future work | partial — benchmark host only, never on-device |
| 10 | Final ablation & external validation | future work | matches — not started |

**Item 8 is the correction that matters.** Any document claiming edge/cloud
routing is complete is wrong: `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`
records a **split** retention — calibration retained, the symmetric window-level
selective router at `c_star = 0.90` **not** retained.

## 3. Experiment ladder

| ID | Status | Evidence | Notes |
|---|---|---|---|
| B0–B3 | complete, **TEST opened** | `phase3b-classical-v3` | one-shot sealed-test access already spent in Phase 3B-1 |
| B4-A | complete, **rejected** | `phase3b2-b4-v1` | `B4CompactCNN`, 87,089 params |
| **B4-B** | **SELECTED encoder** | `phase3b2-architecture-v1` | `B4BTransformerCNN`, 309,809 params |
| B4-C | complete, **rejected** | `phase3b2-architecture-v1` | `B4CSSMCNN`, 155,313 params |
| P1 | **P1-B retained** | `phase4-p1-physiology-v1` | retained with a recorded rate-related FPR caveat |
| M1 | **M1L retained** | `phase5-m1-dual-memory-v2` | v2 canonical; v1 has two documented stage-1 failures |
| M2 | **M2-G retained** | `phase6-m2-development-v1` | canonical is **recovery2**; two earlier attempts have failure receipts |
| U1 | **split retention** | `phase7-u1-development-v1` | Platt retained, router rejected |
| T2 | **S4D retained** | `phase8-t2-development-v1` | training + one-shot outer VALIDATION, both arms scored |
| **T1** | **executed and measured** | `phase9-t1-development-v1` (failed) + `phase9-t1-continuation-v1` (completed) | see §4 |
| E1 | not started | — | `edge/` is a docstring; no inference path exists |

Also present: three `phase-3b-smoke-*` folders (CI fixtures, not science) and
`cardiosentinel-runs/T1/T1_state_machine_v1/` which reads `status: COMPLETE`
but is `run_class: harness_verification`, `protocol_evidence: false` — **not
evidence.**

## 4. T1 result — published, frozen

The measurement is complete and reported. `docs/T1_DESCRIPTIVE_REPORT_V1.md` is
the authority; the values below are its headline, restated with the labelling
its pre-registration requires.

| | |
|---|---|
| **Registered primary** — subject-macro mean `episode_f1` | **0.2524** |
| **95% subject-bootstrap interval** | **[0.0826, 0.4415]** |
| `pooled_episode_f1` — episode-weighted, **descriptive, not what the interval brackets** | 0.3423 |

Twelve held-out LTSTDB subjects, cross-fitted, subject-disjoint. **Seven of
twelve score zero**, and per `docs/T1_POST_HOC_ANALYSIS_V1.md` those zeros are
two incomparable failure modes: three subjects (`s2005`, `s2020`, `s2023`) have
**no reference episodes at all**, so their zero is a false-alarm penalty rather
than a detection failure; four (`s2019`, `s2058`, `s2059`, `s3072`) missed real
episodes. MCC and onset latency are undefined for exactly those seven and are
reported as undefined, never zero-filled.

**The document chain, in the order it was created:**

1. `docs/T1_EVIDENCE_ANALYSIS_PLAN_V1.md` — pre-registration, §§1–6 written
   before any value was read, §7 added at approval (still pre-read), §8 the
   approval record
2. `docs/T1_DESCRIPTIVE_REPORT_V1.md` — the first read of measured values
3. `docs/T1_POST_HOC_ANALYSIS_V1.md` — explicitly labelled post-hoc

That ordering is the point and should not be presented any other way.

### What T1 does not support

No improvement claim (one-armed measurement, no comparator) · no memory or SSM
ablation · no external generalization · no subgroup claim · no test claim · no
clinical claim · no significance claim · no deployment claim. **"Causal" here
means temporal non-anticipation, never causal inference.**

## 5. T2 — next gate, values unread

`docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md` (PR #63) pre-registers the S4D vs
GRU comparison. **No T2 measured value has been read.**

The evidence supports it without any new run: `T2_OUTER_VALIDATION_RESULT.json`
carries `per_arm_evidence` for both arms, and the row stores are paired —
one 492,904-row identity file and one label vector serve both arms, shared
ordering digests, thresholds frozen before outer validation.

**The load-bearing caveat:** the comparison **is** the selection rule
(`selection_basis: pooled_primary_validation_auprc`). The paired contrast is
unbiased; S4D's absolute figure on this set is not. The plan forbids any
unbiased-absolute-performance claim.

**Step 3 of that plan — the first read of T2 values — requires explicit human
authorization and has not been given.**

## 6. Code maturity

| Layer | Location | Maturity |
|---|---|---|
| Models | `models/` | thin — only `baselines.py`; neural architectures live in `neural/` |
| Trainers | `neural/*_experiment.py`, `*_development_run.py` | mature, one harness per phase |
| Pipelines | `signal/` · `features/` · `data/` | mature |
| **Inference path** | — none — | **not started.** No `predict()`, no ONNX, no TorchScript, no serving |
| Evaluation | `evaluation/` | mature, shared |
| `neural/` | 83 modules, ~53.5k lines | has absorbed what `edge/`, `episodes/`, `personalization/`, `uncertainty/` were meant to hold — all four are still one-line docstrings |
| Test suite | `tests/` | **3,062 collected** — see the defect below |

### ⚠️ The local suite is red and CI is green, for a structural reason

**13 tests fail locally and pass in CI.** Every one asserts that
`cardiosentinel-runs/phase9-t1-continuation-v1` **does not exist**. It has
existed since the continuation ran on 2026-08-22 at 16:18.

CI passes because `/cardiosentinel-runs/` is gitignored (`.gitignore:33`, 0
tracked files), so a fresh checkout has no continuation directory and the
assertions hold. **The suite is therefore green in CI and permanently red on any
machine that holds the evidence**, which means a local run can no longer signal a
real regression. All 13 are in `tests/neural`; `tests/neural` alone reports
2,840 passed / 13 failed. This needs its own PR.

## 7. Data preservation — **backed up 2026-08-22**

Previously the largest unmanaged risk in the programme. Now closed.

| | |
|---|---|
| Destination | `s3://cardiosentinel-evidence-341181499761/snapshot-2026-08-22-1bbbd47/` (`us-east-1`) |
| Contents | **786 objects, 24,779,296,980 bytes** — 785 evidence files + manifest |
| Manifest | `MANIFEST_SHA256.txt`, sha256 `dd42385631ded57320116f82d14124c99d3ffb25ea4c6ec046c69b0d13d377f6` |
| Protection | Versioning · Object Lock GOVERNANCE 365d · SSE-S3 AES256 · Block Public Access all-on |
| Verification | object counts 4/4 match per tree · manifest round-trip identical · **16/16 sample re-hash passed** |

Local footprint unchanged: `cardiosentinel-runs` 2.3 G / 365 files,
`cardiosentinel-features` 16 G / 158, `cardiosentinel-data` 5.6 G / 261,
`artifacts` 8 K / 1 — all gitignored, all on one disk (`/dev/sda1`, 86% used).

**Restoring bytes is not enough.** S3 assigns its own `LastModified`, and mtimes
are load-bearing evidence here — immutability is asserted as *"20 files at
`2026-08-21T19:57:57`"*. The manifest carries `sha256 size mtime path`; a restore
must replay them:

```bash
while read -r sha size mtime path; do touch -d "@$mtime" "$path"; done < MANIFEST_SHA256.txt
```

## 8. Open defects and next steps

**Defects**

1. **13 stale tests** asserting the continuation root is absent (§6). Needs a PR.
2. **The T1 report generator is untracked** — it lives only in a scratch
   directory. Regenerating from a stale copy would silently revert the §9.2
   latency correction merged in #62.
3. `IMPLEMENTATION_PLAN.md` / `RESEARCH_SCOPE.md` still unrevised since
   2026-08-07 (§2).

**Next scientific steps, in order**

1. **T2 analysis execution** — step 3 of the T2 plan, gated on human approval.
2. **External validation strategy** — the milestone that decides whether any of
   this generalizes. Everything rests on 12 validation subjects from one dataset
   whose obvious second cohort, EDB, is provably contaminated with the first per
   `CROSS_DATASET_PROVENANCE.md`.
3. **Ablation package** — separate decision; each ablation needs new authorized
   runs. The standing constraints bar *reruns of canonical runs*, not new,
   separately-identified experiments.
4. **Paper assembly** — realistically a methodology and measurement-integrity
   paper with a worked application, not a performance paper.

**Standing constraints, still in force:** no M2/U1/T2 rerun · no T1 fold retry ·
no second continuation · never install, upgrade or downgrade packages in
`tactics` · patient identity selects a namespace and a calibrator and is never a
predictive feature · labels never determine memory-stream membership, ordering,
or update eligibility · do not access sealed TEST.

---

_Last refreshed: 2026-08-22, read-only pass against `origin/master` `1bbbd47`.
To refresh, ask Claude to re-run the audit and rewrite this file — nothing here
is meant to be trusted past its own "As of" line._
