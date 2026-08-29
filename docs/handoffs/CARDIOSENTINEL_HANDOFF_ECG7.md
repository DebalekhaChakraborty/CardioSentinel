# CardioSentinel — handoff to session "ECG 7"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG7.md and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (ServiceDesk etc., do NOT use for CardioSentinel) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |

`tactics` holds exactly the frozen 335-package set,
`installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`.
Never install, upgrade or downgrade anything in it. Torch is `2.13.0+cpu`, no
CUDA.

**Note on shell state:** the Bash working directory silently resets to
`/home/AI_POC` (the OUTER repo). **Always `cd` explicitly to the CardioSentinel
repo before any `git`/`gh`/`pytest` command.** This bit ECG 6 twice — a `git add`
and a whole `pytest` subset ran in the outer repo. Never run `git add -A`
anywhere near `/home/AI_POC`. Outer HEAD is
`086ee281370c1e49b2665d33f5a615989c1dc6da` and must stay that way.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

Ladder, frozen: **B4-B → P1-B → M1L → M2-G → U1 Platt calibration**.

Master is `c975ce709c2c6c1e91a4b64bb73637bd59aaac13`.

**One PR is open and unmerged: #32**, branch
`research/t2-execution-harness-v1`, head
`431bd158b7401466d76bce554b0c57c4c328911d`, CI green, MERGEABLE/CLEAN.

### Merged in ECG 6
- **PR #30** — U1 split retention decision + its denominator wording
  correction (→ master `997df407`).
- **PR #31** — T2 prospective protocol, its scientific-semantics closure, and
  the row-lineage hardening (→ master `c975ce70`).

### Open
- **PR #32** — T2 causal GRU/S4D models + canonical TRAIN-only harness.
  **Implements the science; does not execute it.** Awaiting human merge review.

## 2. What happened in ECG 6

Six authorization boundaries, in order:

1. **U1 human retention decision** — a *split* decision: calibration retained,
   symmetric window router rejected. PR #30.
2. **U1 denominator wording correction** — a real ambiguity, not cosmetic (§4).
3. **T2 prospective protocol** — design only. PR #31.
4. **T2 scientific-semantics closure** — full-timeline vs PRIMARY-mask, row
   roles, one continuous pass, exact architectures, corrected selection rule.
5. **T2 executable row-lineage hardening** — stable_id bound to the row.
6. **T2 models + canonical training harness** — PR #32.

## 3. Frozen digests

| Document | SHA-256 |
|---|---|
| `docs/T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md` | `6546086a55fe2c9c109f4121cdb6b42d4d53ce0112c9611eb895bd8c805cfefb` |
| `docs/T2_CANONICAL_TRAINING_EXECUTION_SPEC_V1.md` | `af6ebf1a6314edb86cce7aa88a6260dd1bd155fd0aebe472d3745b6c823b8054` |
| `docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` | `9d8436f2b7d2c303aeeb03e438c60fb8110f7d06d0bbd589f5be65ea8f80cb7b` |
| `docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md` | `d6235b477af278fe051822bdcccb54f985e4eceb0c6e92c1424f5e9d7d79b33b` |
| `docs/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | `da4a05b4e2e3dd633493b87a08ed369010fa91c9cac21d906980a658fcf2be47` |
| `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` | `a8ba6fad038ed0ec01156b6959239f489426d55db8ad73a0c704fd527e7db91c` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |
| P1 protocol / retention / P1-B lock | `f48ffc66…` / `7b403709…` / `796f00e3…` |
| Split manifest `protocols/splits/ltstdb_v1.json` (self / file) | `66e25d77…` / `74f055de…` |

## 4. U1 — the RETAINED decision (do not re-litigate)

**Split decision.** RETAINED: Platt calibration
`platt_logistic_on_recovered_logit`; subject-disjoint OOF Platt probabilities as
the downstream DEVELOPMENT input; the final all-VALIDATION Platt calibrator
(`a = 0.3715906808641229`, `b = −1.7662772879067046`) for genuinely unseen
subjects. **NOT RETAINED:** the symmetric window router at `c_star = 0.90`,
`u_star_dev` (`0.12763774358328017`), `u_star_deploy` (`0.12914217081334087`).

**Why the router was rejected.** The prespecified `asymmetric_abstention` guard
fired: positive-label escalation `0.5167375624190864` vs negative
`0.0800696045937263`, ratio **`6.453604523726777`** against bound `3.0`. The
calibration-agreement guard passed (`0.006683691656635168` vs `0.02`).

**The denominator, stated correctly — this was corrected once already:**
of the **21,628 positive-label windows in PRIMARY**, the router escalates
51.67 %, leaving **10,452 locally accepted**. Only **8** of those are
true-positive detections and **10,444** are false negatives, giving accepted
sensitivity **`8 / 10,452 = 0.0007654037504783774`**.
**21,628 is the population count, NOT the denominator** (`8/21,628` is a
different number, `0.000369890882189754`). A positive-label window is not a
true-positive detection. Never collapse these again.

## 5. T2 — the frozen protocol

**Question:** can causal longitudinal modelling across successive ECG windows
improve current-window ischemic evidence and temporal consistency?
**Output:** a causal temporal evidence score for the CURRENT window — not a
state machine, not a router, not calibrated uncertainty.

**T2 is not B4-C.** B4-C modelled the inside of one 10-s window and was
rejected; T2 models the sequence across windows at a 5-s stride. That rejection
says nothing about SSMs here.

### 5.1 The input — and the trap

`z_t` = **146 dims** (128 B4-B embedding + 18 physiology), from the **M1 full
stream memory cache** `cardiosentinel-features/m1-stream-memory-v2/{train,validation}`.

| | TRAIN | VALIDATION |
|---|---|---|
| Full replay timeline | **2,208,431** | **492,904** |
| PRIMARY mask | **2,143,599** | **473,897** |
| Non-PRIMARY | 64,832 (challenge 46,025 / other 18,807) | 19,007 (8,137 / 10,870) |
| Streams / records / subjects | 132 / 60 / 56 | 30 / 13 / 12 |
| Unavailable exact-flat | 0 | 6 |
| `stream_cache_sha256` | `d006c698017110bfd95774ca207036a820139779b95cf1b3f3a36c06efa779a4` | `a3e39137a04ebebb3b97ef6c6c614339c990a6041cf649a0ba6e3c2d43baae18` |
| `representation_content_sha256` | `e52a566fbc285a7a9f92715752dee43c020faa3550aaeb660f5f400dee07b5d3` | `b26a2d9b6150e6518dc2bfb394427dc93ae48a7cc3de30adcc3fefcc9f1f53ba` |

**🚩 THE P1 EMBEDDING CACHE IS NOT THE T2 SOURCE.**
`p1-b4b-embeddings-v1/train` holds **374,452 rows at exactly 3:1 negative
sampling** (280,839 = 3 × 93,613) and records a `training_selection_sha256`; its
VALIDATION side is unsampled. It is a *selection, not a timeline*, carries only
the 128-dim embedding, and has no ordering keys. Training on it would destroy
TRAIN temporal continuity while leaving VALIDATION intact. It is refused by path
marker, by digest, and 374,452 is refused as a TRAIN timeline length.

### 5.2 Context vs mask (the distinction that matters)

The **causal state context population is the FULL REPLAY TIMELINE**. **PRIMARY
is a LOSS/METRIC MASK** over that one replay — never a separate sequence.

| Role | `z_t` | State | Score | Direct BCE | PRIMARY metric | Challenge metric |
|---|---|---|---|---|---|---|
| AVAILABLE + PRIMARY | yes | yes | yes | **yes** | yes | no |
| AVAILABLE + CHALLENGE | yes | yes | yes | **no** | no | yes |
| AVAILABLE + OTHER non-primary | yes | yes | yes | **no** | no | no |
| UNAVAILABLE exact-flat | **no** | **no** | **no** | no | no | no |

**Gradient wording — do not regress.** It is FALSE to say "challenge rows are
not trained on": an available challenge `z_t` is label-blind causal context and
can influence a later PRIMARY loss through carried state. There is deliberately
**no `T2_CHALLENGE_TRAINED_ON` flag** and a test asserts the attribute does not
exist. Say only: identity never an input; labels never an input; **no direct
training loss**; never checkpoint/selection evidence; may be label-blind context.

### 5.3 Other frozen T2 facts

- Internal split **48 fit / 8 internal-dev** of the 56 TRAIN subjects, by
  `sha256("cardiosentinel-t2-internal-split-v1:" + subject)`, identity only.
  Digest **`54f8091ee7d4620ab6e24aaa32b121874b6a1610003e3df63f94f9727618e28e`**.
  Internal-dev: `s2008 s2017 s2042 s2046 s2049 s2050 s2063 s2064`.
- Stream unit `(record_id, channel_index)`, ordered by persisted **`start_sample`**
  (alias `window_start_samples := persisted start_sample`).
- **TBPTT 256** windows (1,280 s). State **MUST carry** across chunk boundaries
  and **MUST be detached** there. Resets only at real stream boundaries.
- Loss: BCE-with-logits, `pos_weight = N_neg/N_pos` from the **48-subject fit
  partition only**; sum over direct-loss rows ÷ their count per optimiser step.
- AdamW, lr 3e-4, wd 1e-4, ≤10 epochs, clip 1.0, seed 2026; checkpoint/early-stop
  on internal-dev pooled AUPRC, patience 3, **exact tie keeps the earlier epoch**.
- Threshold: exact max-F1, **highest-threshold tie-break**, internal-dev only.
- Selection (outer VALIDATION only): `d_pooled >= 0.002` → pooled AUPRC; else
  `d_macro >= 0.002` → subject-macro; else lower parameter count; else **GRU**.
  Exactly `0.002` is **not** a tie. Latency is never a selection input.
- Subject bootstrap 1000 / seed 2026 / subject unit. Never windows.

## 6. T2 — the implemented harness (PR #32, unmerged)

New files: `t2_models.py`, `t2_timeline.py`, `t2_training.py`,
`t2_persistence.py`, `t2_evaluation.py`, `t2_development_run.py`, the execution
spec doc, and `tests/neural/test_t2_models.py` + `test_t2_execution_harness.py`.

**Frozen parameter counts, asserted not discovered — construction STOPS if
wrong:** GRU **59,521**, S4D **45,313** (ratio 0.7613, inside [0.5, 2.0]).

S4D reuses B4-C's `DiagonalGatedSSMBlock` conventions verbatim (complex
`λ = complex(-exp(log_decay), frequency)`, ZOH, `expm1` input gain, complex `C`,
real part summed over state, zero-init real per-channel `D`, pre-LayerNorm, SiLU
on the gate branch only, residual with branch dropout, state dim 16). **It is
not Mamba** — the transition is time-invariant and input-independent. The only
divergence from B4-C is that state is carried in and out instead of discarded.

**Canonical claim:** `T2_temporal_v1` / attempt `t2-v1-training` / run root
`cardiosentinel-runs/phase8-t2-development-v1/`. Not yet created — nothing is
consumed.

**CLI:** one route only —
`--execute-canonical-training --expected-git-sha <MERGED_SHA>`. No `--arm`,
`--epoch`, `--lr`, `--batch-size`, `--tbptt`, `--seed`, `--device`,
`--threshold`, `--retry`, `--force`, `--validation`, `--test`.
Today it runs preflight and **stops before claiming** (exit 2).

**Outer VALIDATION is structurally disabled:**
`T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED = False` in `t2_persistence.py`,
defined in exactly one place, no setter, no env var, no flag. Every entry point
refuses first; the CLI route exits 3.

## 7. THE OPEN GATE — start here

**Nothing is authorized right now beyond human review of PR #32.**

Likely next authorizations, in order:
1. Human merge review of **PR #32**.
2. Then, separately, the **one-shot canonical TRAIN run** — which will claim
   `t2-v1-training` and consume the attempt.
3. Then human review of the TRAIN-only artifacts.
4. Only then an **activation change set** flipping
   `T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED` for the one-shot outer VALIDATION.
5. TEST (T1/T2) requires its own separate authorization and is not implied by
   any of the above.

**Do NOT** begin T1, choose a router, or run outer VALIDATION automatically.

## 8. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed: do
  not delete, reset, rename, re-root or reseed it. Stop and report. This applies
  to `phase7-u1-development-v1/` and will apply to
  `phase8-t2-development-v1/` the moment it exists.
- **No M2 rerun. No U1 rerun.** M2-0, M2-G and U1-v1 are immutable.
- Keep scratch files OUTSIDE the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace but is NEVER a predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

## 9. Working preferences and hard-won lessons

- Read-only monitoring for long runs; **never** restart/retry a canonical run,
  never kill for slowness or high RSS.
- **Launch canonical runs with Bash `run_in_background: true`.** The foreground
  tool timeout caps at 10 min.
- Use `git commit -F <file>` with the message file in the scratchpad.
- **Never run `ruff format` over a whole directory** — format only files you
  changed. CI runs `ruff check .` and `pytest -q`.
- `gh pr edit --body-file` fails on this `gh`; use
  `gh api -X PATCH repos/<owner>/<repo>/pulls/N -F body=@file`.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`.
- **CI monitors must wait for ALL jobs** — exit only when none is
  `IN_PROGRESS`/`QUEUED`/`PENDING`.
- Test-suite counts at end of ECG 6: full **1870 passed, 1 skipped** (~11 min);
  `-k "m1 or m2 or u1 or t2"` **1128 passed, 1 skipped, 742 deselected** (~9 min);
  T2 protocol **91**, T2 models + harness **96**.
- **Substring assertions on wrapped markdown are brittle** — a phrase that
  straddles a line break fails silently. Normalise whitespace first
  (`" ".join(text.split())`). This bit ECG 6 once.
- **Do not materialise the frozen row count in a test fixture.** A synthetic
  2,208,431 × 146 array wrote **15 GB** of pytest temp before it was killed. The
  frozen-count gate is `require_frozen_row_count()`, enforced only on the
  canonical path (`root is None`); fixtures pass a root and the identity records
  `frozen_row_count_enforced: False`.
- **Aggregate counts are not an identity.** Equal row count with different
  membership is refused; bind the exact digest and the exact stable-id sequence.
- **Put the identity gate in the caller, not the reader.**
- Test seams that inject past a component hide defects in that component. Drive
  the real component against synthetic on-disk fixtures.
- Assert state-carry equivalence with `allclose`, not bitwise: chunking changes
  the sequence length a BLAS kernel sees, so float32 reassociation moves the
  last ulp (~2e-7). Claiming bit-identity would be false.
- Prove a detach severs the graph **by contrast** (`grad_fn` present vs absent).
  `tensor.grad is None` passes vacuously on a non-leaf tensor.
- Long reports end with the exact mandated closing block when one is specified.

## 10. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG3
handoff: a concurrent session installed distributions into the then-shared
scientific interpreter while the canonical M1-v2 run was executing. Whether that
process loaded any added distribution **cannot be proven retrospectively**; all
read-only evidence is consistent with no effect. **M1-v2 remains the canonical
frozen M1 development evidence; do not rerun or modify it.**

The ECG3 outer-repo index reconstruction also stands: that index was
**reconstructed, not recovered**, and is still worth a human glance. Outer HEAD
`086ee281370c1e49b2665d33f5a615989c1dc6da` was not changed in ECG 4, 5 or 6.

M2 recovery2 and the U1 canonical run both ran clean. No canonical T2 run has
been executed, and no T2 attempt directory exists.
