# CardioSentinel — handoff to session "ECG 13"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG13.md and continue.
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
Python `3.12.6`. Verified intact throughout ECG 12. Never install, upgrade or
downgrade anything in it.

**Verify that digest with `provenance.dependency_environment()`, not a pip-freeze
hash.** A `pip list --format=freeze` digest gives a different value and means
nothing. ECG 12 wasted a step on this.

**Shell state:** the Bash working directory silently resets to `/home/AI_POC`.
Always `cd` explicitly. Never run `git add -A` anywhere near `/home/AI_POC`.

The remote prints "This repository moved" on every push. Noise, not an error.

---

## 1. THE HEADLINE — the continuation ran, and it completed

**On 2026-08-22 the single authorized measurement continuation was executed and
finished successfully.** This is the fact that changes everything relative to
ECG 12.

```
attempt_id        t1-v1-measurement-continuation
run class         t1_continuation_measurement
execution commit  61704aa7259d91eaf9d4dfc2502bf78881a05d61
authorization     b40b4acac16893dcb1af1f1fa91feb0d74c8a78d
started           2026-08-22T16:18:39Z
completed         2026-08-22T16:18:49Z   (10 seconds)
```

**The three lost quantities are recovered, 12/12 folds**: per-fold PRIMARY
confusion counts, per-fold episode evidence, per-fold onset latencies.

All four §13.7 counters read zero in the promoted attestation.
`state_transitions_regenerated: false`. `test_accessed: false`.
`sealed_test_state: unopened`. No file in the run contains `policy_runs`.

**The canonical attempt was never touched.** Still 20 files at
`2026-08-21T19:57:57`.

### It took two launches. The first was pre-claim.

The first invocation refused two seconds in:

```
TypeError: git_provenance() missing 1 required positional argument
runner.py:282  git_sha = _authorized_git_sha()   <- raised here
runner.py:288  _claim(attempt_dir)               <- never reached
```

Six lines short of the claim, so per §25 the attempt was **not consumed** and the
authorization survived. PR #59 fixed the argument and added the seam test that
should have existed first. The second launch crossed the claim and completed.

**Do not read that as luck.** Read §7.

---

## 2. Current state

Master is **`61704aa7259d91eaf9d4dfc2502bf78881a05d61`**. Working tree has one
untracked file (§3). **Zero open PRs.**

| PR | State |
|---|---|
| #48 amendment V1.1 · #49 reliability · #50 §17 persistence | ✅ merged |
| #51 attempt tripwires · #52 recovery prerequisites | ✅ merged |
| #53 continuation safety framework · #54 evidence contract | ✅ merged |
| #55 execution engine · #56 label authority integration | ✅ merged |
| #57 pre-authorization record · #58 **authorization** | ✅ merged |
| #59 seam hardening | ✅ merged |

---

## 3. Two things are open, and both are small

**1. `docs/T1_EVIDENCE_ANALYSIS_PLAN_V1.md` is untracked.** Written at the end of
ECG 12 from a structural inventory only — no measured value was read in preparing
it. It is a pre-registration. It needs human approval, then a PR.

**2. `recovery/T1_CONTINUATION_PREAUTHORIZATION.md` still reads
`Execution commit : pending`.** It should be filled with
`61704aa7259d91eaf9d4dfc2502bf78881a05d61`. Mechanical, but it is a governance
record, so it goes through a PR like everything else.

---

## 4. The continuation evidence

`cardiosentinel-runs/phase9-t1-continuation-v1/t1-v1-measurement-continuation/`
— 19 files, gitignored, local-only.

| Artifact | SHA-256 |
|---|---|
| `T1_OOF_RESULT.json` | `9309b00b55173e00ee793d2468b6aaf796105928c0e5241537ef3fe80ccec6ae` |
| `T1_SUBJECT_EVIDENCE.json` | `6695dd36d890dfdc5e6e6fa16514f2cee8676b7402ba93f0c0f9c10b27223120` |
| `T1_BOOTSTRAP.json` | `57ba66553e712a63b0f670cbb01bc9d680c824a90a2c9b723baa1aaa1adc0f48` |
| `T1_CHALLENGE_EVIDENCE.json` | `0eb8e684944da6768511d57264b20b8d201ab935bdb73125a0f41f9b3fed2d25` |
| `T1_FINAL_CONFIGURATION.json` | `374114293160c1f778a4803ff3a2d893d0eda2b81d6277ae326e201084495a34` |
| `T1_EXPERIMENT_LOCK.json` | `bcbdfdb08293b9c2ba7a9abef38d185e3128177c555b01dea0b81ec62f726a76` |
| `T1_V1_CONTINUATION_EXECUTION_ATTESTATION.json` | `b5a557dd40927999e00516e982c2f1619fdbeb3e5ebdd3ad108037b474eca588` |

Plus 12 `held_out_evaluations/T1_CONTINUATION_FOLD_NN_HELD_OUT.json`.

Every artifact carries `continues.predecessor_run = t1-v1-development`,
`predecessor_digest = cf74f00a…`, and 20 `consumed_evidence` entries. Every
digest the lock records re-verifies. **The lock omits its own digest** — a file
cannot digest itself, the same self-reference that made the authorization need
two commits.

### NOBODY HAS READ THE NUMBERS YET

ECG 12 inventoried **structure only** and deliberately did not read, report or
interpret a single measured value. Step 4 of the analysis plan is the first read.
**That should be a human, or an explicitly authorized analysis — not a side
effect of a status check.** Do not casually print the OOF result.

### The one availability fact you need before reading anything

| Slot | Defined |
|---|---|
| `episode_f1` | **12 / 12** subjects |
| `primary_window_mcc` | **5 / 12** subjects |
| `onset_latency_seconds_median` | **5 / 12** subjects |

The seven undefined-MCC subjects are *exactly* the seven undefined-latency
subjects, and all seven have a zero margin in their PRIMARY confusion. That is
documented frozen-helper behaviour: `window_mcc` is undefined on an empty margin,
and a subject with no matched episodes has no latency. Both refuse to report zero
because zero would read as a real measurement.

**The plan already fixes how this is reported** — per subject, undefined shown as
undefined, never omitted, never zero-filled. That decision was made before the
values were visible. **Do not renegotiate it after seeing them.** The bootstrap
is unaffected; it resamples `episode_f1` and reports 1000 defined replicates.

---

## 5. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- **The consumed attempt directory is immutable.** So, now, is the continuation
  run directory: §14 authorizes no second continuation, and none is predeclared.
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- **No M2 rerun. No U1 rerun. No T2 rerun. No T1 fold retry. No second
  continuation.**
- Keep scratch files **outside the repo**.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; it is NEVER a
  predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

---

## 6. Frozen digests

Unchanged through all of ECG 12. Re-verify before trusting anything.

| File | SHA-256 |
|---|---|
| `t1_protocol.py` | `b0df6ea2ade450037e94e5ab3b193694fea980337851a2458b3f43873450b192` |
| `t1_execution_spec.py` | `edb0cbf1afe43dee48b5d2d0ed190e0939530fc026fd2f09d3312b929ab1fbe3` |
| `t1_evidence_store.py` | `464ca1607191aa02042a6dcbb8cfeda4d4f3aced1eae2e29ae4b77be8cf6d39c` |
| `t1_development_run.py` | `ad08035d33a1f421cf5a6a18df33e9a7ed55fad29074e7581bbe3ba796b90a8e` |
| `t1_persistence.py` | `77c0e0a40efa7056777ef8d3bb13983ae4cd1bb9493d3c6c7eb11c7faebd68ad` |
| amendment V1.1 | `d3ea7734c93be8f59796e03e8c0210778716327f7adc033cb2d3dcfff7f92c96` |

Fast check: `sha256sum` those five and `md5sum` the result → `4107286307d147d542ff15e916225315`.

The consumed attempt's 8 §1.3 artifact digests and 12 §1.4 fold-selection digests
are in ECG 12 §4 and in `t1_continuation_spec.py`, which is the authority now —
read them from code, not from a handoff.

---

## 7. Hard-won lessons from ECG 12

- **"Unprovable by construction" was wrong, and I said it in every readiness
  report.** The claim was that `execute_continuation`'s assembled path could not
  be exercised without arming. It could: sandbox the run root, synthesize the
  labels, run it in a subprocess. The stages were each tested and the *junctions*
  were not, which is the same defect class that consumed the canonical attempt at
  stage 24. If you catch yourself writing "irreducible residue", check whether it
  is actually reducible with a sandbox.
- **Arming a flag can arm the test suite.** With `T1_CONTINUATION_AUTHORIZED =
  True` on disk, the runner's refusal tests stop refusing at stage 1, and
  `test_execute_refuses_before_resolving_anything` calls `execute_continuation`
  directly. A routine `pytest` could have consumed the attempt. `conftest.py` now
  forces the flag False for the session. The `_attempt_guard` fixture would only
  have noticed *afterwards*.
- **A record cannot contain its own hash.** The authorization needed two commits
  (flip, then record the flip's SHA). The experiment lock records six artifacts,
  not seven, for the same reason. Both are correct; both surprised a test.
- **A meta-test that counts is a meta-test that will break.** #51 asserted
  `len(fixtures) == 1` over `conftest.py`. True when written, and it silently
  locked the file to one autouse fixture forever. Name things, don't count them.
- **Check contracts against the real class, not a permissive stub.** #54's label
  adapter passed a directory where a filename was required, omitted a
  keyword-only argument, and never built the sponsoring authority — three defects,
  all invisible because the tests passed a bare `object()`.
- **`len()` of a validator's return value is not a field count.** The retention
  validators return a 64-char digest string; measuring `len()` gives 64 three
  times and means nothing. ECG 12 nearly reported that as a finding.
- **Substring false positives, now six times.** "edb" lives inside a SHA-256 hex
  digest. `is_continuation_artifact: False` contains the word "continuation".
  Scan the syntax tree or the import surface, never raw text.
- **Keep the run log OUTSIDE the repo.** The runner refuses a dirty tree at
  `_authorized_git_sha`. A redirect file in the repo root dirties it before
  Python starts.
- **`gh pr edit --base` fails on a projects-classic GraphQL error.** Use
  `gh api -X PATCH repos/…/pulls/N -f base=master`. `--body-file` works on
  `create` but not `edit`; use the same REST PATCH with `-F body=@file`.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`
  and wait until nothing is `IN_PROGRESS`/`QUEUED`/`PENDING`. Two jobs, ~7–8 min.
- Full suite is ~16 minutes and now **3061 passed, 1 skipped**. The skip is
  `test_m1_memory_scaling.py:117`, an opt-in `M1_STRESS_ROWS` stress —
  environmental, unrelated to T1, and it has skipped for many sessions.
- **Check `ListAgents` and `git worktree list` before starting.**

---

## 8. Facts that are easy to get wrong

- **The continuation succeeded; the canonical attempt is still failed.** Two
  different runs, two directories, both immutable. `T1_RUN_STATUS.json` in the
  *canonical* attempt still reads `STARTED` with every flag false, exactly as the
  failing run left it. Truth about that failure lives in
  `recovery/T1_FAILURE_RECEIPT_RECONSTRUCTED.json`.
- **`T1_CONTINUATION_AUTHORIZED` is `True` on disk and the authorization is
  spent.** It was consumed by a completed run, not a failed one. Do not re-run
  the continuation; §14 authorizes no second.
- **`t1_assembly` is deliberately not used by the continuation.** It binds no
  forbidden name but imports `t1_development_run`, which would give the
  continuation transitive reach the Layer 1 proof does not inspect. Four helpers
  are re-implemented in the continuation with equivalence tests. Do not "clean
  this up".
- **`FORBIDDEN_MODULES` and `NEVER_LOADED_MODULES` answer different questions.**
  The first is Layer 1 (what the proven graph may *name*), the second is Layer 2a
  (what may be in the *process*). `t1_development_run` is in the first and not
  the second, because the §16 label authority drags it in; its three entry points
  carry real call counters instead. A test asserts the two sets partition the
  forbidden set exactly.
- **`cardiosentinel-runs/T1/T1_state_machine_v1/` reads `status: COMPLETE`.** It
  is `run_class: harness_verification`, `protocol_evidence: false`. Not evidence.
- **"TEST is sealed" is only half true.** B0–B3 consumed one-shot sealed-test
  access in Phase 3B-1. The **B4/neural** chain's test is unopened, deferred by
  `B4_TEST_DEFERRAL_DECISION_V1.md`. Only the second is the live firewall.
- **No external validation exists, and EDB is not a clean one.**
  `CROSS_DATASET_PROVENANCE.md` documents that ten LTSTDB recordings come from
  the same Pisa collection as EDB, with verified record-level correspondences.
  The `data/edb.py` parser exists; no EDB data is on disk and no neural phase
  uses it.
- **U1 was a *split* retention.** Platt calibration retained; the selective
  router explicitly **not** retained. Any doc claiming "edge/cloud routing done"
  is wrong.
- **~23 GB of run artifacts and features are gitignored and on one disk**,
  including the consumed attempt and now the continuation evidence. None of it
  may be rerun. This is the largest unmanaged risk in the programme.

---

## 9. Open items for ECG 13

1. **Approve the analysis plan**, then PR it together with the
   `Execution commit` fill-in. Both are in §3.
2. **The descriptive report** — §4 of the plan. This is the first read of the
   measured values. A human should be in the loop.
3. **Ablation package** — separate decision, after the report.
4. **External validation strategy** — the milestone that decides whether any of
   this generalizes. Everything currently rests on 12 validation subjects from
   one dataset whose obvious second dataset is provably contaminated with the
   first. This, not the ablation, is the highest-value next scientific step.
5. **Paper assembly.**
6. E1 edge/HIL is still a 2-line stub; `edge/`, `episodes/`, `personalization/`
   and `uncertainty/` are empty packages. No inference or serving path exists
   anywhere — no `predict()`, no ONNX, no TorchScript.
7. **The ECG 3 outer-repo index reconstruction** still merits a human glance.

---

## 10. Execution-integrity record (do not soften)

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

**The danger has shifted again.** ECG 11 was over-engineering before running.
ECG 12 was haste — and the first launch proved it, refusing on a missing argument
that a sandbox would have caught in a minute. What is dangerous now is
**premature interpretation**. The numbers exist and nobody has looked. The plan
that says how to report them was written before anyone could, and that ordering
is the only thing making it a pre-registration rather than a rationalization.
Approve it, then read them — in that order.
