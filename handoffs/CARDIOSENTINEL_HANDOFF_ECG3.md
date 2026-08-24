# CardioSentinel — handoff to session "ECG 3"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG3.md and continue."

---

## 0. READ FIRST — environment changed on 2026-08-12

**The scientific interpreter is no longer `debalekha`.**

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (ServiceDesk etc., do NOT use for CardioSentinel) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub | `DebalekhaChakraborty/CardioSentinel-AI` |

`tactics` holds exactly the frozen 335-package set,
`installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`,
and `require_p1_runtime()` returns **GREEN**. Never install, upgrade or downgrade
anything in it. Historical run artifacts and frozen documents record the old
`debalekha` path because that is what actually executed; that history is not
rewritten.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

**Current position: PR #21 is open and unmerged, awaiting human review.**
Branch `research/m1-retention-m2-protocol-v1`, head
`27c246247f91fdf2ee47fb53a612fbe5b0298596`, CI green, base scientific tree
`8260b718ab235873bd8067ca3fbf14f158c71dcd`.

### Completed
- B4-A/B4-B/B4-C architecture selection; B4-B retained.
- P1 physiology fusion; **P1-B** retained.
- M1 dual-memory: two documented pre-claim failures (Authorization 1 exit 137
  under memory exhaustion; Authorization 2 exit 1 on waveform admissibility),
  then **Authorization 3 succeeded, exit 0** — the canonical M1-v2 Stage-1 run.
- **M1L_long_memory_v2 retained** (frozen).
- M2-v1 contamination-safe protocol frozen, with all TRAIN-only gate constants
  derived.
- Environment forensics + isolation + runtime restoration (this session).

### Frozen digests (current)
| Document | SHA-256 |
|---|---|
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` (ACTIVE) | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| `docs/M1_MEMORY_RETENTION_DECISION_V1.md` | `a3685fc0f8ff1fa0dce2bf9954bb28a925787070c021f3e80ca5716a4fa5f0ed` |
| `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` | `9d0a635e5b954d1334a78ac327d0190e41a62de7abf570b79446a5110ff53436` |
| `docs/M2_GATE_DERIVATION_RECEIPT_V1.json` | `3befd05dc7e9c51ddfed99078d3020375fd610b328d19e64fc7ee3cc745f398e` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` (design only) | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |
| `docs/P1_PHYSIOLOGY_RETENTION_DECISION_V1.md` | `7b403709fa0fb12eef65423d830c121fc3ada904266a1b47931d438f5e797d68` |

### Canonical M1-v2 artifacts
Run root `cardiosentinel-runs/phase5-m1-dual-memory-v2`, suite
`be36f0743dad649756626a981c3dd05ec6f54dc9c01150e70bb3caeb407bac0e`.
Arm locks: M1S `e9fd43f7…4e593a65`, **M1L `a2636855e14bdd54bd54…6d013c75a5` (retained)**,
M1D `2d08ffbb…5363af1a3c1`. P1-B control lock `796f00e3…0676d0`.
`memory_selection_performed: false`, `memory_selected: null`, `test_accessed: false`.

## 2. Key technical facts

- M1 stream key `(record_id, channel_index)`; causal order `window_start_samples`;
  corpus has **2 OR 3 channels**, indices `{0,1,2}`.
- TRAIN 2,208,431 rows / 60 records / 132 streams; VALIDATION 492,904 / 13 / 30.
- `z_t` = [frozen B4-B 128 ; transformed morphology_v1 18] = **146**.
- `alpha_short = 0.01148597964710385`, `alpha_long = 0.0009622411662165709`,
  per AVAILABLE update, never time-rescaled. Score-before-update.
- Distance standardizer TRAIN-only 374,452×146, `ddof=0`.
- Physical availability: `np.ptp(values) <= eps` → `UNAVAILABLE_EXACT_FLAT`
  (no B4-B call, all-NaN 146-d row, no score, no update, no counter increment).
  TRAIN unavailable 0; VALIDATION unavailable 6.
- `canonical_sha256` = `json.dumps(payload, sort_keys=True, separators=(",",":"))`
  hashed UTF-8.
- Frozen runtime: Python 3.12.6, torch 2.13.0+cpu, numpy 2.3.2, sklearn 1.9.0,
  scipy 1.18.0, wfdb 4.3.1, CPU, AMP off.

## 3. Frozen M2-v1 constants (do not reopen)

- Core arms **M2-0 (naive always-update) vs M2-G (gated)**; rollback excluded.
- Gate order G1 available → G2 finite `z_t` → G3 SQI → G4 normal evidence →
  G5 refractory → G6 `morphology_valid == 1`.
- G3: six declared SQI columns (**five independent** — `flatline_fraction` and
  `repeated_value_fraction` are bitwise identical), Q99 linear on the full TRAIN
  AVAILABLE population, `finite_sample_fraction == 1.0` precondition.
  Bounds: flatline/repeated `0.4853938160326376`, derivative_outlier
  `0.12404953560371516`, high_frequency_power `0.026921875216808343`,
  powerline_50hz `0.0017277915136508007`, powerline_60hz `0.0012836341894374625`.
  Combined TRAIN rejection 0.038969.
- `NORMAL_EVIDENCE_THRESHOLD = 0.0002997174742631614` (median M1L score over
  280,839 PRIMARY TRAIN background-negative rows).
- `M2_CLASSIFICATION_EVALUATION_THRESHOLD = 0.7554003000259399` (the retained
  M1L threshold; both arms use it; **no threshold search of any kind**).
- Refractory 60.0 s real elapsed time, re-armable, keyed on
  `(start_sample + 2500)/250.0`, not an update count.
- TRAIN-only sanity: final M2-G update fraction 0.201222; per-stream median
  0.126352 with one stream at 0.000000 (must be reported, not smoothed).

## 4. THE OPEN BLOCKER — start here

The last authorization ("FINAL M2-v1 PROTOCOL INTEGRITY REVIEW", §1–§15) was
**halted at §1** because the official runtime gate was RED. That cause is now
fixed, but **§2–§13 were never resumed and still need explicit authorization.**

Outstanding from that authorization:
- §2 commit a read-only TRAIN-only derivation verifier
  (`src/cardiosentinel/neural/m2_gate_derivation.py`).
- §3 run it once to reproduce the frozen G3/G4 constants and TRAIN sanity.
- §4 freeze `M2_CLASSIFICATION_EVALUATION_THRESHOLD` in `m2_gate.py` + tests.
- §5 freeze M2-0 control-equivalence requirement.
- §6–§8 build `docs/M2_DEVELOPMENT_STRESS_INDEX_V1.json` (ischemic ST, rate,
  axis, quality/noise, conduction) with the frozen interval-grouping rule.
- §9 per-family drift reporting boundary.
- §10 quality/noise stratum must NOT be defined by the G3 SQI gate.
- §11 revise the gate receipt (record `3befd05d…` as SUPERSEDED BEFORE M2
  IMPLEMENTATION — dependency-provenance semantic correction).
- §12 rebind the protocol + `m2_gate.py`; recompute SHAs.
- §13 sixteen required tests.

**Important:** the committed receipt still records
`environment.dependency_digest = 78e838d2…`, which is the *mutated* environment.
It must be corrected under §11 by re-deriving under the now-green `tactics`
runtime — **never by hand-editing the digest**.

## 5. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/hash
  a B4 test cache or test waveform; inspect B4 test labels; calculate B4 test
  metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed: do
  not delete, reset, rename, re-root or reseed it. Stop and report.
- Keep scratch files OUTSIDE the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace but is NEVER a predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- **There is NO Authorization 4** for M1.
- Do not access VALIDATION for threshold derivation. Do not access sealed TEST.
- Do not merge PR #21. Do not run M2. Do not rerun M1.

## 6. Execution-integrity record (do not soften)

The 2026-08-12 event: a concurrent Codex session working on
`/home/AI_POC/servicedesk-ai` ran two escalated `pip install` commands into the
then-shared scientific interpreter — `pip install -r requirements-aws-workspaces.txt`
at 18:08:2x and `pip install 'botocore[crt]'` at 19:10:0x — while the canonical
M1-v2 run (18:01:39 → 19:49:15) was executing. The run's gate passed at startup,
seven minutes before the first install.

Permanent limitation: **whether the terminated M1-v2 process loaded any of the
five added distributions cannot be proven retrospectively.** All read-only
evidence is consistent with no effect. Human interpretation recorded: **M1-v2
remains the canonical frozen M1 development evidence; do not rerun or modify it.**

Also note: concurrent agents actively create and populate venvs under
`/home/AI_POC/venvs/`. Protection of `tactics` currently rests on convention (no
standing approval rule points at it), not enforcement. Filesystem-level
protection is proposed in `RUNTIME_INTEGRITY_SENTINEL_V1.md` §4 and awaits a
human decision.

## 7. Working preferences

- Read-only monitoring crons for long runs; **never** restart/retry logic, never
  relaunch a canonical run, never kill for slowness or high RSS.
- Report failures with exact exit codes and stage; describe OOM-like kills as
  "strongly consistent with process termination under host memory exhaustion",
  not "kernel OOM killer confirmed", unless the kernel record was observed.
- Use `git commit -F <file>` (commit messages have broken shell quoting before).
- Long reports end with an explicit mandated closing block when the user
  specifies one.
