# CardioSentinel — handoff to session "ECG 9"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG9.md and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (ServiceDesk etc., do NOT use for CardioSentinel) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` (renamed `CardioSentinel-AI`) |

`tactics` holds exactly the frozen 335-package set,
`installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`.
Never install, upgrade or downgrade anything in it. Torch is `2.13.0+cpu`, no CUDA,
so `canonical_execution_device()` resolves to `cpu`.

**Note on shell state:** the Bash working directory silently resets to
`/home/AI_POC` (the OUTER repo). **Always `cd` explicitly to the CardioSentinel
repo before any `git`/`gh`/`pytest` command.** This bit twice in ECG 8: once a
relative `ls` reported the outer-validation attempt as missing when it existed,
and once `gh pr view` failed with "no GitHub remotes". Never run `git add -A`
anywhere near `/home/AI_POC`. Outer HEAD is
`086ee281370c1e49b2665d33f5a615989c1dc6da` and must stay that way.

The remote prints "This repository moved" on every push. Noise, not an error.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

Ladder, frozen: **B4-B → P1-B → M1L → M2-G → U1 Platt calibration → T2
`causal_s4d_longitudinal_v1`** → now **T1 causal episode-state**.

Master is **`b3004da9dcd8e7462d69eac81eb82ca9da86b8cb`** (merge of PR #34).

**T2 IS COMPLETE AND CLOSED.** Both canonical T2 attempts have been executed and
consumed. The T2 retention decision is merged.

**One PR is open and unmerged: #35 (T1 protocol)** — see §6. If §6 says the PR was
not yet opened when this handoff was written, check
`gh pr list --state open` first.

## 2. What happened in ECG 8

Eight authorization boundaries. **This was the session where T2 actually ran.**

1. **PR #32 discovered already merged.** ECG 8 opened with the ECG 8 handoff
   claiming #32 was open; it had in fact been merged. Local master was
   fast-forwarded only.
2. **T2-v1 canonical TRAIN executed** (`t2-v1-training`, ~30 min, both arms).
   COMPLETE, verifier PASS.
3. **T2 TRAIN temporal-cadence forensic audit** — resolved `frontier_count: 135`.
4. **T2 outer-validation activation change set** → PR #33, merged as `b0f189a5`.
5. **T2-v1 one-shot canonical OUTER VALIDATION executed**
   (`t2-v1-outer-validation`, ~11 min). COMPLETE, verifier PASS,
   `selected_arm: causal_s4d_longitudinal_v1`.
6. **T2 human retention decision** → PR #34, merged as `b3004da9`.
7. **T2 retention test/identity hardening** (same PR #34, second commit).
8. **T1-v1 prospective protocol** → PR #35, in progress at handoff time.

## 3. Frozen digests

| Document / artifact | SHA-256 |
|---|---|
| `docs/T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md` | `6546086a55fe2c9c109f4121cdb6b42d4d53ce0112c9611eb895bd8c805cfefb` |
| `docs/T2_CANONICAL_TRAINING_EXECUTION_SPEC_V1.md` | `af6ebf1a6314edb86cce7aa88a6260dd1bd155fd0aebe472d3745b6c823b8054` |
| `docs/T2_TRAIN_ARTIFACT_REVIEW_AND_OUTER_ACTIVATION_V1.md` | `d2065deaef173fd76681c5babcd1a6f16b51e2edd29b0436a24d4853fb7a479c` |
| `docs/T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md` | `4846921135b0ac83ceb40a0db063c2e4a3b2520971f279abe4f0c517c4f7dd20` |
| `docs/T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md` | `ef044754020b1756ea7aae5fa1b747c5ba6fc0c8cd70d52e73185555897d70d4` |
| `docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md` | `d6235b477af278fe051822bdcccb54f985e4eceb0c6e92c1424f5e9d7d79b33b` |
| `docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` | `9d8436f2b7d2c303aeeb03e438c60fb8110f7d06d0bbd589f5be65ea8f80cb7b` |
| `docs/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | `da4a05b4e2e3dd633493b87a08ed369010fa91c9cac21d906980a658fcf2be47` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |
| Feature corpus `ltstdb-baseline-v1` | `f18785d520828cb171482926922346dda824c8868ed4b7f9be45897cd71d6eb5` |
| Split `protocols/splits/ltstdb_v1.json` | `66e25d77b6aaa25502974b4b60667b4c4b24d649bf9493666827c747a385ced7` |
| U1 OOF evidence store | `b95f484c9a7b08447f5a5d4330528136e040cf05acb9e2f7e54305e20bdffcba` |
| M1 TRAIN stream cache / representation | `d006c698…` / `e52a566f…` |
| M1 VALIDATION stream cache / representation | `a3e39137…` / `b26a2d9b…` |
| T2 internal 48/8 split | `54f8091ee7d4620ab6e24aaa32b121874b6a1610003e3df63f94f9727618e28e` |

## 4. T2 — the completed evidence (immutable, do not re-derive)

Attempt `t2-v1-training` (COMPLETE, verifier PASS):

| | |
|---|---|
| Top-level result | `ff9258f95631405b6705811d638d754400a067be4c1a43bb9d52021bb246adb8` |
| Experiment lock file / self-digest | `37e633a3…9cfc8` / `d8de03554931fe65a6f1c1242d80c1c95f1a6a26f93b8013cff5bc221a92202f` |
| Authorized TRAIN commit | `f4759e2a97d17db26cb6a6b7c0e9b6207eb0b045` |
| GRU checkpoint / lock file / lock self | `027048c5…0fa82b` / `61c50911…1274ad` / `fab35e12…3bd9a5` |
| S4D checkpoint / lock file / lock self | `63ccfbe0…a6722e` / `a9807515…59f8c7` / `a51ad25e…6f5139` |
| GRU threshold / S4D threshold | `0.8328019380569458` / `0.8972153067588806` |

TRAIN: GRU best epoch 1, internal-dev AUPRC `0.6285039007027243`, early-stopped
at 4 epochs. S4D best epoch 10, internal-dev AUPRC `0.6402892809361228`, ran the
full budget. FIT 87,254 pos / 1,793,332 neg, `pos_weight = 20.553006165906435`.

Attempt `t2-v1-outer-validation` (COMPLETE, verifier PASS):

| | |
|---|---|
| Outer result | `c58ed40dac753157b00ce6c70eb52fe903ecee72a5ef84e40932c1a80e259dbf` |
| Outer lock file / self-digest | `54a0ca54…4a68c` / `f90b93afc6ba94d76441eb789de924c1256c76d03c8dd8c4eea22014e4c65d9c` |
| Row-evidence manifest / content | `c76453b8…4949` / `2240ca683fbcb790609c47f4a82af85250abb281fbbb9751dc74607a4eb591ca` |
| Authorized outer commit | `b0f189a57bea8bd28884e7e40be50136fd6e2927` |

Selection terminated at **STAGE 1**: GRU pooled outer PRIMARY AUPRC
`0.29486969381230116` vs S4D `0.388084635785268`, difference
`0.09321494197296681` against the frozen `0.002` boundary.
`selected_arm = causal_s4d_longitudinal_v1`.

Row accounting closes exactly: 492,904 = 492,898 scored + 6 unavailable;
PRIMARY 473,897 = 473,897 scored + 0 unavailable.

**Recorded T2 limitations that T1 must respect, not repair:**
- S4D predictions are temporally **more fragmented** than GRU at their frozen
  thresholds: 1787 runs vs 1081, median run 10.0 s vs 25.0 s, isolated
  single-window positive fraction 0.49636 vs 0.15911, 5.21627 vs 3.15664
  transitions/hour.
- S4D cold-start sensitivity is **0.0** in 0–5 min, 0.18673 in 5–60 min, 0.29797
  beyond.
- S4D is **worse** on RATE FPR (0.20551 vs 0.18983) and **better** on AXIS FPR
  (0.018333 vs 0.029). Conduction 0 FP over 164 rows, descriptive only.

## 5. The T2 retention decision (merged, immutable)

`src/cardiosentinel/neural/t2_selection.py` binds it.

- Retained: `causal_s4d_longitudinal_v1`. Comparator: `causal_gru_longitudinal_v1`,
  preserved immutable — the validator refuses if either arm leaves the evidence.
- **The retained object is the CONTINUOUS score**
  `uncalibrated_temporal_model_score = sigmoid(current_window_t2_logit)`.
- `T2_RETAINED_THRESHOLD_IS_T1_POLICY = False` and
  `T2_RETAINED_THRESHOLD_MAY_SELECT_T1_STATE = False`. The S4D threshold
  `0.8972153067588806` is T2 experiment/reporting evidence **only**.
- `T2_RETENTION_STATISTICAL_SIGNIFICANCE_CLAIM = False` — no prospective paired
  superiority procedure was frozen, so none is computed after the fact.
- `T2_RERUN_PERMITTED = False`, `T2_EXTENDED_TRAINING_PERMITTED = False`.
- Outer VALIDATION is **development evidence**, not unseen generalization.
- `supports_t1_without_rerunning_outer_validation = true`.

## 6. THE OPEN GATE — start here

**PR #35 `research/t1-state-protocol-v1` — T1-v1 prospective protocol.**

Three files: `docs/T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md`,
`src/cardiosentinel/neural/t1_protocol.py`,
`tests/neural/test_t1_protocol.py` (68 tests).

At handoff time the quality gauntlet was mid-run (T1 68 passed, upstream
selection/protocol suites 270 passed, subset and full pytest still running), and
the commit/push/PR/CI steps may or may not have completed. **Check the actual
state before assuming**: `gh pr list --state open`, `git log --oneline -3` on the
branch, and `git status --porcelain`.

Likely next authorizations, in order:

1. Human review and merge of the T1 protocol PR.
2. Then a **T1 execution specification** (the harness design), separately
   authorized.
3. Then the T1 development run: full-timeline OOF calibration assembly, 12-fold
   LOSO policy selection, cross-fitted OOF evidence.
4. Then human review of T1 development evidence, then a T1 retention decision.
5. Then, separately, the selective edge/cloud routing layer.
6. TEST (B4/T1/T2) requires its own separate authorization and is implied by
   none of the above.

**Do NOT begin T1 execution, choose a router, or open TEST automatically.**

## 7. T1-v1 — the frozen protocol (do not re-litigate)

**T1 is a deterministic causal state machine**, not a model, calibrator,
smoother, relabelled T2 threshold, LLM or router.

- States: **NORMAL / WATCH / EVENT / RECOVERY**, initial NORMAL, **per-stream**
  on `(record_id, channel_index)`. No cross-record/channel/subject carry.
  Patient-level multi-channel fusion is undefined in V1.
- Runs over the FULL VALIDATION timeline: 492,904 rows / 30 streams / 12
  subjects, stride 1250 samples, window 2500, 250 Hz.
- **Full-timeline OOF calibration contract (the key design rule).** T1 must NOT
  use `target_family` to decide whether calibrated evidence exists — that would
  make a runtime transition depend on evaluation annotation. Instead: read
  retained M2-G full-replay scores, resolve subject, select that subject's
  already-fitted U1 LOSO Platt calibrator, and apply it to EVERY scored M2-G row
  of that subject, label-blind, with the frozen recovered-logit transform and
  clamp `1e-7`. **Not a fit, not a family reselection, not a U1 rerun.**
- The all-VALIDATION **deployment calibrator is FORBIDDEN** for development on
  these twelve subjects (it was fitted on all of them).
- Allowed row inputs: `stable_id`, M2-G detector score, `d_t` at
  **`0.7554003000259399`**, `p_t`, `u_t`, `s_t`, availability, elapsed stream
  time, elapsed state time.
- Forbidden transition inputs: label, target_family, subject outcome, episode
  identity, any future row/score, GRU score, S4D binary decision, T2 reporting
  threshold, `u_star_dev`, `u_star_deploy`, challenge identity, M2 gate outcome,
  `m2_update_admitted`, any TEST quantity.
- Thresholds are **generated prospectively**, never hand-chosen:
  `Q_WATCH = (0.90, 0.95)`, `Q_EVENT = (0.99, 0.995)`, applied separately to the
  `p_t` and `s_t` distributions of **FIT-subject PRIMARY background negatives**,
  via exact empirical order statistic `k = ceil(q*N)` 1-based, ties on
  `stable_id`, **no interpolation**.
- Three persistence profiles (FAST / BALANCED / CONSERVATIVE) → **12 candidate
  policies per fold**. WATCH entry is immediate on one row.
- Evidence: WATCH = `d_t OR p>=p_watch OR s>=s_watch`; mature EVENT =
  `d_t AND p>=p_event AND s>=s_event`; NORMAL = `not d_t AND p<p_watch AND
  s<s_watch`; anything else is ambiguous/WATCH-level.
- **Cold start** (`age < 300 s`): EVENT = `d_t AND p>=p_event` only — the S4D
  term is not required, on the longer `cold_event_confirm_windows` budget. This
  is **not** a T2 repair.
- Unavailable row: hold state, advance state time one stride, **reset all
  streaks**, no transition, no imputation/forward-fill/synthetic zero.
- **RECOVERY never automatically becomes WATCH.**
- Development: **12-fold LOSO** over the twelve VALIDATION subjects
  (`s2004 s2005 s2019 s2020 s2023 s2031 s2057 s2058 s2059 s3068 s3072 s3073`).
  Held-out labels stay closed until that fold's policy is frozen. No fold retry.
- Selection: pooled episode F1 → pooled PRIMARY window MCC → false EVENT onsets
  per hour → EVENT exposure fraction → higher `q_event` → higher `q_watch` →
  CONSERVATIVE before BALANCED before FAST. Tolerance `1e-6`. No challenge, no
  latency, no weighted composite.
- One-to-one episode matching, earliest unmatched overlapping run — deliberately
  penalises overmerged EVENT runs.
- Bootstrap: 1000 replicates, seed 2026, unit **subject**, no policy reselection.
- **Development-optimism disclosure**: subject-disjoint for T1 policy selection
  ONLY. The retained S4D arm was itself selected on the full upstream VALIDATION
  population, so T1 OOF evidence is **cross-fitted T1 development evidence
  conditional on frozen upstream components** — never unseen generalization,
  external, independent or clinical validation.

## 8. Upstream contracts verified in ECG 8 (reuse, do not re-verify blindly)

All three §2 STOP conditions were checked and **passed**:

1. **U1 per-fold Platt parameters are recoverable without refitting.**
   `cardiosentinel-runs/phase7-u1-development-v1/u1-v1-development/U1_FOLD_MANIFEST.json`
   → `folds[k]` carries `held_out_subject`, `fit_subjects`, and
   `fitted["platt_logistic_on_recovered_logit"]` with `a`, `b`, `clamp_delta`.
   12 folds, one per VALIDATION subject.
2. **M2-G row evidence covers the full replay.**
   `phase6-m2-development-v1/m2-v1-development-two-arm-recovery2__evidence/M2-G/`
   → `row_count: 492904`, columns `stable_id, record_id, channel_index,
   start_sample, available_time, score, scored, update_admitted`.
3. **T2 row evidence covers the full timeline** — 492,904 rows, both arms,
   `score` + `score_present`; identity npz also carries `label`, `target_family`,
   `subject_id`, `primary_mask`, `cold_start_bin` (evaluation only, never
   transition inputs).

**The two sources reconcile exactly**: M2-G 492,898 scored / 6 unscored, T2
492,898 present / 6 absent, and `stable_id` arrays are **identical in order**.
That is what makes label-blind full-timeline calibration possible.

## 9. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed: do
  not delete, reset, rename, re-root or reseed it. **Both T2 attempts now
  exist and are consumed.** `phase8-t2-development-v1/` holds `t2-v1-training`
  and `t2-v1-outer-validation`. Additive `__review` siblings are legitimate
  (they hold failure receipts outside a consumed claim) — the permitted set is
  exactly those two names plus their `__review` forms.
- **No M2 rerun. No U1 rerun. No T2 rerun. No extended T2 training.**
- Keep scratch files OUTSIDE the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace but is NEVER a predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

## 10. Working preferences and hard-won lessons

- Read-only monitoring for long runs; **never** restart/retry a canonical run.
- **Launch canonical runs with Bash `run_in_background: true`.** The foreground
  tool timeout caps at 10 min and a timeout kill would consume the attempt.
- Use `git commit -F <file>` with the message file in the scratchpad.
- **Never run `ruff format` over a whole directory** — format only files you
  changed. CI runs `ruff check .` and `pytest -q`.
- `gh pr edit --body-file` fails on this `gh`; use
  `gh api -X PATCH repos/<owner>/<repo>/pulls/N -F body=@file`.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`.
- **CI monitors must wait for ALL jobs** — exit only when none is
  `IN_PROGRESS`/`QUEUED`/`PENDING`. Two jobs run per PR; they settle in ~7 min.
- **CI has no `cardiosentinel-runs/`** (gitignored). Tests needing real canonical
  artifacts must `pytest.skip("... not on this filesystem")`, matching the
  existing M2/U1/T2 selection convention. Verify by running the suite from a
  directory without the artifacts.
- **Naive source-substring scans produce false positives.** This bit three times
  in ECG 8: `--force` matched a *denylist* and prose; `sigmoid(` matched a
  docstring defining the score; `calibrated_probability` matched a field name.
  Test registered CLI options via `build_parser()._actions`, and test calls via
  AST, not substrings.
- **`validate_t2_protocol_document` / `validate_t2_execution_spec` take `path` as
  a DEFAULT ARGUMENT bound at definition time.** Monkeypatching the module path
  constant never reaches them; patch the digest they compare against instead.
- **Snapshot guards must be content-addressed and recursive.** A depth-1
  filename listing cannot see an in-place rewrite. `attempt_content_snapshot`
  in `tests/neural/test_t2_canonical_training_route.py` digests every file by
  relative path and lists directories separately; reuse it.
- **Do not assert repository state that legitimately changes.** Four assertions
  that "the outer attempt does not exist" went stale the moment the authorized
  run consumed it — they passed in CI (no artifacts) and failed locally. Assert
  that *the test* changed nothing instead.
- **Protocol modules stay standard-library only** and define their own
  `_sha256_file` (see `t2_protocol.py`, `t1_protocol.py`). Persistence modules
  import `sha256_file` from `cardiosentinel.data.provenance`.
- Test-suite counts at end of ECG 8: full **2095 passed, 1 skipped** before the
  T1 PR; T1 protocol adds **68**. T2 suites **412**. Subset
  `-k "m1 or m2 or u1 or t2"` **1353 passed, 1 skipped, 742 deselected**.
- **Aggregate counts are not an identity.** Bind the exact digest and the exact
  stable-id sequence.
- **Put the identity gate in the caller, not the reader.**
- Long reports end with the exact mandated closing block when one is specified.

## 11. Real defects surfaced in ECG 8 (do not re-introduce)

1. **A lock invariant conflated global state with run conduct.**
   `validate_t2_run_lock` required a TRAIN lock to record
   `outer_validation_execution_authorized=false`, but the lock writes a live
   snapshot of the global activation constant. After activation every newly
   written TRAIN lock failed its own validator. The snapshot is now required
   only to be a boolean; the five conduct flags stay strict.
2. **A guard that did not prove what it claimed.** `outer_attempt_unchanged`
   snapshotted immediate child filenames, so a same-name rewrite of STATUS,
   RESULT, the row-evidence manifest or a score array was invisible.
3. **A run-root invariant that contradicted the persistence design.** It forbade
   the `__review` siblings `t2_review_directory` intentionally creates.
4. **Decorative frozen constants.** Both checkpoint-lock *self*-digests and the
   protocol/spec/review document identities were bound but never compared;
   they are now load-bearing.

## 12. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG3
handoff: a concurrent session installed distributions into the then-shared
scientific interpreter while the canonical M1-v2 run was executing. Whether that
process loaded any added distribution **cannot be proven retrospectively**; all
read-only evidence is consistent with no effect. **M1-v2 remains the canonical
frozen M1 development evidence; do not rerun or modify it.**

The ECG3 outer-repo index reconstruction also stands: that index was
**reconstructed, not recovered**, and is still worth a human glance. Outer HEAD
`086ee281370c1e49b2665d33f5a615989c1dc6da` was not changed in ECG 4–8.

M2 recovery2, the U1 canonical run, the T2 canonical TRAIN run and the T2
one-shot outer VALIDATION all ran clean, with all runtime-integrity observations
matching the frozen 335-package digest. **No T1 execution of any kind has been
performed, and no T1 run directory exists.**
