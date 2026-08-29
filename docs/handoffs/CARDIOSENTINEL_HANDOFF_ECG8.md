# CardioSentinel — handoff to session "ECG 8"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG8.md and continue.
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
repo before any `git`/`gh`/`pytest` command.** Never run `git add -A` anywhere
near `/home/AI_POC`. Outer HEAD is
`086ee281370c1e49b2665d33f5a615989c1dc6da` and must stay that way.

The remote prints "This repository moved" on every push (renamed to
`CardioSentinel-AI`). Pushes succeed; it is noise, not an error.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

Ladder, frozen: **B4-B → P1-B → M1L → M2-G → U1 Platt calibration**.

Master is `c975ce709c2c6c1e91a4b64bb73637bd59aaac13` — **unchanged since ECG 6**.

**One PR is open and unmerged: #32**, branch
`research/t2-execution-harness-v1`, head
`951503ea64397e8ffd0160dd2023584149a45280`, CI green, MERGEABLE/CLEAN,
+11,841 lines over 14 files. **Nothing has been merged in ECG 7.**

## 2. What happened in ECG 7

Four authorization boundaries, all on PR #32, all implementation — **no science
was executed**:

1. **T2 canonical training harness — execution assembly** (→ `2620da3`, plus
   `8eccdd9` and `62b56c3` fixing the tests' CI seams). The reviewed harness
   implemented every primitive and then raised unconditionally; the canonical
   route had no body. It has one now.
2. **T2 final execution-governance + outer-evidence closure** (→ `64ff267`).
   Absolute run root, actual-device execution, current-arm failure attribution,
   row accounting, the one-shot outer claim, the per-row outer evidence store
   and stream-aware temporal descriptors.
3. **T2 final provenance / canonical-API closure** (→ `951503e`). One authorized
   commit end to end, top-level device cross-binding, a narrowed public outer
   API, and complete outer failure receipts.
4. This handoff.

Commits on the branch, oldest first:
`431bd15` → `2620da3` → `8eccdd9` → `62b56c3` → `64ff267` → `951503e`.

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
| Feature corpus `ltstdb-baseline-v1` | `f18785d520828cb171482926922346dda824c8868ed4b7f9be45897cd71d6eb5` |
| M1 TRAIN stream cache / representation | `d006c698…` / `e52a566f…` |
| M1 VALIDATION stream cache / representation | `a3e39137…` / `b26a2d9b…` |
| T2 internal 48/8 split | `54f8091ee7d4620ab6e24aaa32b121874b6a1610003e3df63f94f9727618e28e` |

Both T2 documents are byte-identical to the digests above. **No scientific rule
changed anywhere in ECG 7.**

## 4. T2 — the frozen science (do not re-litigate)

**Question:** can causal longitudinal modelling across successive ECG windows
improve current-window ischemic evidence and temporal consistency?
**Output:** a causal temporal evidence score for the CURRENT window.

- `z_t` = **146 dims** (128 B4-B embedding + 18 physiology) from the **M1 full
  stream memory cache** `cardiosentinel-features/m1-stream-memory-v2/{train,validation}`.
  TRAIN 2,208,431 rows / 132 streams / 60 records / 56 subjects, 0 unavailable.
  VALIDATION 492,904 rows / 30 streams / 13 records / 12 subjects, **6
  unavailable exact-flat**. PRIMARY masks 2,143,599 and 473,897.
- **🚩 The P1 embedding cache is NOT the T2 source** (3:1 sampled selection,
  374,452 TRAIN rows). Refused by path marker, by digest, and by row count.
- **The causal context population is the FULL REPLAY TIMELINE; PRIMARY is a
  LOSS/METRIC MASK over that one replay**, never a separate sequence.
- Arms: `causal_gru_longitudinal_v1` (**59,521** params) and
  `causal_s4d_longitudinal_v1` (**45,313**). Counts are asserted, not
  discovered; construction STOPS if wrong. S4D is **not Mamba**.
- Internal split **48 fit / 8 internal-dev** of the 56 TRAIN subjects, identity
  digest only. Internal-dev: `s2008 s2017 s2042 s2046 s2049 s2050 s2063 s2064`.
- TBPTT **256**; state carries across frontiers and is **detached** there;
  resets only at real stream boundaries.
- BCE-with-logits, `pos_weight = N_neg/N_pos` from the **48-subject fit
  partition only**; AdamW lr 3e-4, wd 1e-4, ≤10 epochs, clip 1.0, seed 2026.
- Checkpoint/early-stop on internal-dev pooled AUPRC, patience 3, **exact tie
  keeps the earlier epoch**. Threshold: exact max-F1, highest-threshold
  tie-break, internal-dev only.
- Selection (outer VALIDATION only): `d_pooled >= 0.002` → pooled AUPRC; else
  `d_macro >= 0.002` → subject-macro; else lower parameter count; else **GRU**.
  Exactly `0.002` is **not** a tie. Latency is never a selection input.
- Subject bootstrap 1000 / seed 2026 / **subject** unit. Never windows.
- **Gradient wording — do not regress.** It is FALSE to say "challenge rows are
  not trained on": an available challenge `z_t` is label-blind causal context
  and can influence a later PRIMARY loss through carried state. There is no
  `trained_on` field anywhere and a test asserts it. Say only: identity never an
  input; labels never an input; **no direct training loss**; never
  checkpoint/selection evidence; may be label-blind context.

## 5. T2 — what PR #32 now contains

New modules: `t2_models.py`, `t2_timeline.py`, `t2_training.py`,
`t2_persistence.py`, `t2_evaluation.py`, `t2_outer_evidence.py`,
`t2_development_run.py`. Tests: `t2_fixtures.py` plus four `test_t2_*.py`
files. **It implements the science; it does not execute it.**

### 5.1 The canonical TRAIN route — assembled

`execute_canonical_training(expected_git_sha)` is preflight plus
`_execute_training_attempt(checks, T2TrainingSources())`. No unconditional stop
remains. **No activation switch** — human authorization is the exact merged Git
SHA through `--expected-git-sha`.

Choreography: preflight (Git, protocol bytes, spec bytes, claim absence) →
runtime **START** → claim `phase8-t2-development-v1/t2-v1-training` → validate
the real TRAIN store → resolve the real target authority → 48/8 split → select
the execution device once → FIT-only class weight → both arms in frozen
`T2_ARMS` order (each with **pre-model-construction** and
**pre-checkpoint-promotion** observations) → one retained checkpoint and one
frozen threshold per arm → result → lock → **COMPLETION** → COMPLETE.

The real store and target authority are opened **after** the claim, so a
corrupted input consumes the attempt honestly.

### 5.2 Byte-level input verification

`T2Timeline` opens through **`m1_experiment.load_stream_store`** — the strongest
M1 validator, the one M2 and U1 use. A `representation.npy`, `stable_id.npy` or
`start_sample.npy` mutated under an untouched manifest is refused.
`require_frozen_stream_identity` (canonical path only) then refuses a store that
is self-consistent but is not the *promoted* one.

### 5.3 The target-family provider

`resolve_timeline_target_families` joins each timeline row to exactly one
persisted family in the frozen LTSTDB corpus, **record by record**, reading only
metadata members — never the 40-dim feature matrix, never a raw annotation,
never `.stb`, never a context flag. Families and roles are `uint8` codes
(2.2 MB, versus 88 MB for `<U40` roles).

### 5.4 Frontier optimisation

One frontier is one optimiser step, or none. The weighted BCE sum accumulates
across every length group and is divided **once** by the frontier's total
direct-loss count. Groups are keyed by the **compacted available** length, not
the raw slice length. State is detached at every frontier, loss-bearing or not.

### 5.5 The one-shot outer VALIDATION — implemented, gate still FALSE

`T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED = False` in `t2_persistence.py`, one
definition, no setter, no env var, no flag. The public entry point refuses as
its **first statement**; the CLI route exits 3.

Behind the gate the complete body exists: claim `t2-v1-outer-validation`
(sibling of the TRAIN attempt), status/result/lock artifacts, an additive
failure receipt outside the claim, per-row evidence for both arms, and
`validate_canonical_t2_outer_validation_attempt`.

**Public API is `execute_canonical_outer_validation(expected_git_sha)` and
nothing else.** Fixture injection lives on the private
`_outer_validation_worker(expected_git_sha, *, run_root, training_attempt_id,
validation_root, corpus_manifest)`. The former `open_validation_timeline` /
`load_validation_labels` raw loaders are gone from the public surface — flipping
the activation constant alone unlocks no way to open VALIDATION without a claim.

### 5.6 Per-row outer evidence (this is what T1 consumes)

`t2_outer_evidence.py`. Row identity npz + one score npz per arm + a
self-digesting manifest. The score is named exactly what it is:
**`uncalibrated_temporal_model_score` = `sigmoid(current_window_t2_logit)`** —
never a calibrated probability, confidence or uncertainty. Unavailable rows
carry `score_present=false` with a NaN **storage sentinel**; a finite value
behind a false mask, or a NaN behind a true one, is refused.
`selected_arm_scores()` + `row_index_by_stable_id()` let T1 read the selected
arm without re-running the one-shot outer attempt.

### 5.7 Provenance invariants added in ECG 7

- **Absolute run root**: `T2_RUN_ROOT = REPOSITORY_ROOT / "cardiosentinel-runs"
  / "phase8-t2-development-v1"`. A foreign cwd neither moves the claim nor
  bypasses a consumed one.
- **Actual device**: `canonical_execution_device()` = `cuda:0` if available else
  `cpu`, selected once, no override. Everything scientific runs there.
  Provenance carries `declared_execution_device` **and** the observed
  `model_parameter_device`; a record claiming CUDA over a CPU model is refused.
  Determinism failure STOPS — no silent CPU fallback.
- **One authorized commit**: `authorized_git_sha` travels preflight → result →
  provenance → lock. `require_authorized_git_identity` re-reads HEAD once,
  immediately before promotion. Drift consumes the attempt.
- **Row accounting**: PRIMARY *target* population (label authority) is distinct
  from PRIMARY *scored* population (target ∧ `score_present`), and
  `scored + unavailable == target` is enforced, for PRIMARY and for the full
  timeline.
- **Stream-aware descriptors**: segmented by `(record_id, channel_index)`; runs
  never cross a stream boundary; an unavailable gap breaks a *descriptive* run
  (the model state still carries); non-primary AVAILABLE predictions stay in
  continuity; the transition denominator is full physical timeline exposure.

## 6. THE OPEN GATE — start here

**Nothing is authorized right now beyond human merge review of PR #32.**

Likely next authorizations, in order:

1. **Human merge review and merge of PR #32.**
2. Then, separately, the **one-shot canonical TRAIN run** — which claims
   `t2-v1-training` and consumes the attempt. Launch with Bash
   `run_in_background: true`; it will take hours.
3. Then human review of the TRAIN-only artifacts.
4. Only then an **activation change set** flipping
   `T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED`. That change set should be tiny:
   persistence, row evidence, descriptors, metrics, selection and failure
   semantics all already exist.
5. Then the one-shot outer VALIDATION run, then its review.
6. **T1** consumes the selected T2 arm from the per-row evidence store.
7. TEST (T1/T2) requires its own separate authorization and is implied by none
   of the above.

**Do NOT** begin T1, choose a router, or run outer VALIDATION automatically.

## 7. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed: do
  not delete, reset, rename, re-root or reseed it. Stop and report. This applies
  to `phase7-u1-development-v1/` and will apply to both
  `phase8-t2-development-v1/t2-v1-training` and `.../t2-v1-outer-validation`
  the moment either exists. **Neither exists today.**
- **No M2 rerun. No U1 rerun.** M2-0, M2-G and U1-v1 are immutable.
- Keep scratch files OUTSIDE the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace but is NEVER a predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

## 8. Working preferences and hard-won lessons

- Read-only monitoring for long runs; **never** restart/retry a canonical run,
  never kill for slowness or high RSS.
- **Launch canonical runs with Bash `run_in_background: true`.** The foreground
  tool timeout caps at 10 min and a timeout kill would consume the attempt.
- Use `git commit -F <file>` with the message file in the scratchpad.
- **Never run `ruff format` over a whole directory** — format only files you
  changed. CI runs `ruff check .` and `pytest -q`.
- `gh pr edit --body-file` fails on this `gh`; use
  `gh api -X PATCH repos/<owner>/<repo>/pulls/N -F body=@file`.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`.
- **CI monitors must wait for ALL jobs** — exit only when none is
  `IN_PROGRESS`/`QUEUED`/`PENDING`.
- Test-suite counts at end of ECG 7: full **2020 passed, 1 skipped** (~14 min);
  `-k "m1 or m2 or u1 or t2"` **1278 passed, 1 skipped, 742 deselected**
  (~13 min); T2 protocol **91**, models **28**, execution harness **68**,
  canonical TRAIN route **70**, outer governance **49**, provenance closure
  **31**.
- **CI is not the scientific interpreter.** The frozen 335-package digest
  belongs to `venvs/tactics` alone, so any test that drives the real runtime
  sentinel fails in CI. Use the reviewed M2 canonical-runner seam: fake
  `observe_runtime_identity` / `require_runtime_identity` with a frozen check.
  This cost two CI round-trips in ECG 7.
- **`monkeypatch.undo()` tears down every seam, not just yours.** A test that
  repaired an injected fault that way also removed the frozen-runtime and
  clean-Git fixtures. Return an `armed` switch and disarm that instead.
- **Patch `git_provenance` in every module that imported the name**, not only
  its source module: `t2_development_run.require_expected_git_sha` resolves it
  in its own namespace.
- **The synthetic fixture must be genuinely valid.** `tests/neural/t2_fixtures.py`
  writes a real M1 stream cache (real self-digests, real content digests, real
  standardizer) and a real LTSTDB-shaped corpus, using the **real frozen subject
  identities** so `assign_internal_split` produces the frozen 48/8 digest. That
  is what gives the mutation tests their force.
- **Do not materialise the frozen row count in a fixture.** A synthetic
  2,208,431 × 146 array wrote 15 GB of pytest temp once. Fixtures pass a root;
  the frozen-count gate fires only on the canonical path (`root is None`).
- **Aggregate counts are not an identity.** Bind the exact digest and the exact
  stable-id sequence.
- **Put the identity gate in the caller, not the reader.**
- Test seams that inject past a component hide defects in that component. Drive
  the real component against synthetic on-disk fixtures.
- Assert state-carry equivalence with `allclose`, not bitwise (~2e-7 drift).
- Prove a detach severs the graph **by contrast** (`grad_fn` present vs absent).
- **Substring assertions on wrapped markdown are brittle** — normalise
  whitespace first (`" ".join(text.split())`).
- Long reports end with the exact mandated closing block when one is specified.

## 9. Real defects this implementation surfaced (do not re-introduce)

These were found by building, not by review. Each is now pinned by a test.

1. **Lazy determinism split the arms.** `seed_everything` was called inside the
   first arm's construction, so arm A observed `deterministic_algorithms: False`
   and arm B `True`, and `require_single_runtime` correctly refused a comparison
   that was never actually mixed. Determinism is now established once, before
   the first runtime reading.
2. **`primary_mask` was derived from the ROLE mask**, which demotes an
   unavailable row to `UNAVAILABLE`. That silently equated the PRIMARY target
   and PRIMARY scored populations — the exact conflation the accounting exists
   to prevent — and the accounting only closed because the discrepancy had been
   absorbed. It now comes from the label authority alone.
3. **The failure receipt could name the arm that worked.** Attribution came from
   `arms_completed[-1]`; a GRU that completed followed by an S4D that failed
   produced a receipt blaming the GRU.
4. **The top-level lock re-read Git and the runtime independently**, so a result
   and a lock could name different commits, and the lock could claim a device
   nothing ran on.

## 10. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG3
handoff: a concurrent session installed distributions into the then-shared
scientific interpreter while the canonical M1-v2 run was executing. Whether that
process loaded any added distribution **cannot be proven retrospectively**; all
read-only evidence is consistent with no effect. **M1-v2 remains the canonical
frozen M1 development evidence; do not rerun or modify it.**

The ECG3 outer-repo index reconstruction also stands: that index was
**reconstructed, not recovered**, and is still worth a human glance. Outer HEAD
`086ee281370c1e49b2665d33f5a615989c1dc6da` was not changed in ECG 4–7.

M2 recovery2 and the U1 canonical run both ran clean. **No canonical T2 run of
any kind has been executed, and no T2 attempt directory exists.**
