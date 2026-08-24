# CardioSentinel — handoff to session "ECG 4"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG4.md and continue."

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

**Note on shell state:** the Bash working directory has silently reset to
`/home/AI_POC` (the OUTER repo) more than once mid-session. Always `cd` to the
CardioSentinel repo explicitly before any `git` command. A `git add -A` in the
outer repo once required reconstructing that repo's index — see §7.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

**Phase 5B — M2-v1 contamination-safe continual adaptation.**

**Current position: PR #26 is open and unmerged, awaiting human review.**
Branch `research/m2-development-recovery2-v1`, head
`eb025dc24820aadb714342108505a33dda666988`, CI green (`test` pass),
`mergeable_state: clean`, base master
`d77fbdc37415c43728dbe3173ce58a85cfe2e71d`.

### Completed and merged
- B4-A/B4-B/B4-C architecture selection; **B4-B** retained.
- P1 physiology fusion; **P1-B** retained.
- M1 dual-memory canonical run; **M1L_long_memory_v2** retained (frozen).
- M2-v1 protocol frozen with all TRAIN-only gate constants derived.
- **PR #21** provenance-only canonicalization of the M2 TRAIN-only derivation.
- **PR #22/#23** M2 implementation + canonical execution harness.
- **PR #24** canonical development execution route (four populations, suite
  contract, filesystem-authoritative failure state).
- **PR #25** recovery route after the attempt-#1 partition-join failure.

### Frozen digests (current, verified this session)
| Document | SHA-256 |
|---|---|
| `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` | `a8ba6fad038ed0ec01156b6959239f489426d55db8ad73a0c704fd527e7db91c` |
| `docs/M2_GATE_DERIVATION_RECEIPT_V1.json` | `5b14c1a72f34945d59d73f152e8fdeaf929a3be56ad47d94a698bc4bfabd3f24` |
| `docs/M2_STRESS_INTERVAL_ELIGIBILITY_DECISION_V1.md` | `078acb3d72a11513010c88a03b0143a2be43da5da807c72d3d7433f98031f8f6` |
| `docs/M2_DEVELOPMENT_ATTEMPT1_FAILURE_AND_RECOVERY_DECISION_V1.md` | `e9d55d7a047e9610c6e156afc9e1a98aafbca86a3131c02a8e56624da7ad57d6` |
| `docs/M2_DEVELOPMENT_RECOVERY1_FAILURE_AND_RECOVERY2_DECISION_V1.md` | `93e53d3c8281d922823d48b73712a2a1ede1c5b0f5bc9f41694af563e1a2fca4` |
| `docs/M1_MEMORY_RETENTION_DECISION_V1.md` | `a3685fc0f8ff1fa0dce2bf9954bb28a925787070c021f3e80ca5716a4fa5f0ed` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |

`docs/M2_DEVELOPMENT_EXECUTION_PROTOCOL_V1.md` is implementation/execution
semantics only and is **not** pinned by a code constant; it changes as the route
changes.

## 2. THE CENTRAL FACT — two canonical attempts are consumed and failed

**No M2 development scientific evidence exists.** Neither attempt scored a
single row.

| | Attempt #1 | Recovery1 |
|---|---|---|
| Suite id | `m2-v1-development-two-arm` | `m2-v1-development-two-arm-recovery1` |
| Execution master | `3c1ba4ce87ade6a2d17386b3a9d2b579ded442e7` | `d77fbdc37415c43728dbe3173ce58a85cfe2e71d` |
| Started / exited | `2026-08-13T21:58:44Z` → `22:00:09Z` | `2026-08-14T12:52:11Z` → `12:53:32Z` |
| Failure stage | full label-blind replay | full label-blind replay, inside stream assembly |
| Reason class | `pre_scoring_partition_alignment_execution_defect` | `pre_scoring_source_null_join_sentinel_defect` |
| Exception | `M2GateDerivationError`: TRAIN record set ≠ M1 stream cache list | `M2FeatureJoinError`: join left unmatched rows for `high_frequency_power_ratio` |

Both claimed **both** arms first, so both are consumed. Preserved under
`cardiosentinel-runs/phase6-m2-development-v1/` (gitignored, on disk only).

### Frozen forensic digests — do not alter these files
```
attempt #1  M2-0 status   3699e656ee5ab6c6d3fba90dd7dd726cbb06233d478e53b81327f394e9f6365d
attempt #1  M2-G status   7908130758cfffa171fe47f3958ee4ef7961bfe3d352486e1f2558862251a751
attempt #1  receipt file  8c3a0734dcd2b3dd695e7ad3ff88933a48e80ec48adc3a42b759932cc07cb278
attempt #1  receipt_sha   31345512e42578c1bac8ad611689501a49c40e5d7ab2d70f6c41508d9c4492eb

recovery1   M2-0 status   642cc8376c87826a5d7fdbd5d0730ca44b20f3429c26ea44c58974b45244d054
recovery1   M2-G status   8ba15ca25b70c7686b2e39fe3e073607511835ff42fa19b5ee4d9138f4a0170d
recovery1   receipt file  7773c6135a22e7ba64699511e1db1e92c8aac1ec9b90727d7805f540d5156446
recovery1   receipt_sha   5b05873d48f1355292113a07d6025258e071cb9b13a35caaff1a10132cbb0408
```

`validate_original_attempt1_failure_lineage()` and
`validate_recovery1_failure_lineage()` prove both from these artifacts. Recovery2
**cannot be claimed** unless both verify. If any is absent or mutated: STOP.

### Recovery1's two scoring facts — both preserved, neither replaces the other
- `receipt_scoring_started = "indeterminate"` (the immutable runtime value —
  never rewrite it)
- `human_forensic_scorer_invocation_observed = false` (control-flow
  determination: the traceback ended inside `iter_timeline_streams` before the
  first stream reached replay, and no trajectory file was written)

## 3. What PR #26 contains (open, unmerged)

11 files. Root cause: the partition-aware join used `isnan(output)` as proof a
row was never assigned — but NaN is also the legitimate representation of an
upstream source null, so a valid corpus raised a structural error.

- **The join now tracks structural assignment separately from values**: a
  `written` mask per assigned block + `require_all_rows_written()`. A source null
  survives **unchanged**; no zero/median/bound/infinity substitution, no dropped
  row, no availability re-marking, no new threshold, no corpus regeneration.
- **The value semantics were already frozen** and are proved against the real
  `evaluate_gate`: `UNAVAILABLE_EXACT_FLAT` → `G1=false`, G2–G6 not applicable
  (not a G3 refusal); `AVAILABLE` + non-finite G3 feature → `G3=false`, refused;
  M2-0 does not operate G3–G6 so its behaviour is identical with/without a null.
- **Recovery2 identity frozen**: `m2-v1-development-two-arm-recovery2`. Both
  consumed ids and every alternate name (`recovery3`, `attempt4`, timestamps,
  random suffixes) are refused.
- **Dual lineage**: 14 fields covering both prior attempts, validated by value,
  bound in every arm result, lock and suite.
- **Execution history** reports three attempts:
  `consumed_failed_pre_scoring` / `consumed_failed_pre_scoring_stream_assembly` /
  recovery2 state.

Full suite **1446 passed, 1 skipped**. ruff clean, format clean,
`git diff --check` clean.

## 4. THE OPEN GATE — start here

**Nothing is authorized right now beyond human review of PR #26.**

The likely next authorizations, in order:
1. Human merge review of PR #26 (possible further blockers).
2. After merge: a **recovery2 execution authorization** naming the new master
   SHA — the same seven-point preflight shape as before, plus verification of
   **both** prior failure lineages before any claim.
3. If recovery2 completes: **human bounded-Pareto M2 retention review**
   (M2-G retained only if materially safer on contamination/drift and/or false
   alarms while preserving detectability without unacceptable sensitivity loss,
   and not a trivial never-update gate). **Do NOT begin U1/U2 automatically.**

If recovery2 is ever claimed and fails: **STOP FOR HUMAN REVIEW.** Nothing
authorizes a further attempt.

## 5. The canonical route (as merged/pending)

Command shape (do **not** run without an explicit authorization naming the SHA):
```
/home/AI_POC/venvs/tactics/bin/python \
  -m cardiosentinel.neural.m2_development_run \
  --execute-canonical-development \
  --expected-git-sha <HUMAN_REVIEWED_MASTER_SHA>
```
Only those two flags exist. No partition, arm, threshold, retry, seed or
data-source option. Roots are deterministic (`canonical_roots()`):
`cardiosentinel-data/ltstdb/1.0.0`, `ltstdb-baseline-v1`,
`m1-stream-memory-v2`, `p1-b4b-embeddings-v1`, `phase5-m1-dual-memory-v2`,
`phase6-m2-development-v1`.

Order: pre-claim readiness (13 items) → START + claim M2-0 → claim M2-G →
evidence workspace → development source integrity → full label-blind VALIDATION
replay → post-replay PRIMARY / CHALLENGE / STRESS → frozen evidence → per-arm
result+lock → two-arm suite with its own PRE_PROMOTION.

**Four populations, never interchangeable:** FULL REPLAY (all causal rows, never
a metric denominator) · PRIMARY (473,897 / 21,628 / 452,269 / 12 subjects) ·
CHALLENGE (4,973 + 3,000 + 164 = 8,137, digest `49899d1b…`) · STRESS INTERVAL
(source-defined only; axis/conduction/point-noise are
`not_estimable_from_source_defined_LTSTDB_intervals` — never manufacture zeros).

## 6. Frozen M2-v1 constants (do not reopen)

- Arms **M2-0 (naive) vs M2-G (gated)**; rollback excluded; no arm selection.
- Gate order G1 available → G2 finite `z_t` → G3 SQI → G4 normal evidence →
  G5 refractory → G6 `morphology_valid == 1`.
- G3: six declared SQI columns (five independent), `finite_sample_fraction == 1.0`
  precondition, each `isfinite(v) and v <= frozen Q99 bound`.
- `NORMAL_EVIDENCE_THRESHOLD = 0.0002997174742631614`
- `M1L_CLASSIFICATION_THRESHOLD = 0.7554003000259399` (both arms; **no threshold
  search of any kind**)
- Refractory 60.0 s real elapsed, re-armable, keyed on `(start_sample + 2500)/250.0`
- `z_t` = [frozen B4-B 128 ; transformed morphology 18] = **146**; scorer input
  is `[z_t ; pre-update d_long]` = 147
- Prototype drift is exactly `sqrt(mean((mu_long(t) - mu_ref) ** 2))`
- `canonical_sha256` = `json.dumps(payload, sort_keys=True, separators=(",",":"))`
  hashed UTF-8
- `M2_INTRA_OP_THREADS`/torch thread pinning matters for numerical reproducibility

## 7. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/hash
  a B4 test cache or test waveform; inspect B4 test labels; calculate B4 test
  metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed: do
  not delete, reset, rename, re-root or reseed it. Stop and report.
- Keep scratch files OUTSIDE the repo. Do not add the Research Execution
  Handbook to the repo (it is not on this filesystem; repository protocols are
  the authority).
- Do not change code in response to scientific results.
- Patient identity selects a state namespace but is NEVER a predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access VALIDATION for threshold derivation. Do not access sealed TEST.
- Do not modify `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` — frozen
  historical science. Do not regenerate the TRAIN gate receipt.
- Do not merge PR #26. Do not execute recovery2.

## 8. Working preferences and hard-won lessons

- Read-only monitoring for long runs; **never** restart/retry logic, never
  relaunch a canonical run, never kill for slowness or high RSS.
- Report failures with exact exit codes and stage; describe OOM-like kills as
  "strongly consistent with process termination under host memory exhaustion",
  not "kernel OOM killer confirmed".
- Use `git commit -F <file>` (shell quoting has broken commit messages before).
- **Never run `ruff format` over a whole directory** — it swept 27 unrelated test
  files into a commit this session and had to be reverted and amended. Format only
  the files you changed.
- `gh pr edit --body-file` fails on this `gh` version with a projectCards GraphQL
  error; use `gh api -X PATCH .../pulls/N -F body=@file` instead.
- Test seams that inject past a component hide defects **in that component** —
  attempt #1 was invisible because the end-to-end test injected `stream_source`.
  Prefer driving the real component against synthetic on-disk fixtures.
- Long reports end with the exact mandated closing block when one is specified.

## 9. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG3
handoff: a concurrent session installed distributions into the then-shared
scientific interpreter while the canonical M1-v2 run was executing. Whether that
process loaded any added distribution **cannot be proven retrospectively**; all
read-only evidence is consistent with no effect. **M1-v2 remains the canonical
frozen M1 development evidence; do not rerun or modify it.**

Separately, this session: a `git add -A` executed in the OUTER `/home/AI_POC`
repository (working directory had reset) and the follow-up `git reset` unstaged
that repo's large pre-existing index. It was reconstructed with
`git add .gitignore && git add -u`, giving back `A .gitignore` + 41,921 staged
deletions + 321 staged modifications with 285 untracked entries, matching the
session-start snapshot. Outer HEAD `086ee281370c1e49b2665d33f5a615989c1dc6da`
was never changed and nothing was committed there. **That index was
reconstructed, not recovered** — worth a human glance.
