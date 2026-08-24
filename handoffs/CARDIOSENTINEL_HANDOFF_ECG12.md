# CardioSentinel — handoff to session "ECG 12"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG12.md and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use for CardioSentinel) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` (renamed `CardioSentinel-AI`) |

`tactics` holds the frozen 335-package set,
`installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`,
Python `3.12.6`. Verified intact throughout ECG 11. Never install, upgrade or
downgrade anything in it.

**Shell state:** the Bash working directory silently resets to `/home/AI_POC`.
Always `cd` explicitly before any `git`/`gh`/`pytest` command. Never run
`git add -A` anywhere near `/home/AI_POC`.

The remote prints "This repository moved" on every push. Noise, not an error.

---

## 1. THE HEADLINE — the canonical T1 attempt ran, and failed

**On 2026-08-21 the one canonical T1 attempt was authorized, executed, and
consumed.** It failed at stage 24 of 29. This is the single most important fact
in this handoff and everything below follows from it.

```
attempt_id      t1-v1-development
commit          c538181eb93884f4583a8bd328e50573efbcf3df
claimed         2026-08-21T19:47:24Z
failed          2026-08-21T19:57:57Z   (10 min 32.8 s)
terminal stage  promote_oof_result  (24 of 29)
exception       KeyError: 'true_positive'
```

**It is not a failed experiment. It is a failed evidence-persistence path.**
Ten of twelve scientific components are complete and frozen; the programme is
one measurement away from closing its last development-phase component.

### What completed and survives on disk

| Phase | State |
|---|---|
| Policy selection, all 12 folds | ✅ promoted, digest-verified, immutable |
| Held-out execution, all 12 folds | ✅ performed — but see below |
| Label-blind input evidence | ✅ 492,904 rows, digest-verified |
| OOF state evidence | ✅ 492,904 rows, cross-fitted, digest-verified |
| §19 OOF result and everything after | ❌ never written |

### What was lost, and why it matters

Stage 22 (`fold_promote_held_out_evidence`) was **entered as a stage marker and
wrote nothing**. The per-fold PRIMARY confusion counts, episode evidence and
onset latencies lived in `run.held_out_traces`, an in-process dict, and died
with the interpreter. The state *trace* survived only because stage 23 widened
it into the OOF store.

Those three label-derived quantities are the entire remaining gap. They cannot
be recomputed from the surviving artifacts, which are label-free by design.

### The defect

```
t1_fold_evaluator:479   produces  {"tp", "fp", "tn", "fn"}
t1_composition:261      pools and forwards unchanged
t1_assembly:336-339     reads  {"true_positive", "false_positive", ...}
```

Wrapped in a `_LazyMapping`, so it first resolved at stage 24 — after the claim,
after twelve folds. The pre-claim capability gate proves callable shape,
attestation and structural production of a value; it does not compare dict key
vocabularies. Fixed in PR #49.

---

## 2. Governance state — the recovery is authorized

`docs/T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md`, **frozen and merged**:

```
d3ea7734c93be8f59796e03e8c0210778716327f7adc033cb2d3dcfff7f92c96
```

A human authorized **one measurement continuation**. It amends exactly three
clauses — spec §1 (one alternate run root, one named identity), spec §17 and
protocol §14 ("once" / "exactly once" constrain decision-informing evaluation,
not evidence persistence) — and states every other clause of both governing
documents stands verbatim.

**The decisive narrowing, §9.1.** The continuation **consumes the persisted OOF
state trace and does not regenerate it**:

```
frozen predictions + held-out labels  ->  measurement
```

not `old experiment -> rerun -> new experiment`. The frozen state machine never
re-executes, the selected policy is not re-run, and the scientific claim rests
on the original immutable trace. Episode grouping and matching run through the
same frozen `t1_protocol` functions the consumed attempt used; the only new
input is the held-out labels.

**§13.6–§13.7** make that narrowing a mechanical authorization gate: four
zero-valued counters proven at three independent layers, carried by a promoted
execution attestation artifact.

### Continuation identity (amendment §7)

| | |
|---|---|
| Run class | `t1_continuation_measurement` |
| Attempt id | `t1-v1-measurement-continuation` |
| Run root | `cardiosentinel-runs/phase9-t1-continuation-v1` |

`t1-v1-development-continuation` would be **refused**: `t1-v1-development` and
`phase9-t1-development-v1` are canonical reserved prefixes matched by
case-insensitive prefix. Already asserted by a test.

**The continuation must refuse to start** unless the consumed attempt exists and
every bound digest re-verifies. A standalone continuation is unstartable by
construction — that is what makes it a continuation rather than a fresh
experiment wearing the name.

---

## 3. Where the PRs stand

Master is **`8db30ffc8800ee4ff20634231bd62e43020c10cd`**.

| PR | State |
|---|---|
| #47 authorization | ✅ merged |
| #48 amendment V1.1 | ✅ merged |
| #49 reliability hardening | ✅ merged, CI green |
| #50 §17 held-out persistence | ✅ merged, CI green |
| **#51 attempt tripwires** | 🟡 **open, CI re-running after a fix** |
| **#52 recovery prerequisites** | 🟡 **open, based on #51, CI re-running** |
| #53 continuation capability | ⏳ not started — the next PR |

**#52 is based on `research/t1-attempt-tripwires-v1`, not `master`.** Retarget it
to master once #51 merges.

### What #51 does

38 assertions across 11 suites asserted the canonical run directory did not
exist. True when written, permanently false since the attempt ran, and green on
CI only because `cardiosentinel-runs/` is gitignored. `tests/neural/_attempt_guard.py`
states the honest invariant — *the canonical attempt is exactly as this session
found it* — and `tests/neural/conftest.py` applies it after **every** test in the
package via one autouse fixture, covering ~2,800 tests instead of 38.

**Its first version failed CI by making the mirror-image mistake**: three tests
assumed the attempt is *present*, false on CI. Fixed with `ATTEMPT_PRESENT`, on
which tests branch rather than assuming either world.

### What #52 does

1. `src/cardiosentinel/neural/t1_recovery_amendment.py` — the amendment digest,
   version, path, amended clauses, continuation identity, the four zero
   counters, and `validate_recovery_amendment_document()`. **Provenance only, no
   logic.** Deliberately *not* in `t1_execution_spec.py`, which is byte-frozen.
2. `recovery/T1_FAILURE_RECEIPT_RECONSTRUCTED.json` — the §25 receipt the run
   never produced, reconstructed from surviving evidence, `receipt_type:
   "reconstructed"`, outside the consumed attempt. **Three lost quantities are
   named as not-reconstructed rather than invented**, and a test asserts no
   fabricated key ever appears.
3. `tests/neural/test_t1_recovery_prerequisites.py` — 31 acceptance gate tests.

---

## 4. Frozen digests

### Documents

| Document | SHA-256 |
|---|---|
| `T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md` | `ef044754020b1756ea7aae5fa1b747c5ba6fc0c8cd70d52e73185555897d70d4` |
| `T1_CANONICAL_DEVELOPMENT_EXECUTION_SPEC_V1.md` | `11b6a9aff2f1d928a9f33516db2ea764cf0553a949cd79c14562bafe34f090bf` |
| **`T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md`** | **`d3ea7734c93be8f59796e03e8c0210778716327f7adc033cb2d3dcfff7f92c96`** |
| `RUNTIME_INTEGRITY_SENTINEL_V1.md` | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |
| `T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md` | `6546086a55fe2c9c109f4121cdb6b42d4d53ce0112c9611eb895bd8c805cfefb` |
| `T2_CANONICAL_TRAINING_EXECUTION_SPEC_V1.md` | `af6ebf1a6314edb86cce7aa88a6260dd1bd155fd0aebe472d3745b6c823b8054` |
| `T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md` | `4846921135b0ac83ceb40a0db063c2e4a3b2520971f279abe4f0c517c4f7dd20` |
| `U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md` | `d6235b477af278fe051822bdcccb54f985e4eceb0c6e92c1424f5e9d7d79b33b` |
| `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` | `9d8436f2b7d2c303aeeb03e438c60fb8110f7d06d0bbd589f5be65ea8f80cb7b` |
| `M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | `da4a05b4e2e3dd633493b87a08ed369010fa91c9cac21d906980a658fcf2be47` |
| `M1_DUAL_MEMORY_PROTOCOL_V2.md` | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| Retention: B4-B `1300e7ad…` · P1-B `7b403709…` · M1L `a3685fc0…` | (files `B4_GLOBAL_ENCODER_SELECTION_V1.md`, `P1_PHYSIOLOGY_…`, `M1_MEMORY_…`) |

> **The split digest is NOT a file digest.** `66e25d77…` is
> `split_sha256(manifest)`; the raw file hashes to `74f055de…`. Both correct,
> not supposed to match. Verify with
> `cardiosentinel.evaluation.splits.split_sha256`, never `sha256sum`. ECG 10
> wasted time on this.

### Source modules — **three of these moved in ECG 11**

| File | SHA-256 | Status |
|---|---|---|
| `t1_protocol.py` | `b0df6ea2ade450037e94e5ab3b193694fea980337851a2458b3f43873450b192` | frozen, unchanged |
| `t1_execution_spec.py` | `edb0cbf1afe43dee48b5d2d0ed190e0939530fc026fd2f09d3312b929ab1fbe3` | frozen, unchanged |
| `t1_evidence_store.py` | `464ca1607191aa02042a6dcbb8cfeda4d4f3aced1eae2e29ae4b77be8cf6d39c` | frozen, unchanged |
| `t1_development_run.py` | **`ad08035d33a1f421cf5a6a18df33e9a7ed55fad29074e7581bbe3ba796b90a8e`** | changed in #50 |
| `t1_persistence.py` | **`77c0e0a40efa7056777ef8d3bb13983ae4cd1bb9493d3c6c7eb11c7faebd68ad`** | changed in #49 and #50 |

**Both `t1_development_run.py` and `t1_persistence.py` are pinned in four suites
each**: `test_t1_canonical_driver`, `test_t1_fold_authority`, `test_t1_assembly`,
`test_t1_fold_evaluation`. Re-cut both pins after any change, **after
formatting**, and format only the files you touched.

The three frozen sources are additionally pinned in seven suites. **Do not
modify them.** In particular, do not put the amendment digest in
`t1_execution_spec.py` — that was proposed in ECG 11 and correctly rejected.

### The consumed attempt's artifacts

`cardiosentinel-runs/phase9-t1-development-v1/t1-v1-development/`

| Artifact | SHA-256 (file) |
|---|---|
| `T1_PREFLIGHT.json` | `917b5421c9c7731eb185821ed279564c65fed5737153316cfa410811ea4f25da` |
| `T1_RUN_STATUS.json` | `f305da7ad3d465c4500124fe4d4422dfc471580a01afe7b9d424e866e9e2c59d` |
| `T1_INPUT_LINEAGE.json` | `e307bdd3ad244f6440ad437f66d5f7b4e2af3072b6b1833e74552095ede3c555` |
| `T1_INPUT_EVIDENCE.json` | `bf36ac0e538b0cee61a97109de413c52ec942356d974930e5de64bc32b86423b` |
| `t1_input_evidence.npz` | `4391b4e7cda5ac5d70c93663563cc37954afdfc7b28092ef65c2d351006c2f5c` |
| `T1_FOLD_SELECTIONS.json` | `71e0da62ad2a86fd6bb2561137e0a152df2d5b894bd9fecfb67ad762a5682f6d` |
| `T1_OOF_STATE_EVIDENCE.json` | `aefc922a5224b7c857b9bf99b12441e55e46fdc71def373c043ffb112e5e2405` |
| `t1_oof_state_evidence.npz` | `72f13a8b29eafdd99801bb64dbf8b61f19717f3d7af777d74f21c9709dd28232` |

Canonical payload self-digests: input evidence `57d434d9…`, OOF store
`cf74f00a…`, fold-selection binding `32bab16c…`. **File digests and payload
self-digests differ by design.**

The twelve fold selections are in `fold_selections/`, all twelve verifying by
`sha256_file` against the digests recorded in `T1_FOLD_SELECTIONS.json`. Note
the standalone files do **not** contain their own digest — a file cannot hold
its own hash. ECG 11 briefly mis-read this as a mismatch.

**Fold results:** 12/12 folds, 12 distinct held-out subjects, verified
subject↔fold bijection, `fold_retry_performed: false`. Eleven folds selected
`qw0.9_qe0.99_FAST`; fold 01 (s2005) selected `qw0.9_qe0.99_BALANCED`. States:
NORMAL 407,028 · WATCH 55,168 · EVENT 26,467 · RECOVERY 4,241; 8,832 transitions.
**Do not interpret these — no scientific analysis has been authorized.**

---

## 5. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- **The consumed attempt directory is immutable.** Not deleted, renamed,
  re-rooted, extended, tidied or made to look clean.
  `T1_FAILED_ATTEMPT_MAY_BE_DELETED_OR_REWRITTEN = False`.
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- **No M2 rerun. No U1 rerun. No T2 rerun. No T1 fold retry.**
- Keep scratch files **outside the repo** — see §7, this rule cost the first two
  launch attempts.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; it is NEVER a
  predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.
- **One continuation is authorized. If it fails post-claim, that is another
  documented human decision** — no second continuation is authorized by the
  amendment.

---

## 6. Open items carried into ECG 12

1. **Merge #51, then retarget and merge #52.** Both CI runs are in flight at
   handoff time. Check them first.
2. **PR #53 — continuation capability.** Scope, per the amendment and the human
   decision:
   - `predecessor verifier` — refuse to start unless every §1.3/§1.4 digest
     re-verifies
   - `continuation permission gate`
   - **negative capability gate** — the mirror of the pre-claim gate: it proves
     the graph *cannot do too much*
   - **persisted OOF trace consumer** — reads `t1_oof_state_evidence.npz`;
     **never regenerates the trace**
   - held-out label join → evaluation evidence
   - provenance blocks (`continues`, `consumed_evidence`)
   - **execution attestation artifact** with the four zero counters
   - No state machine. No policy selection. No thresholds. No fold evaluator.
3. **Then, and only then, the human decision to run the continuation.**
4. Afterwards: T1 evidence analysis, ablation package, E1 edge/HIL (still a
   2-line stub), paper package.
5. **The ECG 3 outer-repo index reconstruction** still merits a human glance.

---

## 7. Hard-won lessons from ECG 11

- **Keep the run log OUTSIDE the repo.** The first two canonical launch attempts
  wrote `nohup … > t1_canonical_run.log` into the repo root. The shell creates
  the redirect file *before* Python starts, so the run dirtied the tree it was
  about to verify and refused at stage 2. Both refusals were pre-claim and cost
  nothing, but they cost two attempts and twenty minutes.
- **`pgrep -f "t1_development_run"` matches your own bash wrapper.** A guard
  built on it aborts the launch it is protecting. Anchor the pattern:
  `pgrep -af "^/home/AI_POC/venvs/tactics/bin/python -m cardiosentinel"`.
- **A git worktree reproduces CI exactly.** It contains no gitignored files, so
  `git worktree add --detach <scratchpad>/ci-sim HEAD` and running pytest there
  reproduces CI's view of the repository. This caught the #51 failure locally in
  seconds. Remove it afterwards.
- **Assuming the consumed attempt is absent, and assuming it is present, are the
  same mistake.** Tests whose expected behaviour differs between the frozen
  interpreter and CI must branch on `ATTEMPT_PRESENT`, never assume.
- **Naive substring scans produce false positives — five times now.** A module's
  own refusal list contains the word it refuses; a provenance module's docstring
  necessarily says "claim" and "continuation". Scan the syntax tree or the
  import surface, never raw text.
- **`ast.walk` finds the wrong loop.** `stage_folds` opens with a `for stage in
  (...)` before the fold loop, so an AST probe must key on the loop that
  iterates `t1_folds()`.
- **`inspect.getsource` on a method needs `textwrap.dedent`** before
  `ast.parse`, or it raises IndentationError.
- **Do not serialise the local suite ahead of opening a PR.** CI runs the same
  suite; open the PR and let both run in parallel.
- **A handoff's claim about PR state is a hypothesis.** Run `gh pr list`,
  `git log --oneline -3`, `git status --porcelain` before assuming. ECG 11 was
  handed a claim that PR #51 was merged when it had not been written.
- **Check `ListAgents` and `git worktree list` before starting.** ECG 11 nearly
  duplicated a peer session's in-flight work; `git checkout -b` failing with
  "branch already exists" was the only warning.
- Never run `ruff format` over a whole directory — ECG 10 reformatted 61
  unrelated files. Format only what you changed, and re-cut digest pins
  **after** formatting.
- Use `git commit -F <file>` with the message file in the scratchpad.
- **`gh pr create --body-file` works.** `gh pr edit --body-file` does not; use
  `gh api -X PATCH repos/DebalekhaChakraborty/CardioSentinel-AI/pulls/N -F body=@file`.
  `gh pr edit --title` can fail on a projects-classic GraphQL error; the REST
  PATCH works.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`,
  and wait until no job is `IN_PROGRESS`/`QUEUED`/`PENDING`. Two jobs, ~7–8 min.
- Full suite ~15m30s. Launch long runs in the background.

---

## 8. Facts that are easy to get wrong

- **`T1_RUN_STATUS.json` in the consumed attempt reads `status: STARTED`** with
  `updated_at` equal to the claim timestamp, and `label_blind_input_opened`,
  `held_out_labels_opened_for_folds`, `oof_evidence_promoted` all false. Every
  one of those was false at 19:47:24 and none was true at 19:57:57. **It is left
  exactly as the run wrote it.** The truth is in
  `recovery/T1_FAILURE_RECEIPT_RECONSTRUCTED.json` (PR #52).
- **The run produced no failure receipt.** §25 requires one;
  `write_failure_receipt` and `T1DevelopmentRun.failure_receipt` were both
  implemented and neither was called, because the driver had no handler. Fixed
  in #49; the historical gap is filled by the reconstructed receipt.
- **`cardiosentinel-runs/T1/T1_state_machine_v1/` reads `status: COMPLETE`.** It
  is `run_class: harness_verification`, `protocol_evidence: false`. **Not T1
  evidence.**
- **"TEST is sealed" is only half true.** B0–B3 classical baselines already
  consumed one-shot sealed-test access in Phase 3B-1. The **B4/neural chain's**
  test is unopened, deferred by `B4_TEST_DEFERRAL_DECISION_V1.md`. Only the
  second is the live firewall.
- **1.9 GB of canonical run artifacts are gitignored and local-only**, including
  the consumed T1 attempt. Losing this disk destroys every M1/M2/U1/T2 result
  and the T1 evidence the continuation depends on. **None of it may be rerun.**
- **`recovery/` is tracked**, unlike `cardiosentinel-runs/`. That is deliberate:
  a governance record that exists on one disk only is not a record.

---

## 9. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG 3
handoff. **M1-v2 remains the canonical frozen M1 development evidence.** The
ECG 3 outer-repo index reconstruction also stands: that index was
**reconstructed, not recovered**, and is still worth a human glance.

M2 recovery2, the U1 canonical run, the T2 canonical TRAIN run and the T2
one-shot outer VALIDATION all ran clean against the frozen 335-package digest.

**The canonical T1 development attempt was executed on 2026-08-21 at commit
`c538181` and failed post-claim at stage 24. The attempt is consumed. TEST was
never opened. One measurement continuation is authorized by
`T1_EXECUTION_RECOVERY_AMENDMENT_V1_1` and has not been built or run.**

---

**The danger has shifted again.** ECG 11 began with "over-engineering before
running the experiment" and the experiment ran. What is dangerous now is
*haste*: the continuation is the single authorized remaining attempt, a
post-claim failure consumes it, and no second one is authorized. Every gate that
can be green before it starts should be green before it starts — which is what
#51, #52 and #53 exist to make true.
