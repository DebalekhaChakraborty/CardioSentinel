# CardioSentinel — handoff to session "ECG 6"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG6.md and continue.
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
Never install, upgrade or downgrade anything in it.

**Note on shell state:** the Bash working directory silently resets to
`/home/AI_POC` (the OUTER repo). **Always `cd` explicitly to the CardioSentinel
repo before any `git`/`gh`/`pytest` command.** Never run `git add -A` anywhere
near `/home/AI_POC`. Outer HEAD is `086ee281370c1e49b2665d33f5a615989c1dc6da`
and must stay that way — it was not changed in ECG 5.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

**Phase 5B (M2) is CLOSED.** M2-G is the retained update policy, immutable.

**Phase 7 (U1) DEVELOPMENT IS EXECUTED AND COMPLETE.**

Master is `233a474aca14dac4bad7d213eae46cd07836928a`. Working tree clean.
No open PR. Nothing is in flight.

### Completed and merged
- B4-A/B4-B/B4-C architecture selection; **B4-B** retained.
- P1 physiology fusion; **P1-B** retained.
- M1 dual-memory canonical run; **M1L_long_memory_v2** retained (frozen).
- M2-v1 protocol frozen; **PR #21–#26** implementation and recovery routes.
- **PR #27** human bounded-Pareto retention of **M2-G** (→ `ba20fc94`).
- **PR #28** U1 calibration / selective-routing protocol, design only (→ `02f1ee41`).
- **PR #29** U1 execution harness + provenance closure (→ `233a474a`).

### Executed
- **U1-v1 canonical DEVELOPMENT run — `COMPLETE`.** See §5.

## 2. What happened in ECG 5

Three authorization boundaries, in order:

1. **U1 CANONICAL DEVELOPMENT EXECUTION HARNESS** — implemented (not executed)
   the one canonical U1 route. Four new modules (`u1_calibration`,
   `u1_evidence_store`, `u1_persistence`, `u1_development_run`) plus one
   hardened helper. Opened PR #29.
2. **U1 EXECUTION HARNESS — FINAL PROVENANCE CLOSURE** — the science was
   ACCEPTED; one hardening pass linked *self-consistency* to *lineage* on both
   the input and output sides. Head `efdb5a2e`. Human merged → `233a474a`.
3. **U1-v1 CANONICAL DEVELOPMENT EXECUTION** — the one-shot run. Exit 0.

The provenance closure is the part worth remembering. Before it, the harness
proved the frozen M2-G arm result was authentic *and* proved the opened
per-window store validated against its own manifest — and never linked the two.
A store that was internally perfect but not the one the frozen arm binds would
have been calibrated. Now refused, and proved refused by an adversarial test
(two synthetic stores differing by one `np.nextafter` on the score bytes; both
validate independently; the run must reject STORE B).

## 3. Frozen digests

| Document | SHA-256 |
|---|---|
| `docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md` | `d6235b477af278fe051822bdcccb54f985e4eceb0c6e92c1424f5e9d7d79b33b` |
| `docs/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | `da4a05b4e2e3dd633493b87a08ed369010fa91c9cac21d906980a658fcf2be47` |
| `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` | `a8ba6fad038ed0ec01156b6959239f489426d55db8ad73a0c704fd527e7db91c` |
| `docs/M2_GATE_DERIVATION_RECEIPT_V1.json` | `5b14c1a72f34945d59d73f152e8fdeaf929a3be56ad47d94a698bc4bfabd3f24` |
| `docs/M2_STRESS_INTERVAL_ELIGIBILITY_DECISION_V1.md` | `078acb3d72a11513010c88a03b0143a2be43da5da807c72d3d7433f98031f8f6` |
| `docs/M2_DEVELOPMENT_ATTEMPT1_FAILURE_AND_RECOVERY_DECISION_V1.md` | `e9d55d7a047e9610c6e156afc9e1a98aafbca86a3131c02a8e56624da7ad57d6` |
| `docs/M2_DEVELOPMENT_RECOVERY1_FAILURE_AND_RECOVERY2_DECISION_V1.md` | `93e53d3c8281d922823d48b73712a2a1ede1c5b0f5bc9f41694af563e1a2fca4` |
| `docs/M1_MEMORY_RETENTION_DECISION_V1.md` | `a3685fc0f8ff1fa0dce2bf9954bb28a925787070c021f3e80ca5716a4fa5f0ed` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |

## 4. Frozen M2 evidence — recovery2 (unchanged, U1's inputs)

| Artifact | SHA-256 |
|---|---|
| M2 suite (`m2_suite_sha256`, self-digest) | `8a6b0a1c64da72fc0f4573c742bef491b01b4eb8179f0759da3c537a01939a02` |
| **M2-G arm result (RETAINED, file digest)** | **`a061d4d8c5211381c18baa228436bb9abc78b2f87f71fe4cab6ca71b2d15cf75`** |
| **M2-G experiment lock (self-digest)** | **`5ac07d9f1ea3859e046c84fb91f22cee1bb20ef4857837b1c82fcd944dbf0fe8`** |
| M2-G evidence-store **content** | `fe721c8b888ee32eae545f5e24a8cffd9b636a93c3fd2698738fd986aa335687` |
| M2-G row evidence npz | `48adbde24eb149be403116e41224c2b22cb73a6e40d68164fea15b2d9e1c994d` |
| Stream cache | `a3e39137a04ebebb3b97ef6c6c614339c990a6041cf649a0ba6e3c2d43baae18` |
| Split (self-digest) | `66e25d77b6aaa25502974b4b60667b4c4b24d649bf9493666827c747a385ced7` |
| M2-0 arm result (control/ablation) | `37a6e9d4c01b823e407addbb897d14f6f54835a347a6557a745890585395644c` |
| Suite result **file** digest | `dfbbbbe8f7a1379a844b894f585fa3c7b1c4098e6ecfc17b438b9297d9f839b6` |

Note: some fields are **file** digests and some are the artifact's own
**canonical payload** self-digest. They differ by design — do not "fix" this.
`arm_result.evidence_store_identity` is byte-equal to the on-disk
`M2_EVIDENCE_STORE.json`, which is why U1 compares whole payloads instead of
inventing a second digest scheme.

**M2 headline (do not re-derive):** PRIMARY = 473,897 rows (21,628 pos /
452,269 neg, 12 subjects) at frozen threshold `0.7554003000259399`. M2-G
sensitivity 0.4683280932, specificity 0.9575120117, AUPRC 0.3845274603.
**M2-G DID NOT improve false-alarm behaviour** — never present the retention as
evidence that it did.

## 5. U1-v1 CANONICAL DEVELOPMENT — the executed run

Run root `cardiosentinel-runs/phase7-u1-development-v1/` (gitignored).
Claim `u1-v1-development`, experiment `U1_selective_v1`.
Started `2026-08-17T18:45:22Z`, completed `18:46:17Z`, exit 0, 62 s wall.
Git SHA `233a474a…`, `git_dirty: false`, 11 runtime enforcement points all
matched at 335 packages. **`validate_canonical_u1_attempt(run_root,
"u1-v1-development")` → PASS.** No `__review` directory: no stop receipt, no
failure receipt.

**THE ATTEMPT IS CONSUMED. There is no second U1 development run, ever.**

### Promoted artifacts

| Artifact | SHA-256 |
|---|---|
| `U1_SATURATION_CENSUS.json` | `0ee3e80dc86d48d89dbb2e3a9f3d1ddb8263670a636335853e36bd91a710e5de` |
| `U1_FOLD_MANIFEST.json` | `6de92e8d86f8fed03357a5daf6a5c33a5c97df06d5cefa846ee2d453e49ed82a` |
| `U1_OOF_CALIBRATION.json` | `c6a48fcd5e14cbe9d543eaa1d81328a8eade41343cc9629c8f3f8b78eee47da2` |
| `U1_FAMILY_SELECTION.json` | `cbf8dec21defa18143050cd74b5c08916a17f07279578541e234fac3cdce70d1` |
| `U1_OOF_RESULT.json` | `dbe546ecb4da1b6a974ace6549803ac9a6894db321707da25cff39d9bca0e7e6` |
| `U1_DEPLOYMENT_CALIBRATOR.json` | `acec97c1ebd3bed459ad2d75204b6c82f274b248edbb1d779b844bd46c62fdc1` |
| `U1_RESULT.json` | `649631cbf5188731d006f533997cfe28df4f5acb79e7693514e86ad0cef0cb12` |
| `U1_EXPERIMENT_LOCK.json` (file) | `eca664ced24cdbc3f28b1ef339c99f0e37ec7185a034a7c7ed28b7f773d1ebfc` |
| `U1_EXPERIMENT_LOCK` (self-digest) | `7f4dd1505919e23a598773736dc57e2d1b4d360f496b45acdf2028ed0574b1b6` |
| OOF evidence-store **content** | `b95f484c9a7b08447f5a5d4330528136e040cf05acb9e2f7e54305e20bdffcba` |
| PRIMARY OOF npz (473,897 rows) | `d30ee58f72e88f09ec940b6a2b284a5c2030f32c2fb8045e1c64b2fb08e60de2` |
| CHALLENGE OOF npz (8,137 rows) | `52fffe2fbef91da55679615d480da2de600ad9acd05b173fe89f0673297e5bec` |
| Fold assignment | `f0f5d8e93a757c0975f3613879d11f53970befa6c6bc57578b1a084c92c85b9a` |

### Scientific results — read these from the artifacts, do not recompute

- **Saturation census: PASS.** 4 / 473,897 rows outside the clamp
  (`8.440652715674503e-06` vs bound 0.01). Zero rows at exactly 0 or 1.
  467,322 distinct persisted scores. Clamp not widened.
- **LOSO K=12: all 24 fits converged** (status 0, `CONVERGENCE: RELATIVE
  REDUCTION OF F <= FACTR*EPSMCH`), `bounds_applied: false`, no retry, no
  fallback. Verified from the per-row store: 473,897 unique stable_ids, exactly
  one OOF prediction per family per row, no held-out subject in its own fit.
- **Family selection: `platt_logistic_on_recovered_logit`.** Pooled OOF NLL
  Platt `0.14370784818131235` vs temperature-only `0.19169200154056643`;
  difference `−0.04798415335925407`; not a tie (tolerance 1e-4).
  Platt Brier `0.040344375976781484`, ECE-EW `0.016990579896181784`,
  ECE-EM `0.018603649015666395`.
  *Temperature-only's two ECEs are identical (`0.07404013328988358`) because it
  over-predicts in every bin of both binnings, so both collapse to the same
  global mean gap. Real, not a defect — expect a reviewer to ask.*
- **Decision equivalence: 0 disagreements** in all 12 folds and in the final
  calibrator (473,897 rows).
- **Retained operating point (`c_star = 0.90`): `u_star_dev =
  0.12763774358328017`**, rank 426,508, achieved coverage 0.9000014771142253,
  accepted 426,508, tie count 1, escalation 0.09999852288577471.
  Accepted risk `0.024770930439757286`, sensitivity `0.0007654038`,
  specificity `0.9997091738`, PPV `0.0620155039`, NPV `0.9755053603`.
- **🚩 ROUTING GUARD RAISED: `asymmetric_abstention`.** Ratio
  `6.453604523726777` against bound 3.0 (positive escalation 0.5167375624 vs
  negative 0.0800696046). The calibration-agreement guard did NOT fire
  (`0.006683691656635168` vs bound 0.02). A raised guard is a **scientific
  outcome**: the complete evidence was persisted, nothing was refit or
  re-selected, `human_review_required: true`, `automatic_retention: false`.
- **Subject-level (n=12):** macro coverage 0.8789353968, macro escalation
  0.1210646032, macro accepted risk 0.0251302289, macro sensitivity
  0.0010357338 (9 of 12 contributing), macro specificity 0.9995026716.
  Bootstrap 1000 replicates / seed 2026, 0 undefined: coverage 95% CI
  [0.8263853591, 0.9524000003], accepted risk [0.0051276110, 0.0490417394],
  sensitivity [0.0, 0.0037951623].
  Claim scope wording: **between-subject variation conditional on fitted OOF
  calibration.**
- **Cold start** (counts bound to frozen M2-G *and* to the stream-cache
  identity): 0–5 min N=1,798 (1 positive — discrimination undefined),
  5–60 min N=19,637, >60 min N=452,462. The 0–5 min zero sensitivity is
  **inherited from M2**; U1 defines no cold-start threshold and performs no
  repair.
- **Challenge at `u_star_dev`:** RATE N=4,973 → accepted 2,254, escalation
  0.5467524633, accepted FP 1 (FPR 0.0004436557), all-window FP 2,029.
  AXIS N=3,000 → accepted 2,428, escalation 0.1906666667, accepted FP 0,
  all-window FP 236. CONDUCTION N=164 → descriptive only, 157 accepted,
  0 accepted FP, 5 all-window FP.
- **Final deployment calibrator:** Platt `a = 0.3715906808641229`,
  `b = −1.7662772879067046`, 12 subjects / 473,897 rows, status 0, calibrated
  boundary `0.20631829355583678`, 0 disagreements.
  **`u_star_deploy = 0.12914217081334087` is CONFIGURATION PROVENANCE ONLY.**
  In-sample performance was not computed and must never be reported as
  DEVELOPMENT evidence.
- **TEST: untouched.** `test_accessed: false`, `sealed_test_state: unopened`,
  all 12 TEST subjects refused **by name** (not filtered). Independently
  confirmed: no TEST subject appears in the promoted per-row evidence.

## 6. THE OPEN GATE — start here

**Nothing is authorized right now beyond the human U1 retention review.**

The next human decision is: **retain U1 selective routing, or not** — given
that the asymmetric-abstention guard fired at the retained operating point.
Do not make that decision. Do not soften it. Do not propose a different
`c_star`, a different `u_star`, a cold-start-specific threshold, or a refit.

Likely next authorizations, in order:
1. Human U1 calibration / selective-routing **retention decision** (a frozen
   `docs/U1_..._RETENTION_DECISION_V1.md` + PR, same shape as M2's).
2. Only then a human decision on whether **U2 conformal** is worth the
   schedule. **Do NOT begin U2/T1/T2/E1 automatically.**
3. TEST (T1/T2) requires its own separate authorization. Completion of U1
   DEVELOPMENT does **not** authorize TEST.

## 7. U1 — what is frozen (do not redesign, do not re-litigate)

Accepted through three human review rounds: LOSO K=12 · OOF-only family
selection · Platt-on-recovered-logit primary · approximate temperature-only
comparator · recovered-logit policy · saturation census and its 0.01 bound ·
frozen classifier threshold `0.7554003000259399` · uncertainty definition ·
risk definition · coverage grid · `c_star = 0.90` · empirical `ceil` order
statistic · `u_star_dev`/`u_star_deploy` distinction · final all-validation
calibrator semantics · both ECE definitions · bootstrap semantics (1000, seed
2026, subject unit) · TEST firewall · M2 immutability.

Key facts a future session will need:

- **True logits are NOT persisted.** Only `sigmoid(logit)` is stored, in
  float32-then-widened. Recovered logits are quantized (~5.96e-8 spacing below
  1.0, saturating above z≈16.6). Proper temperature scaling is unavailable.
  **Do not rerun M2 to persist logits.** Never call recovered logits true
  logits.
- **G4 normal-evidence (`0.0002997174742631614`) is NOT classifier confidence**
  and is never calibrated. The only calibration input is the persisted `score`
  column.
- Uncertainty `u` = calibrated probability the frozen decision is wrong
  (`1−p` if predicted positive, else `p`).
- Routing threshold: `k = ceil(c_star * N)` over a stable `(u, stable_id)`
  sort, accept `u <= u_star`. **Never a library quantile** — numpy `'lower'`
  gives 426,507 and lands below target. This was a real defect caught in
  review.
- All U1 DEVELOPMENT evidence is **OOF only**. The final all-validation
  calibrator is deployable configuration, **parameterisation not evaluation**.
- U1 development evidence is **development-optimistic** — VALIDATION already
  selected `tau`. Cross-fitting fixes subject self-calibration only.
- The inferential unit is the **subject (12)**. Windows overlap; never claim
  hundreds of thousands of independent windows.
- `u1_protocol.py` imports **only the standard library** — a test enforces
  this so protocol validation cannot reach real data. Keep it that way.
- The harness's two non-M2-G inputs are deliberate and disclosed, not hidden:
  the M2-G store is `labels_present: false`, so PRIMARY labels/subjects come
  from the frozen P1 authority and cold-start strata from the persisted M1
  stream-cache array — the same authorities M2 itself used. Neither is a
  replay.

## 8. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed: do
  not delete, reset, rename, re-root or reseed it. Stop and report.
  **This now applies to `phase7-u1-development-v1/` as well.**
- **No M2 rerun is permitted, ever.** M2-0 and M2-G are both immutable.
- **No U1 rerun.** No `recovery1`, no alternate root, no timestamp/uuid/random
  suffix, no repair of the promoted artifacts.
- Keep scratch files OUTSIDE the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace but is NEVER a predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

## 9. Working preferences and hard-won lessons

- Read-only monitoring for long runs; **never** restart/retry, never relaunch a
  canonical run, never kill for slowness or high RSS.
- **Launch canonical runs with Bash `run_in_background: true`, never in the
  foreground.** The foreground tool timeout caps at 10 min; a timeout kill on a
  one-shot canonical run would consume the attempt irrecoverably.
- Report failures with exact exit codes and stage; describe OOM-like kills as
  "strongly consistent with process termination under host memory exhaustion",
  not "kernel OOM killer confirmed".
- Use `git commit -F <file>` with the message file in the scratchpad.
- **Never run `ruff format` over a whole directory** — format only the files you
  changed. `m1_selection.py` is itself not `ruff format`-clean; CI only runs
  `ruff check .` and `pytest -q`.
- `gh pr edit --body-file` fails on this `gh` version (projectCards GraphQL);
  use `gh api -X PATCH repos/<owner>/<repo>/pulls/N -F body=@file`.
- **`gh pr checks` has no `--json` on this version.** Use
  `gh pr view N --json statusCheckRollup`.
- **CI monitors must wait for ALL jobs.** Exit only when no job is
  `IN_PROGRESS`/`QUEUED`/`PENDING`.
- Full `pytest -q` takes ~10½ min; the M2/U1 `-k` subset ~8¼ min. `-q` buffers,
  so silence is not a stall.
- Test-suite counts at end of ECG 5: full **1643 passed, 1 skipped**;
  M2/U1 subset **714 passed**; targeted U1 **176 passed** (106 harness +
  70 protocol).
- `validate_canonical_u1_attempt(run_root, experiment_id)` takes the **claim
  id** (`u1-v1-development`), not the scientific identity (`U1_selective_v1`).
- Substring assertions on protocol prose produce false positives when the
  document legitimately *forbids* a phrase. Prefer AST/identifier checks.
- Test seams that inject past a component hide defects **in that component**.
  Drive the real component against synthetic on-disk fixtures. Two real defects
  surfaced this way in ECG 5: the challenge calibration loop called the fold
  calibrator on an empty array for the 8 of 12 folds whose held-out subject
  contributes no challenge windows, and monkeypatching a module constant did
  nothing because `routing_guards` binds its bounds as default arguments.
- Put the identity gate in the **caller**, not the reader — otherwise an
  injected loader bypasses it.
- **Aggregate counts are not an identity.** Matching stratum totals do not make
  it the same artifact; bind the exact digest.
- Never weaken an integrity check for performance. The `O(N²)` duplicate-id
  scan became a single hashed pass with **identical** refusal semantics, proved
  by a parity test.
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
`086ee281370c1e49b2665d33f5a615989c1dc6da` was not changed in ECG 4 or ECG 5.

M2 recovery2 and the U1 canonical run both ran clean: runtime-integrity sentinel
matched at every enforcement point, 335 packages, digest `b0fd6eaa…`, no
automatic retry, no environment repair.
