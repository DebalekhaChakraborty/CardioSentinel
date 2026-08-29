# CardioSentinel — handoff to session "ECG 11"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG11.md and continue.
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
Python is `3.12.6`. Verified intact at the end of ECG 10. Never install, upgrade
or downgrade anything in it.

**Note on shell state:** the Bash working directory silently resets to
`/home/AI_POC` (the OUTER repo). **Always `cd` explicitly to the CardioSentinel
repo before any `git`/`gh`/`pytest` command.** Never run `git add -A` anywhere
near `/home/AI_POC`.

The remote prints "This repository moved" on every push. Noise, not an error.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

Ladder, frozen: **B4-B → P1-B → M1L → M2-G → U1 Platt calibration → T2
`causal_s4d_longitudinal_v1` → T1.**

Master is **`64d5fc91c225266fb958c4f99752afc17714786d`** (merge of PR #45).

Test suite: **2765 collected**, full run ~15m30s.

**No T1 scientific execution has occurred.** No canonical T1 run directory
exists. VALIDATION has been read by no T1 code. The B4/neural TEST is sealed.

## 2. THE OPEN GATE — start here

The four-layer peel is finished except the last two:

```
Capability     ✅  (#35–#38, #40–#44)
Reachability   ✅  (#45)
Permission     ❌  <- next
Execution      ❌
```

**`execute()` now refuses on permission alone.** The capability graph is
complete (8/8 collaborators attest `executes=True`), the composition root
resolves all four frozen artifacts and 12 U1 calibrators, and
`main()` runs: parse → permission gate → compose → capability gate →
`T1CanonicalDevelopmentExecutor.execute()`.

`T1_EXECUTION_SPECIFICATION_AUTHORIZED` is still `False` and is the only
blocker.

### PR #39 must be CLOSED AND REPLACED, not rebased

This is the most important finding of ECG 10. **Do not merge #39.**

It is 17 commits behind master and its `t1_development_run.py` diff (74 lines)
was written against the pre-#44 entrypoint. Merging it would:

1. **Revert #45's entrypoint wiring.** Its `main()` contains zero references to
   `T1CanonicalDevelopmentExecutor` or `executor.execute` — verified. The
   result would be an *authorized* system that still cannot run: the flag says
   yes while the path goes nowhere.
2. **Add a second permission gate.** It introduces
   `t1_config.require_canonical_execution_authorized()`, which does not exist
   on master; master's entrypoint uses
   `t1_canonical_driver.require_canonical_execution_capability()`. Two doors
   where the design has deliberately had one.
3. Carry refusal prose that is now false on every count — "nothing sequences
   them", "requires a fold evaluator no caller supplies", "the 29-stage
   orchestration ... not implemented in this module".

Its 390-line `tests/neural/test_t1_execution_authorization.py` is worth
salvaging; port the tests whose premises survive.

**The replacement should be minimal:**

```
T1: authorize canonical execution after capability completion
```

- flip one constant in `t1_config.py`
- do NOT touch `t1_development_run.py`
- do NOT add a second gate
- port surviving authorization tests, dropping any that assert the entrypoint
  stops at preflight

### BLOCKER: the working tree is dirty

At the end of ECG 10 the tree carried uncommitted changes **from another
session** (not from the ECG 10 work):

```
 M README.md
 M docs/IMPLEMENTATION_PLAN.md
 M docs/RESEARCH_SCOPE.md
?? docs/CURRENT_STATE.md      (255 lines, self-described living state doc)
```

`stage_preflight` requires a clean tree and will refuse. These must be
committed or reverted by whoever owns them. **ECG 10 did not touch them.**

### The exact command, once authorization is merged

**The SHA to authorize does not exist yet.** It is the merge commit of the
replacement authorization PR, because that PR changes `t1_config.py` and the
authorized SHA must name the code that actually runs. **Do NOT use
`64d5fc91…`** — that is master before authorization.

```
cd /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
git checkout master && git pull --ff-only origin master
git rev-parse HEAD        # <- the SHA to authorize
git status --porcelain    # <- must be empty

/home/AI_POC/venvs/tactics/bin/python \
  -m cardiosentinel.neural.t1_development_run \
  --execute-canonical-development \
  --expected-git-sha <that SHA>
```

Launch with Bash `run_in_background: true` — foreground caps at 10 minutes and
twelve folds over ~493k rows will exceed it.

**This command consumes the one canonical T1 attempt.** No retry, no resume, no
recovery. Re-run the readiness checklist (§9) against the new master first.

**Do NOT enable authorization, run the harness, or open TEST automatically.**

## 3. What happened in ECG 10

Six PRs. All merged except the authorization one.

1. **PR #43** — pre-claim capability gate hardening + label-bearing assembly
   collaborators. Found the defect that `require_complete` only checked
   `callable`, so a refusal-only evaluator could reach `stage_claim` and spend
   the attempt.
2. **PR #44** — the canonical fold evaluator, the last missing scientific
   component. Required two `stage_folds` changes: thread the stage 12 columns
   in, and invoke a post-barrier held-out phase using the `held_out_authority`
   that was already built and discarded.
3. **PR #45** — four commits: narrow post-trace challenge reader
   (`t1_challenge`), subject evidence from held-out evaluations, final
   all-VALIDATION configuration selection (§23), and the composition root
   (`t1_composition`) with the `main()` wiring.
4. **Readiness audit v2** — 13 of 14 items green; the dirty tree is the one
   blocker, and #39 must be replaced.

Full-suite progression: 2501 → 2636 → 2676 → 2697 → 2720 → 2745 → 2764 passed.

## 4. Frozen digests

| Document | SHA-256 |
|---|---|
| `docs/T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md` | `ef044754020b1756ea7aae5fa1b747c5ba6fc0c8cd70d52e73185555897d70d4` |
| `docs/T1_CANONICAL_DEVELOPMENT_EXECUTION_SPEC_V1.md` | `11b6a9aff2f1d928a9f33516db2ea764cf0553a949cd79c14562bafe34f090bf` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` | `cd5c2e6d0b5dbc4ea35b319f98e9b9e678256c391491839d3f1745247eeb4075` |
| `docs/T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md` | `6546086a55fe2c9c109f4121cdb6b42d4d53ce0112c9611eb895bd8c805cfefb` |
| `docs/T2_CANONICAL_TRAINING_EXECUTION_SPEC_V1.md` | `af6ebf1a6314edb86cce7aa88a6260dd1bd155fd0aebe472d3745b6c823b8054` |
| `docs/T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md` | `4846921135b0ac83ceb40a0db063c2e4a3b2520971f279abe4f0c517c4f7dd20` |
| `docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md` | `d6235b477af278fe051822bdcccb54f985e4eceb0c6e92c1424f5e9d7d79b33b` |
| `docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` | `9d8436f2b7d2c303aeeb03e438c60fb8110f7d06d0bbd589f5be65ea8f80cb7b` |
| `docs/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | `da4a05b4e2e3dd633493b87a08ed369010fa91c9cac21d906980a658fcf2be47` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` | `31a81358870cd23c2258cf4f307ab8c4dc7bf245bc4bf18a4d1f48fe2aada39c` |
| Feature corpus `ltstdb-baseline-v1` | `f18785d520828cb171482926922346dda824c8868ed4b7f9be45897cd71d6eb5` |
| Split `protocols/splits/ltstdb_v1.json` (**canonical payload**, see below) | `66e25d77b6aaa25502974b4b60667b4c4b24d649bf9493666827c747a385ced7` |
| Retention: B4-B `1300e7ad641df9137e1722771e5d3932cae0fc4d244047b7c8a5070f151f74bb` · P1-B `7b403709fa0fb12eef65423d830c121fc3ada904266a1b47931d438f5e797d68` · M1L `a3685fc0f8ff1fa0dce2bf9954bb28a925787070c021f3e80ca5716a4fa5f0ed` | |

> **The split digest is NOT a file digest.** `66e25d77…` is
> `split_sha256(manifest)` = `sha256_canonical(_assignment_payload(manifest))`,
> which hashes only the canonical subject/record partition assignment and
> deliberately excludes surrounding metadata. The raw file hashes to
> `74f055dee370ab2742b2a5346eb37de4d3f6fccb011676b203b3eb339a62d714`. Both are
> correct and they are not supposed to match; ECG 10 wasted time on this.
> Verify with `cardiosentinel.evaluation.splits.split_sha256`, never `sha256sum`.

**The three genuinely frozen T1 sources — unchanged through six PRs.**
A test in five suites asserts each byte-for-byte:

| File | SHA-256 |
|---|---|
| `t1_protocol.py` | `b0df6ea2ade450037e94e5ab3b193694fea980337851a2458b3f43873450b192` |
| `t1_execution_spec.py` | `edb0cbf1afe43dee48b5d2d0ed190e0939530fc026fd2f09d3312b929ab1fbe3` |
| `t1_evidence_store.py` | `464ca1607191aa02042a6dcbb8cfeda4d4f3aced1eae2e29ae4b77be8cf6d39c` |

`t1_development_run.py` is **`0077bb8e2c4d3996cb44657e36d3a380556386d026fd17ae74139b96c2464594`**.
It changed deliberately twice (#44 fold wiring, #45 entrypoint) and its pin is
carried in four suites. **Re-cut the pin after any further harness change, and
re-cut it AFTER formatting, not before.**

## 5. The T1 layer — what each module is

| Module | Role |
|---|---|
| `t1_protocol.py` | The frozen science. States, evidence formulas, three persistence profiles, order-statistic rule, `next_state`, episode grouping, matching, `policy_sort_key`, LOSO folds. **Never re-derive this.** |
| `t1_execution_spec.py` | Non-scientific mechanics binder: identity, 29-stage order, CLI contract, artifact plan, refusals. |
| `t1_config.py` / `t1_stream.py` / `t1_engine.py` / `t1_execution.py` | The **model-agnostic engine**: runs the frozen machine on any producer's window evidence. NOT the canonical harness. |
| `t1_evidence_store.py` | Typed stores + **member-restricted, label-blind** upstream readers. |
| `t1_persistence.py` | Claim, stage ordering, promotion, experiment lock, failure receipts. |
| `t1_development_run.py` | The canonical 29-stage harness, fold firewall, metrics, `main()`. |
| `t1_canonical_driver.py` | Sequences all 29 stages; owns `T1ExecutionCollaborators`. |
| `t1_capability_gate.py` | **Pre-claim gate.** Shape + attestation + structural proof. |
| `t1_fold_authority.py` | `FoldScopedEvaluationAuthority`, scopes `(fit, held_out)` only. |
| `t1_fold_evaluation.py` | `T1CorpusTargetSource` + `T1NonExecutingFoldEvaluator` (the negative control). |
| `t1_fold_evaluator.py` | **`T1CanonicalFoldEvaluator`** — the real scientific body. |
| `t1_assembly.py` | Pure arranger: no path, no archive, no reader. |
| `t1_challenge.py` | Narrow **post-trace** `target_family` reader. |
| `t1_final_configuration.py` | §23 all-VALIDATION selection + `FinalValidationAuthority`. |
| `t1_composition.py` | **The composition root.** Resolves, binds, delegates. Computes nothing. |

**Canonical identity:** experiment `T1_state_machine_v1`, attempt
`t1-v1-development`, run root `cardiosentinel-runs/phase9-t1-development-v1`.

## 6. Governance mechanisms a new session must not weaken

- **The pre-claim capability gate is three independent checks.** Shape
  (`Signature.bind`, never invoking), attestation (positive
  `t1_execution_capability`; silence is refusal — an allowlist, because a
  denylist would admit the next placeholder written), and structural proof (a
  body with no reachable `return` cannot produce what the next stage consumes).
  **When attestation and proof disagree, the proof wins.**
- **`evaluate_fold` is two calls, not one.** Selection before the fold barrier,
  held-out evaluation after it. The gate proves both halves before the claim.
- **The fold barrier is enforced by object graph, not by a branch.** Selection
  takes a FIT-scoped authority which refuses the held-out subject;
  `held_out_evaluation_authority` only constructs after the fold's selection
  artifact is promoted and re-read with a verified digest.
- **The evaluator holds nothing.** Frozen, slotted, zero fields — nowhere to
  put a path, frame or source. Row membership comes from the authority's
  `stable_id` tuple, never from a `subject_id` predicate over the columns.
- **`T1_AUTHORITY_SCOPES` is exactly `(fit, held_out)` and must stay so.**
  `FinalValidationAuthority` is a separate *type* precisely so no fold-path
  caller can construct an all-twelve authority. Mutually unusable by type.
- **The challenge reader is a second narrow door, never a widening.**
  `read_t2_identity_members` still refuses `target_family` at stage 12; the
  §22 join reads it at stage 26, after every state and policy is fixed.
- **The assembly layer is a pure arranger.** Tests assert it names no path,
  opens no archive and calls no reader. Anything that must read goes elsewhere.
- **Subject-level metrics come from held-out evaluations, not OOF columns.**
  The OOF store is label-free by design; fold index ↔ held-out subject is a
  bijection, checked both ways and against the roster.
- **Undefined metrics stay undefined.** `None`/NaN, never a silent zero.
- **Canonical namespace protection covers the PATH, not just the name.**

## 7. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed.
- **No M2 rerun. No U1 rerun. No T2 rerun. No T1 fold retry.**
- Keep scratch files OUTSIDE the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; it is NEVER a
  predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

## 8. Facts that are easy to get wrong

- **`cardiosentinel-runs/T1/T1_state_machine_v1/` reads `status: COMPLETE`.**
  It is `run_class: harness_verification`, `protocol_evidence: false`. **Not T1
  evidence.** The canonical `phase9-t1-development-v1/` does not exist.
- **"TEST is sealed" is only half true.** B0–B3 classical baselines already
  consumed one-shot sealed-test access in Phase 3B-1 (`metrics_test.json` holds
  real numbers, per the frozen protocol). The **B4/neural chain's** test is
  unopened, deliberately deferred by `B4_TEST_DEFERRAL_DECISION_V1.md`. Only the
  second is the live firewall.
- **The B4-B encoder is deliberately NOT resolved by the composition root.**
  T1 never runs it; it consumes persisted M2-G and T2 scores. Binding a file
  the run never reads would be fake provenance. Encoder identity belongs in the
  experiment lock.
- **1.9 GB of canonical run artifacts are gitignored and local-only.** Losing
  this disk destroys every M1/M2/U1/T2 result, none of which may be rerun.

## 9. The authorization readiness checklist (re-run before the run)

**Repository:** clean tree · authorized SHA = merge commit of the authorization
PR (`git rev-parse HEAD` after merge, never guessed).

**Scientific chain:** B4-B `1300e7ad…` · P1-B `7b403709…` · M1L `a3685fc0…` ·
M2-G `da4a05b4…` · U1 `9d8436f2…` · T2 `48469211…`. Validators must return
M2 PASS (17 bound fields), U1 PASS (35), T2 PASS (36).

**T1:** `execution_graph_complete=True` with 8/8 attesting · composition
resolves 4 artifacts + 12 calibrators · `main()` reaches the executor ·
`T1_EXECUTION_SPECIFICATION_AUTHORIZED is False` until the deliberate flip.

**Safety:** no `phase9-t1-development-v1` · no `TEST_ATTEMPT*` · no
`T1_RESULT.json` / `T1_OOF_RESULT.json` / `T1_EXPERIMENT_LOCK.json` /
`T1_FOLD_SELECTIONS.json` / `T1_SUBJECT_EVIDENCE.json` · runtime digest matches
frozen.

At the end of ECG 10 this was **13 of 14 green**; only the dirty tree failed.

## 10. Working preferences and hard-won lessons

- **A handoff's claim about PR state is a hypothesis, not a fact.** Run
  `gh pr list --state open`, `git log --oneline -3`, `git status --porcelain`
  before assuming. Master moved mid-session three times in ECG 10.
- **Never run `ruff format` over a whole directory.** ECG 10 did this once and
  reformatted 61 unrelated files; they had to be reverted file by file. Format
  only the files you changed, and re-cut any digest pin **after** formatting.
- **Naive substring scans produce false positives.** ECG 10 hit this four
  times: a module's own refusal list contains the word it refuses, and a
  receipt asserting `labels_opened: False` contains "label". Scan
  docstring-stripped code, or check the import surface, never raw text.
- **Any digest computed from an interpreter's internal serialisation is not a
  file invariant.** CI runs 3.11; tactics runs 3.12. Digest bytes, never
  `ast.dump`, `repr`, `pickle` or set/dict order.
- **The frozen dependency digest only holds in `tactics`.** CI installs a
  different set, so tests claiming canonical state need
  `pytest.mark.skipif` on the observed digest, with a separate refusal test
  that runs everywhere. `test_t1_composition.py` uses this for the artifacts.
- **Launch long runs with Bash `run_in_background: true`**; foreground caps at
  10 min. Full suite ~15m30s.
- Use `git commit -F <file>` with the message file in the scratchpad.
- **`gh pr create --body-file` WORKS.** Only `gh pr edit --body-file` fails; use
  `gh api -X PATCH repos/DebalekhaChakraborty/CardioSentinel-AI/pulls/N -F body=@file`.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`.
- **CI monitors must wait for ALL jobs** — exit only when none is
  `IN_PROGRESS`/`QUEUED`/`PENDING`. Two jobs; ~7–8 min.
- **Another session shares this machine.** ECG 10 saw a concurrent pytest run
  and foreign doc edits appear mid-session. Check `ps` and `git status` before
  concluding something is yours.
- Long reports end with the exact mandated closing block when one is specified.

## 11. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG 3
handoff. **M1-v2 remains the canonical frozen M1 development evidence; do not
rerun or modify it.** The ECG 3 outer-repo index reconstruction also stands:
that index was **reconstructed, not recovered**, and is still worth a human
glance.

M2 recovery2, the U1 canonical run, the T2 canonical TRAIN run and the T2
one-shot outer VALIDATION all ran clean against the frozen 335-package digest.

**No T1 execution of any kind has been performed and no canonical T1 run
directory exists.**

## 12. Open items carried into ECG 11

1. **Resolve the dirty tree.** Three modified docs + `docs/CURRENT_STATE.md`,
   owned by another session. Blocks preflight.
2. **Close PR #39; open the minimal replacement.** One constant, no harness
   change, no second gate.
3. **Re-run the §9 checklist against the new master**, then the human
   authorization decision.
4. **One canonical T1 execution.**
5. Afterwards: T1 evidence analysis, ablation package, E1 edge/HIL (still a
   2-line stub), paper package.
6. **The ECG 3 outer-repo index reconstruction** still merits a human glance.

---

**The danger has inverted.** At the start of this project it was
"authorization before capability". It is now "over-engineering before running
the experiment". The machine is finished and is saying: *I am ready, give me
permission.* The next merge after the authorization replacement should be the
last gate before the first canonical T1 run. Resist adding capability.
