# CardioSentinel — handoff to session "ECG 5"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG5.md and continue."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (ServiceDesk etc., do NOT use for CardioSentinel) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub | `DebalekhaChakraborty/CardioSentinel-AI` |

`tactics` holds exactly the frozen 335-package set,
`installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`,
and `require_p1_runtime()` returns **GREEN**. Never install, upgrade or
downgrade anything in it.

**Note on shell state:** the Bash working directory silently resets to
`/home/AI_POC` (the OUTER repo) repeatedly — it happened several times again
this session, and it is why one `gh` call failed with "none of the git remotes
... point to a known GitHub host". **Always `cd` explicitly to the CardioSentinel
repo before any `git`/`gh`/`pytest` command.** Never run `git add -A` anywhere
near `/home/AI_POC`. Outer HEAD is `086ee281370c1e49b2665d33f5a615989c1dc6da`
and must stay that way.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

**Phase 5B is CLOSED.** M2-G is the retained update policy, merged and immutable.

**Current position: PR #28 is open and unmerged, CI green, awaiting human merge.**
Branch `research/u1-calibration-protocol-v1`, head
`32aae59a56ec99d37c83304acdda4fbdfb032bd3`, base master
`ba20fc94465ac5c3080b998096797cc6d965ec1f`, `mergeable_state: clean`,
both `test` jobs SUCCESS.

### Completed and merged
- B4-A/B4-B/B4-C architecture selection; **B4-B** retained.
- P1 physiology fusion; **P1-B** retained.
- M1 dual-memory canonical run; **M1L_long_memory_v2** retained (frozen).
- M2-v1 protocol frozen with all TRAIN-only gate constants derived.
- **PR #21–#25** M2 implementation, canonical route, and two recovery routes.
- **PR #26** source-null SQI semantics + recovery2 preparation.
- **PR #27** human bounded-Pareto retention of **M2-G** (merged → `ba20fc94`).

### Open
- **PR #28** U1 calibration / selective-routing protocol — **design only**,
  hardened through two human review rounds. Do not merge without review.

## 2. What happened in ECG 4 — the big one

**Recovery2 executed and SUCCEEDED.** Two prior canonical attempts had been
consumed by pre-scoring failures with zero scientific evidence. Recovery2 was
the last authorized attempt; there was no recovery3.

- Started `2026-08-14T17:38:32Z`, exited `17:51:18Z`, **exit code 0**, 12m46s.
- Both arms `COMPLETE`, results + locks + suite promoted, no failure receipt.
- Suite `m2-v1-development-two-arm-recovery2`, execution SHA
  `cdc33797c3b7eb8a2c337c64a7f22a92f05d83a5`.

Then the human made the retention decision (**RETAIN M2-G**), which was frozen,
tested, merged as PR #27. Then U1 was designed and hardened (PR #28).

## 3. Frozen digests — verified at end of ECG 4

| Document | SHA-256 |
|---|---|
| `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` | `a8ba6fad038ed0ec01156b6959239f489426d55db8ad73a0c704fd527e7db91c` |
| `docs/M2_GATE_DERIVATION_RECEIPT_V1.json` | `5b14c1a72f34945d59d73f152e8fdeaf929a3be56ad47d94a698bc4bfabd3f24` |
| `docs/M2_STRESS_INTERVAL_ELIGIBILITY_DECISION_V1.md` | `078acb3d72a11513010c88a03b0143a2be43da5da807c72d3d7433f98031f8f6` |
| `docs/M2_DEVELOPMENT_ATTEMPT1_FAILURE_AND_RECOVERY_DECISION_V1.md` | `e9d55d7a047e9610c6e156afc9e1a98aafbca86a3131c02a8e56624da7ad57d6` |
| `docs/M2_DEVELOPMENT_RECOVERY1_FAILURE_AND_RECOVERY2_DECISION_V1.md` | `93e53d3c8281d922823d48b73712a2a1ede1c5b0f5bc9f41694af563e1a2fca4` |
| **`docs/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md`** (new) | **`da4a05b4e2e3dd633493b87a08ed369010fa91c9cac21d906980a658fcf2be47`** |
| **`docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md`** (new, PR #28) | **`d6235b477af278fe051822bdcccb54f985e4eceb0c6e92c1424f5e9d7d79b33b`** |
| `docs/M1_MEMORY_RETENTION_DECISION_V1.md` | `a3685fc0f8ff1fa0dce2bf9954bb28a925787070c021f3e80ca5716a4fa5f0ed` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |

## 4. The frozen M2 evidence — recovery2

| Artifact | SHA-256 |
|---|---|
| M2 suite (`m2_suite_sha256`) | `8a6b0a1c64da72fc0f4573c742bef491b01b4eb8179f0759da3c537a01939a02` |
| **M2-G arm result (RETAINED)** | **`a061d4d8c5211381c18baa228436bb9abc78b2f87f71fe4cab6ca71b2d15cf75`** |
| **M2-G experiment lock (RETAINED)** | **`5ac07d9f1ea3859e046c84fb91f22cee1bb20ef4857837b1c82fcd944dbf0fe8`** |
| M2-0 arm result (control/ablation) | `37a6e9d4c01b823e407addbb897d14f6f54835a347a6557a745890585395644c` |
| M2-0 experiment lock (control/ablation) | `8f7109494efc243613046dd57bcdece80491cf6897c867e224235eb8480c1461` |
| Suite result **file** digest | `dfbbbbe8f7a1379a844b894f585fa3c7b1c4098e6ecfc17b438b9297d9f839b6` |

Note: `arm_result_sha256` is the **file** digest; `arm_experiment_lock_sha256`
is the lock's internal **canonical payload** digest. They differ by design —
do not "fix" this.

Preserved on disk (gitignored) under
`cardiosentinel-runs/phase6-m2-development-v1/`: all three attempts
(`...two-arm`, `...-recovery1`, `...-recovery2`), plus 62 recovery2 prototype
trajectory `.npz` files. **Do not delete, move, rename or regenerate any of it.**

`validate_original_attempt1_failure_lineage()` and
`validate_recovery1_failure_lineage()` still verify. Recovery1's two scoring
facts remain preserved and neither replaces the other:
`receipt_scoring_started = "indeterminate"` and
`human_forensic_scorer_invocation_observed = false`.

## 5. The headline M2 result — both arms, no re-derivation needed

PRIMARY = 473,897 rows (21,628 pos / 452,269 neg, 12 subjects) at the frozen
threshold `0.7554003000259399`.

| Metric | M2-0 | M2-G | Δ (G−0) |
|---|---|---|---|
| AUPRC | 0.3847955698 | 0.3845274603 | −0.0002681095 |
| AUROC | 0.9075699068 | 0.9084480510 | +0.0008781442 |
| Sensitivity | 0.4535324579 | 0.4683280932 | +0.0147956353 |
| Specificity | 0.9606053035 | 0.9575120117 | −0.0030932918 |
| PPV | 0.3550640701 | 0.3451695348 | −0.0098945353 |
| MCC | 0.3688867751 | 0.3687438704 | −0.0001429047 |
| Background FPR | 0.0393946965 | 0.0424879883 | **+0.0030932918** |
| Rate-related FPR | 0.3939272069 | 0.4080032174 | **+0.0140760105** |
| Axis FPR | 0.0713333333 | 0.0786666667 | **+0.0073333334** |

Max peak prototype drift (`sqrt(mean((mu_long(t) − mu_ref)**2))`):
ischemic 1.3088318203 → 0.0023193737 (~99.82%), HR-related 1.0076068363 →
0.0398963001 (~96.04%), unreadable 1.1560887735 → 0.4041660010 (~65.0%).

M2-G admitted **107,671** updates (0.2184421307) — **not** a trivial
never-update gate. Cold start: 0–5 min sensitivity **0.000000 in both arms**.

**M2-G DID NOT improve false-alarm behaviour.** Never present the retention as
evidence that it did. No Pareto dominance, no statistical significance, no
clinical claim, no generalisation claim.

## 6. THE OPEN GATE — start here

**Nothing is authorized right now beyond human merge review of PR #28.**

Likely next authorizations, in order:
1. Human merge review of PR #28 (U1 protocol, design only).
2. After merge: **U1 PR B** — the reviewed execution implementation. This is a
   separate change set by explicit design, because calibration methodology is a
   new scientific decision.
3. Only then a U1 execution authorization naming the new master SHA.
4. After U1 closes: a human decision on whether U2 conformal is worth the
   schedule. **Do NOT begin U2/T1/T2/E1 automatically.**

## 7. U1 protocol — what is already frozen (do not redesign)

Accepted by human review; do not reopen: LOSO K=12 · OOF-only family selection ·
Platt-on-recovered-logit primary · approximate temperature-only comparator ·
recovered-logit policy · saturation census · frozen classifier threshold ·
uncertainty definition · risk definition · coverage grid · `c_star = 0.90` ·
empirical `ceil` order statistic · `u_star_dev`/`u_star_deploy` distinction ·
final all-validation calibrator semantics · ECE definitions · bootstrap
semantics · TEST firewall · M2 immutability.

Key facts a future session will need:

- **True logits are NOT persisted.** The head emits `single_raw_logit`, but only
  `sigmoid(logit)` is stored, and the head + features are **float32**, so the
  sigmoid is evaluated in float32 then widened. Proper temperature scaling is
  therefore unavailable; recovered logits are quantized (~5.96e-8 spacing below
  1.0, saturating above z≈16.6). **Do not rerun M2 to persist logits.**
- **G4 normal-evidence (`0.0002997174742631614`) is NOT classifier confidence**
  and is never calibrated. The only calibration input is the persisted `score`
  column (`float64`, schema `m2_v1_evidence_store/1`).
- Uncertainty `u` = calibrated probability the frozen decision is wrong
  (`1−p` if predicted positive, else `p`).
- Routing threshold: `k = ceil(c_star * N)` over a stable `(u, stable_id)` sort,
  accept `u <= u_star`. At `N=473,897`, `c*=0.90` → `k=426,508`. A numpy
  `'lower'` quantile gives 426,507 → 0.8999993669…, **below target** — this was
  a real defect found in review; do not reintroduce a library quantile.
- All U1 DEVELOPMENT evidence is **OOF only**. The final all-validation
  calibrator is deployable configuration, **parameterisation not evaluation**,
  and its in-sample numbers are never a U1 result.
- U1 development evidence is **development-optimistic** — VALIDATION already
  selected `tau`. Cross-fitting fixes subject self-calibration only.
- The inferential unit is the **subject (12)**. Windows overlap and are
  correlated; never claim hundreds of thousands of independent windows.

`src/cardiosentinel/neural/u1_protocol.py` imports **only the standard library**
(hashlib, json, math, pathlib, typing) — a test enforces this so protocol
validation cannot reach real data. Keep it that way.

## 8. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/hash
  a B4 test cache or test waveform; inspect B4 test labels; calculate B4 test
  metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed: do
  not delete, reset, rename, re-root or reseed it. Stop and report.
- **No M2 rerun is permitted, ever.** M2-0 and M2-G are both immutable.
- Keep scratch files OUTSIDE the repo. Do not add the Research Execution
  Handbook to the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace but is NEVER a predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access VALIDATION for threshold derivation. Do not access sealed TEST.
- Do not modify the frozen M2 protocol or regenerate the TRAIN gate receipt.
- Do not merge PR #28. Do not implement the U1 execution runner yet.

## 9. Working preferences and hard-won lessons

- Read-only monitoring for long runs; **never** restart/retry, never relaunch a
  canonical run, never kill for slowness or high RSS. (Recovery2 grew 301 MB →
  1.14 GB and was fine.)
- Report failures with exact exit codes and stage; describe OOM-like kills as
  "strongly consistent with process termination under host memory exhaustion",
  not "kernel OOM killer confirmed".
- Use `git commit -F <file>` with the message file in the scratchpad.
- **Never run `ruff format` over a whole directory** — format only the files you
  changed. Note `m1_selection.py` is itself not `ruff format`-clean; CI only runs
  `ruff check .` and `pytest -q`, so do not "fix" unrelated files.
- `gh pr edit --body-file` fails on this `gh` version (projectCards GraphQL);
  use `gh api -X PATCH repos/<owner>/<repo>/pulls/N -F body=@file`.
- **`gh pr checks` has no `--json` on this version.** For CI waiting use
  `gh pr view N --json statusCheckRollup`.
- **CI monitors must wait for ALL jobs.** A break condition matching
  `*COMPLETED*` against the combined status string fires when only one of two
  jobs finishes. Exit only when no job is `IN_PROGRESS`/`QUEUED`/`PENDING`.
- Full `pytest -q` takes ~10–10½ min; the M2/U1 `-k` subset ~8½ min. `-q`
  buffers, so silence is not a stall.
- Test-suite counts at end of ECG 4: full **1537 passed, 1 skipped**;
  M2/U1 subset **608 passed**; targeted U1 **70 passed**.
- Substring assertions on protocol prose produce false positives when the
  document legitimately *forbids* a phrase. Prefer AST/identifier checks, or
  reword the prohibition — twice this session a test failed on its own doc text.
- Test seams that inject past a component hide defects **in that component**.
  Prefer driving the real component against synthetic on-disk fixtures.
- A helper that "documents" a rule but doesn't execute it is a real gap: U1's
  equal-mass ECE helper originally consumed only the row count and never sorted.
  Human review caught it. Make executable specs actually executable.
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
`086ee281370c1e49b2665d33f5a615989c1dc6da` was not changed in ECG 4 and nothing
was committed there.

Recovery2 itself ran clean: runtime-integrity sentinel matched at START and
PRE_PROMOTION, 335 packages, digest `b0fd6eaa…`, no automatic retry, no
environment repair.
