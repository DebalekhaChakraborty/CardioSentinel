# CardioSentinel — handoff to session "ECG 10"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG10.md and continue.
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
Python is `3.12.6`. Verified intact at the end of ECG 9. Never install, upgrade
or downgrade anything in it.

**Note on shell state:** the Bash working directory silently resets to
`/home/AI_POC` (the OUTER repo). **Always `cd` explicitly to the CardioSentinel
repo before any `git`/`gh`/`pytest` command.** This bit twice in ECG 9. Never
run `git add -A` anywhere near `/home/AI_POC`. Outer HEAD is
`086ee281370c1e49b2665d33f5a615989c1dc6da` and must stay that way.

The remote prints "This repository moved" on every push. Noise, not an error.

## 1. Program state

Protocol-governed ECG ischemia-detection research. Every user turn is a numbered
**human authorization boundary**. Frozen documents carry pinned SHA-256 digests;
a byte change is a hard refusal.

Ladder, frozen: **B4-B → P1-B → M1L → M2-G → U1 Platt calibration → T2
`causal_s4d_longitudinal_v1` → T1 protocol → T1 execution specification → T1
model-agnostic engine → T1 canonical development harness.**

Master is **`5804e66668dda062a7dfe2d3a5bb3a43bff7ee5e`** (merge of PR #38).

**THERE ARE NO OPEN PRs.** Everything ECG 9 built is merged.

**No T1 scientific execution has occurred.** No canonical T1 run directory
exists. VALIDATION has not been read by any T1 code. TEST is sealed.

## 2. THE OPEN GATE — start here

Everything mechanical is finished. **One deliberate human act remains.**

`cardiosentinel.neural.t1_development_run.main()` currently ends in a refusal:

> a merged specification is a contract and a merged harness is a capability;
> neither is a permission.

Running the canonical command today produces that refusal, **not a run**.
Turning it into an execution is a code change that was deliberately NOT made in
ECG 9. It is the single point at which the one canonical T1 attempt gets
consumed, and it must be its own reviewable PR.

The authorization review at the end of ECG 9 returned **GO on all eight
validation items**:

| # | Item | Status |
|---|---|---|
| 1 | Harness SHA binding | PASS — `5804e666…`, clean tree |
| 2 | Runtime identity | PASS — digest matches, 335 packages, 8 enforcement points |
| 3 | Attempt identity | PASS — `t1-v1-development`, deterministic |
| 4 | Run root reservation | PASS — `phase9-t1-development-v1` absent |
| 5 | TEST unopened | PASS |
| 6 | VALIDATION unopened | PASS |
| 7 | No retry/recovery path | PASS |
| 8 | No protocol drift | PASS |

Upstream re-verified read-only: M2 PASS (17 bound fields), U1 PASS (35), T2
PASS (36).

### The exact command, once execution is authorized

```
/home/AI_POC/venvs/tactics/bin/python \
  -m cardiosentinel.neural.t1_development_run \
  --execute-canonical-development \
  --expected-git-sha <MERGE_COMMIT_OF_THE_ENABLING_PR>
```

**Do NOT reuse `5804e666…` as the expected SHA if the enabling change lands as a
new commit.** The SHA names the code that runs, and enabling execution changes
that code. Re-run the eight-item checklist against whatever master becomes.

**Do NOT enable execution, run the harness, open TEST or choose a router
automatically.**

## 3. What happened in ECG 9

Eleven authorization boundaries. Four PRs opened and merged.

1. **PR #35 discovered never opened.** The ECG 9 handoff said it was "in
   progress"; ECG 8 had ended before the commit step. Re-ran the gauntlet,
   committed `7544ad0`, opened PR #35, CI green. Merged `9fa7e88`.
2. **PR #35 body provenance alignment** — eight explicit scope declarations,
   metadata only.
3. **T1 model-agnostic episode-state engine** → PR #36 (`f30350d`).
4. **T1 canonical development execution specification** → PR #37, merged
   `7242995`. Included the comment-only `§N` repair to `t1_protocol.py`.
5. **Implementation review of PR #36** — found it was NOT the canonical harness,
   and had never been checked against the spec because it predated it.
6. **PR #36 hardening** (`c472fba`) — three findings fixed. Merged `2672a72`.
7. **T1 canonical development harness** → PR #38 (`2feb76c` + `f91c417`).
   Merged `5804e666`.
8. **Execution authorization review** — GO on all eight items, blocked only on
   the deliberate enabling act.

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
| Split `protocols/splits/ltstdb_v1.json` | `66e25d77b6aaa25502974b4b60667b4c4b24d649bf9493666827c747a385ced7` |
| U1 OOF evidence store | `b95f484c9a7b08447f5a5d4330528136e040cf05acb9e2f7e54305e20bdffcba` |
| T2 outer result | `c58ed40dac753157b00ce6c70eb52fe903ecee72a5ef84e40932c1a80e259dbf` |
| T2 row-evidence content | `2240ca683fbcb790609c47f4a82af85250abb281fbbb9751dc74607a4eb591ca` |

T1 source files on master (code, not protocol-frozen):

| File | SHA-256 |
|---|---|
| `t1_protocol.py` | `b0df6ea2ade450037e94e5ab3b193694fea980337851a2458b3f43873450b192` |
| `t1_execution_spec.py` | `edb0cbf1afe43dee48b5d2d0ed190e0939530fc026fd2f09d3312b929ab1fbe3` |
| `t1_config.py` | `5e0fc6c2e458a19f59ac78a0beb90eaa0f885f8ccda222105cb733f159aa84af` |
| `t1_stream.py` | `ecca64ebf21f15282b10af358dd1cead952f201a5ea1ec8e740f95bdad9301eb` |
| `t1_engine.py` | `0bb3a71e0926c96f903d62c13fe880d8d48c9193593be90e019ff4bee30fae7b` |
| `t1_execution.py` | `263f9b6109d70d481687a85934655c96bc627fa75e7ecbbc366115f98dd20488` |
| `t1_evidence_store.py` | `464ca1607191aa02042a6dcbb8cfeda4d4f3aced1eae2e29ae4b77be8cf6d39c` |
| `t1_persistence.py` | `f715871bd1213d7605aa9b9117c0b8d1a86470b939e04e1df8614a9f982697df` |
| `t1_development_run.py` | `2fb3d7494363ee41be157bdf9a88db3f9852a1606024acb90193ed538f04d358` |
| `configs/t1_episode.yaml` | `d5ec66fad71c77edc26cf30329b27459eba770f1f0b66b42dd6dfb1006284e60` |
| `docs/t1_episode_reasoning.md` | `efdda6b2417b4fde3e4267b02560da7d84abd5ce2a5975d01d65790fdf28368e` |

The `t1_protocol.py` **comment-only `§N` repair is DONE** (the ECG 9 open item).
Its comment-stripped digest, base and repaired alike, is
`66548c4ced7513ccbf83781417e5cd23fd3293f49fa0079873834f3c4d6ec17c`, bound in a
test.

## 5. The T1 layer — what each module is

| Module | Role |
|---|---|
| `t1_protocol.py` | The frozen science. States, evidence formulas, three persistence profiles, order-statistic rule, `next_state`, episode grouping, matching, `policy_sort_key`, LOSO folds. **Never re-derive this.** |
| `t1_execution_spec.py` | Non-scientific mechanics binder: identity, 29-stage order, CLI contract, artifact plan, refusals. |
| `t1_config.py` / `t1_stream.py` / `t1_engine.py` / `t1_execution.py` | The **model-agnostic engine**: runs the frozen machine on any producer's window evidence. NOT the canonical harness. |
| `t1_evidence_store.py` | Typed stores + **member-restricted** upstream readers. |
| `t1_persistence.py` | Claim, stage ordering, promotion, experiment lock, failure receipts. |
| `t1_development_run.py` | The canonical 29-stage harness, fold firewall, metrics, CLI. |

**Canonical identity:** experiment `T1_state_machine_v1`, attempt
`t1-v1-development`, run root `cardiosentinel-runs/phase9-t1-development-v1`.

**Three separate facts, deliberately not conflated** (`t1_config.py`):

```
T1_EXECUTION_SPECIFICATION_EXISTS        True
T1_CANONICAL_DEVELOPMENT_HARNESS_EXISTS  True
T1_EXECUTION_SPECIFICATION_AUTHORIZED    False   <- the only one that gates
```

## 6. Governance mechanisms a new session must not weaken

- **The fold label firewall is an object graph, not a branch.**
  `FoldScopedTargetAuthority` is built over an explicit subject set and refuses
  every subject outside it. There is deliberately **no method returning "all
  labels"**, and a test asserts the absence. `held_out_authority` is only
  constructible after the fold's selection artifact is promoted AND re-read with
  a verified digest.
- **The convenience T2 readers are not label-blind.** `read_t2_outer_row_group`
  materialises every manifest column, which for the row identity includes
  `label`, `target_family`, `primary_mask`. Use
  `t1_evidence_store.read_t2_identity_members` instead. `read_t2_selected_scores`
  deliberately skips `predicted_positive`. `read_m2g_row_evidence` refuses
  `update_admitted`.
- **Canonical namespace protection covers the PATH, not just the name.**
  `canonical_namespace_would_be_materialised` refuses any run whose target is,
  or is under, the canonical run root — including relative and `..` forms.
- **Undefined metrics stay undefined.** Episode F1 returns `None` on a zero
  denominator; `require_defined_metric` turns that into a stop for human review,
  never a silent zero.
- **Physical exposure includes unavailable positions.** Time passed and state
  was carried. PRIMARY-only time is not physical exposure.

## 7. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or test waveform; inspect B4 test labels; calculate B4
  test metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- Never install, upgrade or downgrade packages (especially in `tactics`).
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- If a canonical run directory exists in ANY state, the attempt is consumed.
  `phase8-t2-development-v1/` holds both consumed T2 attempts.
- **No M2 rerun. No U1 rerun. No T2 rerun. No T1 fold retry.**
- Keep scratch files OUTSIDE the repo.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; it is NEVER a
  predictive feature.
- Labels must NEVER determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

## 8. `cardiosentinel-runs/T1/` is NOT T1 evidence

`cardiosentinel-runs/T1/T1_state_machine_v1/` exists locally (gitignored). It is
the **synthetic harness-verification scaffold** from PR #36:
`run_class: harness_verification`, `protocol_evidence: false`,
`evidence_class: harness_verification_only_not_scientific_evidence`,
`performance_claimed: false`. It sits **outside** the canonical namespace and
must never be cited as scientific evidence.

The canonical `cardiosentinel-runs/phase9-t1-development-v1/` does **not** exist.

## 9. Working preferences and hard-won lessons

- **A handoff's claim about PR state is a hypothesis, not a fact.** Always run
  `gh pr list --state open`, `git log --oneline -3`, `git status --porcelain`
  before assuming. This was wrong at the start of ECG 9 and again mid-session
  (a "merged" harness was still open).
- **Any digest computed from an interpreter's internal serialisation is not a
  file invariant.** CI runs Python 3.11; tactics runs 3.12. An `ast.dump` digest
  failed CI on identical bytes. Digest **bytes** (e.g. source minus COMMENT
  tokens via `tokenize`), never `ast.dump`, `repr`, `pickle` or set/dict order.
- **The frozen dependency digest only holds in `tactics`.** CI installs ~71
  packages with a different digest, so any test that claims a canonical run
  directory must `pytest.mark.skipif` on the observed digest. Cover the refusal
  with a separate test that runs everywhere.
- **Never delete a git worktree while a background test run is executing inside
  it.** That produced a mass error storm and a `runpy` traceback in ECG 9 that
  looked like a code failure and was not.
- **Launch long runs with Bash `run_in_background: true`**; foreground caps at
  10 min.
- Use `git commit -F <file>` with the message file in the scratchpad.
- **Never run `ruff format` over a whole directory** — format only changed files.
  CI runs `ruff check .` and `pytest -q`.
- **`gh pr create --body-file` WORKS.** Only `gh pr edit --body-file` fails; for
  edits use
  `gh api -X PATCH repos/DebalekhaChakraborty/CardioSentinel-AI/pulls/N -F body=@file`.
- **`gh pr checks` has no `--json`.** Use `gh pr view N --json statusCheckRollup`.
- **CI monitors must wait for ALL jobs** — exit only when none is
  `IN_PROGRESS`/`QUEUED`/`PENDING`. Two jobs; ~7–8 min.
- **Naive substring scans produce false positives.** `--force` and `--retry`
  match a *denylist*; "no uuid" in prose matches a determinism scan. Use AST
  scans and `build_parser()._actions`.
- **Test-suite counts:** 2095 → 2163 (+68 T1 protocol) → 2221 (+58 engine) →
  2238 (+75 spec, then 2239 after the proof fix) → 2312 (engine hardening) →
  **2388 passed, 1 skipped** on current master. Full run ~15m30s.
- Long reports end with the exact mandated closing block when one is specified.

## 10. Execution-integrity record (do not soften)

The 2026-08-12 shared-interpreter incident stands as recorded in the ECG 3
handoff: a concurrent session installed distributions into the then-shared
scientific interpreter while the canonical M1-v2 run was executing. Whether that
process loaded any added distribution **cannot be proven retrospectively**; all
read-only evidence is consistent with no effect. **M1-v2 remains the canonical
frozen M1 development evidence; do not rerun or modify it.**

The ECG 3 outer-repo index reconstruction also stands: that index was
**reconstructed, not recovered**, and is still worth a human glance.

M2 recovery2, the U1 canonical run, the T2 canonical TRAIN run and the T2
one-shot outer VALIDATION all ran clean against the frozen 335-package digest.

**No T1 execution of any kind has been performed and no canonical T1 run
directory exists.**

## 11. Open items carried into ECG 10

1. **The execution-enabling act.** `main()` refuses by design. Enabling it is a
   separate reviewable PR and a human decision. Re-run the eight-item checklist
   against the new master afterwards, because the SHA that gets authorized must
   name the code that actually runs.
2. **Stage-recorder granularity, documented not fixed.** The recorder forbids
   re-entry, so the nine fold stages are entered once for the whole 12-fold
   loop, not per fold. Run-level order is enforced by index; within a fold the
   authority object graph enforces it instead. If per-fold index enforcement is
   wanted, that is a design change.
3. **The ECG 3 outer-repo index reconstruction** still merits a human glance.
