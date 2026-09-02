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
| Branch | `master` at `675fd765`, **green**. **No open PRs.** |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **Never `git add -A`.**

### The working directory resets, and it is not a nuisance — it is dangerous

Put `cd /home/AI_POC/tactics/CardioSentinel &&` in **every** command. This bit
me twice in one session. Once it silently swallowed a heredoc. The second time
`git checkout -b` ran in **`/home/AI_POC`**, the outer repository, creating a
stray branch there; I only noticed because the next command reported the wrong
branch. `gh` also fails there with *"none of the git remotes point to a known
GitHub host"*, which is the cheapest tell that you have drifted.

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

### The J1 chain, and exactly where it stops

```text
frozen protocol            ✅   authorization contract        ✅
frozen pre-registration    ✅   approved runtime + dep lock   ✅
freeze receipt             ✅   build-authority mechanism     ✅
execution instrument       ✅   builder candidate + protocol  ✅
candidate evaluator        ✅   controlled-build workflow     ✅ inert
negative capability        ✅
environment-authority mech ✅
────────────────────────────────────────────────────────────────
builder human-authorized   ❌ ← THE NEXT STEP, AND IT IS A HUMAN ACT
environment artifact       ❌
environment authorized     ❌
J1 authorization           ❌
J1 execution               ❌
```

**All seven collaborators are real**; `require_execution_capability` passes over
the whole graph. **Capability is not permission** — preflight still refuses with
`authorization absent`, and the same is true one layer down for the builder.

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

### #147 — the approved runtime, and a lock that already existed

The runtime question turned out not to be a choice. All three V1 experiment
locks record the environment the inherited scaffold was **built in**:
`python_version 3.12.6`, 335 packages, `environment_dependency_digest
b0fd6eaa…`. J1 estimates a conditional contrast *given* that scaffold, so the
approved runtime is a fact read out of frozen evidence.

**CI is not the scientific interpreter and never was** — Python 3.11 from
unpinned ranges. Right for proving code correct, wrong for producing evidence.

I first reported "there is no dependency lock." **That was wrong: I searched for
a lockfile by filename.** The lock exists inside the frozen experiment locks,
PEP 503 normalised, with its digest compiled into V1's source as
`FROZEN_DEPENDENCY_DIGEST` and enforced by `require_exact_scientific_environment`
— whose refusal ends *"Do not change packages to satisfy this check."*

### #148 — what makes an artifact authoritative

Not that it exists, that Docker built it, or that its digest was written down.
`build_authority.py` freezes the manifest schema, the builder ladder and the
reproducibility contract. **A tag is not authority — and neither is
`registry/name@sha256:…`**, which carries a *location*; identity is the digest,
because two mirrors share one identity.

### #149 — builder candidate and the frozen build protocol

GitHub Actions, `CANDIDATE`. Target platform traced from evidence: all three
locks record `device=cpu`, `cuda_version=None`, `torch==2.13.0+cpu` — a CPU-only
wheel that cannot use CUDA, so a GPU target would change the dependency digest.

**Dependency reconstruction turned up a finding.** The 335-package set does not
come from one index: 332 PyPI, **2 from `download.pytorch.org/whl/cpu`**
(`torch`/`torchvision` `+cpu` are HTTP 404 on PyPI), and **1 first-party**
(`cardiosentinel==0.1.0`, which no index resolves — the *source commit* pins it,
not the version string). A build pointed only at PyPI fails on two and silently
mis-resolves a third.

### #150 — the inert controlled-build workflow, and two corrections to it

`.github/workflows/j1-environment-artifact-build.yml` exists so a human
authorization can name a real object. `workflow_dispatch` only, **no inputs at
all**, gate first, every artifact job behind it. Verified against the provider:
after merge GitHub registered it and it has **zero runs**.

**Review caught a defect I had shipped: the identity rule was unsatisfiable.**
It required `github.sha == authorization.workflow_commit`. The authorization
lives in the repository, so the commit that adds it *is* the commit the workflow
runs at — the document would have had to contain the SHA of the commit
containing itself. It could never have been written.

Fixed by naming the reviewed **bytes**: `workflow_path`,
`workflow_review_commit`, `workflow_sha256` over raw committed bytes. The
authorization may live in a **later** commit; one differing byte refuses. Both
digests are recomputed — one from the working tree, one from git's object store
— and the two failures are separate exception types.

Also pinned what pinning the action does not pin: **Buildx `v0.36.1`** (settled
decision, not recency) and the **BuildKit `linux/amd64` image manifest**
`sha256:040d3412…`, resolved by addressing the index by its own digest,
re-hashing it to itself, finding exactly one non-attestation `linux/amd64`
descriptor, and comparing that descriptor against an independent SHA-256 over
2261 fetched bytes.

### Verification at the end of the session

`tests/reproducibility` **52**, `tests/journal_extension` **559**,
`tests/neural/test_b4b_sealed_test_identity.py` **23**, all three in one
interpreter — **634 passed**. `ruff check .` clean.

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
5. **A gitignored path swallows work silently.** `build/` is ignored as a
   Python packaging convention. I wrote the container build files there; they
   existed on disk, every local test passed, and **not one would have reached
   the repository**. They live in `containers/j1-environment/` now, and a test
   runs `git check-ignore` and `git ls-files` over every build input. Check
   `git status` actually lists what you wrote.
6. **PyYAML parses a bare `on:` key as the boolean `True`.** A workflow test
   that looks up the string `"on"` finds nothing and passes while the workflow
   triggers on every push. Resolve the key explicitly.
7. **Do not write a digest you have not resolved.** I typed an
   `actions/download-artifact` SHA into the workflow from memory before
   checking it. It happened to be right. That is luck, not process, and it is
   the exact failure this programme exists to prevent.
8. **`git commit` sweeps the whole index.** Stage explicit paths, or
   `git add -u <path>`.
9. **`grep` is ugrep here** and skips gitignored paths. Use `git grep` /
   `git ls-files` for anything authoritative.
10. **`gh pr checks` has no `--json`** (gh 2.23.0). Read failures with
   `gh api repos/.../actions/jobs/<id>/logs`.
11. **`gh pr edit` fails silently** on a body change. Use
   `gh api -X PATCH repos/.../pulls/<n> -f body=...`.
12. **Never `ruff format`.** `ruff check` only. `scripts/provenance` is in
   `extend-exclude`, so its 116 pre-existing errors are out of scope.
13. **Poll CI in a background waiter**, never one long blocking wait.
14. **The shared working tree is one checkout.** A peer session in
    `/home/AI_POC/tactics/CardioSentinel` sees your `git checkout`. Run
    `ListAgents` and `git worktree list` before claiming a handoff task, and say
    so before you switch branches.

---

## 5. WHAT IS OPEN

```text
builder human authorization   ← next, and it is a human act
        v
two controlled artifact builds
        v
environment authority record
        v
J1_AUTHORIZATION_V1
        v
ONE J1 attempt
```

1. **The next step is a human builder authorization, and you must not write
   it.** It would live at `docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_V1.json`
   and needs 21 fields with no placeholders. **These four are already
   determined, recomputed on merged master and handed over as evidence, not as
   an authorization:**

   ```text
   workflow_path           .github/workflows/j1-environment-artifact-build.yml
   workflow_review_commit  675fd7656b333bdf950a63222ecba214d1c4d8b1
   workflow_sha256         32ffdfc28bf8f3044f069190b1f0b15617733487de985f3e0e477ce7af02ec6d
   runner_class            ubuntu-24.04
   ```

   The digest was taken from git's object store over raw committed bytes and
   cross-checked against the working tree. Verify it yourself before signing —
   that is the whole point of the recomputation rule.

2. **Then two controlled builds**, under the frozen protocol. On divergence the
   procedure **stops**: neither digest promoted, no rebuild until they agree, no
   automatic reclassification to `NOT_REPRODUCIBLE_DOCUMENTED`. Reproducibility
   is falsifiable here, not proven — nothing has been built twice.

3. **Then the environment authority record.** Four of its twelve fields are
   already determined by frozen evidence (`approved_runtime_fields()`); the
   other eight need the artifact.

4. **Then `J1_AUTHORIZATION_V1`**, populating the contract merged in #145.
   **Authorization is a human act — do not perform it autonomously.**

5. **The S3 mirror re-check is still owed and still blocked.**
   `aws sts get-caller-identity` returns session expired. Evidence bucket has
   Object Lock to 2027; retention expires **2027-08-22**.

6. **The residual trust has not moved and is the real content of the builder
   authorization.** GitHub controls the runner image, the hardware and the code
   behind those pinned SHAs. **Pinning by SHA constrains what code runs, not
   what executes it.** Accept it knowingly or not at all.

7. **`tactics` is a witness, not an authority.** It currently matches the frozen
   V1 environment exactly. One `pip install` destroys that match. Its failure
   would remove a convenient check, not rewrite the frozen authority.

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

It happened repeatedly, and the shape never changed. In #143 the specification
said padded values are refused *because stripping would merge two records that
differ*, and the separators — the same failure, one door over — were unguarded.
In #145 I wrote that `protocol_sha256` "must equal the frozen protocol digest"
and implemented "looks like 64 hex", **and my own fixture declared `"a"*64`**,
so 112 passing tests certified a check the document did not describe. In #146's
receipt I called two collaborators real when no object exposed the method the
gate calls. In #150 I shipped an identity rule that could never be satisfied by
any document anyone could write, and review caught it, not me.

Every one of those passed its tests. **A green suite is evidence about the
fixtures**, and the fixture and the code were written by the same hand, in the
same hour, from the same misunderstanding. The habit that actually caught things
was different: bind a check to something the fixture cannot supply — a digest
recomputed from git, a package list read from frozen evidence, a query to a
registry, `git check-ignore`. When ECG 28 writes a guarantee, ask what external
fact would falsify it, and check *that*.
