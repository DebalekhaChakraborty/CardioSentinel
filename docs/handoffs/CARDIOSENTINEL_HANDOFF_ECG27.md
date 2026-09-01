# CardioSentinel — handoff to session "ECG 28"

Paste this whole file as the first message of the new chat, or say:
"Read `docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG27.md` in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do **not** use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/CardioSentinel` |
| Branch | `master` at `8b91408`, **green**. **No open PRs.** |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **The Bash working directory silently resets** — put
`cd` in the same command as the work. **Never `git add -A`.**

### The symlink was gone. Recreate it before running anything.

ECG26 said it existed. It did not. Without it nine governance tests fail as
`DID NOT RAISE` and look like disabled safety guards. **Check, do not assume:**

```bash
ln -sfn /home/AI_POC/tactics/CardioSentinel \
        /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
```

It is untracked infrastructure and nothing recreates it. Expect it to be missing
again; `ls -ld` it first.

### The disk trap ECG26 named is resolved. Do not inherit it.

ECG26 §0 warned that ~32 `tests/neural` tests fail locally with
`B4 run requires 2147483648 free output bytes, but only 1264009216 are
available`, and told you not to chase it. **That is stale.** ECG26's own session
then cleared ~5.8 GB of pure cache (`~/.cache/pip`, `~/.npm/_cacache`,
`/tmp/pytest-of-*`) and confirmed 113 passes where 32 had failed. This session
measured **7.0 GB free at 93%**. Full local suites are usable — run them.

**Do not delete `~/.cache/hf-bench` (13 GB)** to find more space. It holds the
pinned Qwen revisions `70d244cc` and `cdbee75f` that the demo-UI
`--with-local-models` path uses under `HF_HUB_OFFLINE=1`; deleting it makes the
guarded-generation evidence in `QWEN_EVALUATION_RUN.md` unreproducible on this
machine. Same for the 25 GB under `cardiosentinel-data/`, `-features/` and
`-runs/`: mirrored to S3, but live scientific data, and an owner decision.

---

## 1. STATE — V1 frozen, V2 running, J1 pre-registered

**V1 is complete.** All fifteen one-shot budgets are spent; the B4 neural sealed
test was consumed 2026-08-25, attempt 1 of 1. Nothing in this session
recomputed, re-scored or re-selected anything.

**J1 is `PRE-REGISTERED — NOT AUTHORIZED`.**

```text
QUESTION           complete
PROTOCOL           FROZEN   cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0
PRE-REGISTRATION   FROZEN   1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1
AUTHORIZATION      ABSENT
EXECUTION          NOT PERMITTED
REPORT / DECISION  nonexistent
```

`real_data_authority = NONE` · `attempt_budget = NOT ESTABLISHED` · zero
authorization documents · zero attempt directories. **Both digests re-checked
against `J1_FREEZE_RECEIPT_V1.md` this session and unchanged**, rather than
copied forward from ECG26.

Bound by `docs/journal-extension/j1/J1_FREEZE_RECEIPT_V1.md` and guarded by
`tests/reproducibility/test_j1_freeze_binding.py`, which fails if either
document drifts.

---

## 2. WHAT THIS SESSION DID

**Four PRs merged: #143, #144, #145, #146.** The session began expecting to
review one PR and ended with the execution apparatus complete.

### #143 — environment authority (reviewed, fixed, merged)

The judgement call it raised was right and I kept it: the qualification receipt
names no `environment_sha256`. **The defect was elsewhere — the canonical
serialization §3.1 freezes had a digest collision.** Two different environments
hashed identically and both reached `QUALIFIED`:

```text
runtime_dependencies={"numpy": "2.3.2", "scipy": "1.0.0"}
runtime_dependencies={"numpy": "2.3.2,scipy=1.0.0"}
```

Both serialize to `runtime_dependencies=numpy=2.3.2,scipy=1.0.0`. Separators are
now refused as content, never escaped. `reject_mutable_local_state` also skipped
`runtime_dependencies`, and preflight accepted any object carrying an
`environment_sha256` attribute — `verify_runtime_matches` compares against that
object's *own* record, so a duck-typed stand-in verified itself.

### #144 — three collaborators promoted from fixture

`calibration.py`, `thresholds.py`, `selection.py`. The doctrine this settled:
**three frozen sections say J1 "preserves" a V1 rule whose function is a
forbidden entry point.** Read together, the constraints admit exactly one
implementation — the same arithmetic, computed inside J1, pinned by test to the
inherited version. The U1 Platt fit is the exception: not forbidden, so it is
called, not copied.

The trap it found: **J1's registry enumerates profiles `("FAST","MED","SLOW")`
and V1's frozen tie-break is `T1_PERSISTENCE_PROFILES`, most cautious first.
They are exact opposites, both accept `.index()`, and §6.5 names V1's.**

### #145 — the authorization contract

`ABSENT → DRAFT → AUTHORIZED`, no transition function to `AUTHORIZED`.
`attempt_budget = 0` is a valid *contract* value and an invalid *execution*
value, deliberately: zero and absent are different states.

**Review of my own PR found two governance defects.** The contract said
`protocol_sha256` "must equal the frozen protocol digest" and the code checked
only shape — a contract declaring `"a"*64` was accepted, **and my own fixture
used exactly that**, so 112 tests proved a check that was not the one the
document described. It now recomputes both digests from disk and refuses a
mismatch. Second, the AST proof covered attribute reads, but
`AuthorizationState("AUTHORIZED")` constructs the member from a *value*; the
contract object now refuses any state but `DRAFT`.

### #146 — the candidate evaluator, and the last fixture closed

The §2.1 state machine is re-stated (because `next_state` is forbidden) and
pinned to the inherited implementation across **3,000+ comparisons**.
`group_reference_episodes` and `match_runs_to_episodes` are *imported*: the
forbidden four are all operating-point functions, and those two are measurement
conventions over reference truth that §7.1.1 preserves unchanged.

**The reading that would have changed the science.** §2.1 gives EVENT evidence
as `d_t AND p_t ≥ p_event AND s_t ≥ s_event`. The retained implementation
**relaxes the S4D term before `T1_COLD_START_SECONDS`**, and §2.1 also says the
retained semantics are not modified. §2.1's line is the *mature-stream* form.
Implementing the prose literally builds a fair comparator against a subtly
different stateful arm — a different question, with nothing looking wrong. Both
branches are pinned by test. **This is the one judgement in the apparatus that
no test can catch, because both readings pass a self-consistent suite.**

It also corrected my own receipt: `fold_allocator` and `bootstrap` were listed
as real and were **not gate-shaped** — module functions with no `allocate` or
`resample` and no attestation, so `require_execution_capability` could never
have passed. Thin adapters now exist and **the whole seven-collaborator graph is
provable end to end** for the first time.

**Capability is not permission.** The gate reads no data and consults no
authorization; preflight still refuses with `authorization absent`.

### Verification at the end of the session

`tests/reproducibility` **52**, `tests/journal_extension` **306**,
`tests/neural/test_b4b_sealed_test_identity.py` **23**, all three in one
interpreter — **381 passed**. `ruff check .` clean.

---

## 3. J1 — the frozen science. Do not re-derive it.

| | |
|---|---|
| Question | does stateful episode reasoning retain an advantage against an **independently tuned** memoryless comparator |
| Population | 56 V1 TRAIN subjects |
| Primary F1 cohort | `reference_episode_count > 0` — reference-defined, identical for both arms |
| Arm-neutral row | **8 fields**. `elapsed_state_seconds` is J1-S-endogenous and is *not* in it |
| Inherited scaffold | B4 / P1 / M1 / M2 / T2, frozen |
| Cross-fit upstream | **U1 calibration only** |
| Geometry | outer 7 × 8, inner 6 × 8 over 48; seed 2026 |
| J1-S | **12** candidates, `NO EXPANSION` |
| J1-W | **206** candidates |
| Primary contrast | `Δ = mean(F1_S,i − F1_W,i)` |
| Interval | percentile paired subject bootstrap, 1000 replicates, seed 2026, 2.5 / 97.5 |
| Gate A | PASS = `Δ > 0` **and** 95% lower bound `> 0` |

**Two facts that shaped the design and are easy to lose.** T1/W1 were developed
on the **12 VALIDATION** subjects, which J1 may not reopen — hence TRAIN, with
**zero overlap**. And **B4 was trained on all 56 TRAIN subjects** (verified from
its experiment lock), so J1 estimates a *conditional* episode-policy contrast
given the inherited scaffold; it is **not** a fully out-of-sample evaluation,
and absolute values are development evidence only.

---

## 4. TRAPS

1. **A well-argued specification is not an implemented one.** #143's prose,
   commit message and PR body all state the rule that padded values are refused
   *because stripping would merge two records that differ*. The identical
   argument applies to the separators, the code did not make it, 34 tests
   passed, and the digest was forgeable. **Read the serialization function
   against the invariant, not the paragraph describing it.**
2. **Review the code, not the question the author raised.** #143 asked for a
   judgement on one point and was right about it. The defect was in the part
   nobody flagged. An author's named uncertainty is where they already looked.
3. **Verify on a clean checkout, not a subset.** This cost ECG26 twice.
   `docs/paper/` was *gitignored, not deleted*, so tests reading it from disk
   passed locally and failed CI — master was red for 18 hours. Then a J1 test
   asserted `b4b_sealed_test not in sys.modules`, true in isolation and false in
   the full suite. Reproduce CI cheaply:
   `pytest tests/neural/test_b4b_sealed_test_identity.py tests/journal_extension tests/reproducibility`
4. **A string search is not a dependency analysis.** Prove by **AST and import
   graph, never source text** — a guard's own refusal list contains the words it
   refuses. V1 recorded that false positive five times.
5. **`git commit` sweeps the whole index.** Stage explicit paths, or
   `git add -u <path>`.
6. **`grep` is ugrep here** and skips gitignored paths. Use `git grep` /
   `git ls-files` for anything authoritative.
7. **`gh pr checks` has no `--json`** (gh 2.23.0). Read failures with
   `gh api repos/.../actions/jobs/<id>/logs`.
8. **`gh pr edit` fails silently** on a body change. Use
   `gh api -X PATCH repos/.../pulls/<n> -f body=...`.
9. **Never `ruff format`.** `ruff check` only. `scripts/provenance` is in
   `extend-exclude`, so its 116 pre-existing errors are out of scope.
10. **Poll CI in a background waiter**, never one long blocking wait.
11. **The shared working tree is one checkout.** A peer session in
    `/home/AI_POC/tactics/CardioSentinel` sees your `git checkout`. Run
    `ListAgents` and `git worktree list` before claiming a handoff task, and say
    so before you switch branches.

---

## 5. WHAT IS OPEN

The agreed order, and it is an order, not a menu:

```text
candidate evaluator  ✅ done (#146)
        v
qualified environment record   <- BLOCKED, and blocked outside this machine
        v
authorization document
        v
human signs
        v
ONE J1 attempt
```

1. **No environment has been built or submitted, and this machine cannot do
   it.** That is the package's own thesis: a local machine may generate a
   candidate, it cannot promote itself. A real record needs a reproducibly
   built, **digest-addressed artifact that exists outside this box** — a
   container image in a registry. `verify_authority_record` takes
   `artifact_exists` as an injected callable precisely because checking it
   means reaching a registry. **Producing that artifact, or authorizing its
   construction, is an owner decision.** The mechanism is qualified; nothing has
   passed through it.
2. **Then `J1_AUTHORIZATION_V1`**, populating the contract merged in #145.
   **Authorization is a human act — do not perform it autonomously.**
3. **The provenance sink value comes from the authorization**, and the **TRAIN
   manifest is supplied by it**, never discovered by the instrument.
4. **The S3 mirror re-check is still owed and still blocked.**
   `aws sts get-caller-identity` returns `Your session has expired. Please
   reauthenticate using 'aws login'.` Evidence bucket, Object Lock to 2027;
   drafts bucket, versioned, no lock; 994 files at the last count. Retention
   expires **2027-08-22**.
5. **Three frozen records name the retired `docs/paper/` files in prose** —
   ECG16 and two audits. Historical, not drift.
6. **The symlink question is still open** (§0). It went missing between ECG26
   and this session, which argues for settling it.

## 6. THE SCIENCE IS UNCHANGED

**All fifteen V1 one-shot budgets remain spent.** No frozen artifact, attempt
receipt, threshold or experiment identity was touched this session. No
physiological data, annotation or reference-episode count was accessed. No fold,
calibrator, threshold, candidate selection or scientific result was generated.
No scientific attempt was claimed. The ledger still reads `PRE-REGISTERED` with
authority `NONE`.

RQ4 **Supported (bounded)** — the parenthesis is part of the claim. RQ3 is a
**negative finding** reported as a result. RQ1, RQ2 (partial), RQ5, RQ6 and RQ7
are open, and every one needs a run.

---

**The characteristic failure of this session:** writing the guarantee in prose
and the weaker check in code — then building the fixture to the prose, so the
suite went green over the gap.

It happened three times. In #143 the specification said padded values are
refused *because stripping would merge two records that differ*, and the
separators — the same failure, one door over — were unguarded. In #145 I wrote
that `protocol_sha256` "must equal the frozen protocol digest" and implemented
"looks like 64 hex", **and my own fixture declared `"a"*64`**, so 112 passing
tests certified a check the document did not describe. In #146's receipt I
listed two collaborators as real when no object exposed the method the gate
calls.

The first was someone else's and I caught it reviewing. The second and third
were mine and I caught them only because a later step forced me to actually run
the thing. **A green suite is evidence about the fixtures, not about the
claim** — the fixture and the code were written by the same hand, in the same
hour, from the same misunderstanding. Bind a check to an external fact the
fixture cannot supply, or it proves nothing.
