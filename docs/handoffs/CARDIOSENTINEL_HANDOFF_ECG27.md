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
| Branch | `master` at `c737250`, **green**. **No open PRs.** |

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

**Reviewed and merged #143. That is all of it.** One PR in, one commit of my
own, no new work started.

**The judgement call #143 raised was right, and I kept it.** The qualification
receipt names no `environment_sha256`, recording `NOT YET SUBMITTED`, because
the task defined the authority mechanism but was scoped not to select an
environment. A receipt carrying a plausible digest is exactly what a later
reader — or a later piece of code — mistakes for authority. A real environment
gets a **V2 receipt**, never an edit to V1.

**The defect was somewhere else: the canonical serialization §3.1 freezes had a
digest collision.** Two different environments hashed identically and **both
reached `QUALIFIED`**:

```text
runtime_dependencies={"numpy": "2.3.2", "scipy": "1.0.0"}
runtime_dependencies={"numpy": "2.3.2,scipy=1.0.0"}
```

Both serialize to `runtime_dependencies=numpy=2.3.2,scipy=1.0.0` and share
`d87ecdb29ccdb87537436c9dddee599c2c0b6a809cbaaf6b8b5e3d4accc1802b`. It is the
failure the padded-value rule already names — *two records that differ silently
merging into one* — reached through the separator instead of the padding. A
`\n` in a scalar field value is the same defect one level up: it adds or
displaces a field line, so the record hashed is not the record described.

**Fixed at `5556e0c`, before merge, because that was the last free moment.** The
form freezes on merge and no environment has been built, so no digest anywhere
depended on it. Separators are now **refused as content, never escaped** —
`\n`/`\r` in any field value, `\n`/`\r`/`,`/`=` in any dependency name or
version. Escaping would close it too, but an escaping scheme is a second thing
two independent implementations must agree on byte for byte, and this form
exists so that they need not.

**No admissible record changed digest.** A well-formed record still hashes to
`d87ecdb2`; what changed is that inadmissible records are refused instead of
silently accepted.

**Two more holes on the same seam.** `reject_mutable_local_state` iterated
`ENVIRONMENT_RECORD_FIELDS` only, so a dependency pinned to
`file:///home/dev/cs.whl` qualified — §5.1 refuses home paths, but the one
mapping that reaches the digest was exempt. And `run_preflight` accepted any
object carrying an `environment_sha256` attribute; `verify_runtime_matches`
compares the runtime against *that object's own* record, so a duck-typed
stand-in declaring the digest the authorization names was checking itself
against itself. It now requires a `VerifiedEnvironmentAuthority`, asserted by
AST over `run_preflight` rather than by text scan.

**Two corrections to the qualification receipt.** Its table read
`tests/reproducibility — 75 passed`; that suite is **52**, and the 75 was
reproducibility plus the **23** of `tests/neural/test_b4b_sealed_test_identity.py`.
And its heading read `QUALIFIED — NOT AUTHORIZED`, borrowing a word that names a
state of a **record** in the ladder the package itself defines. No record has
reached it. It now reads **`MECHANISM QUALIFIED — NO ENVIRONMENT SUBMITTED`**.
That last is a wording call I made on my own — if a later session disagrees,
it is one line in the receipt and one row in `docs/journal-extension/j1/README.md`.

**Verification.** `tests/journal_extension` **112**, `tests/reproducibility`
**52**, `tests/neural/test_b4b_sealed_test_identity.py` **23**, and all three in
one interpreter — **187 passed**. `ruff check .` clean. 16 new regression tests.
Re-run on merged `master`, not only on the branch.

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

1. **No environment has been built or submitted.** The mechanism is qualified;
   nothing has passed through it. Building one needs a reproducible, immutably
   located artifact — a container image addressed by digest — and this machine
   cannot authoritatively produce one, which is the package's own point: a local
   machine may generate a candidate, it cannot promote itself. **This is the
   next real task and it is an infrastructure decision, not a coding one.**
2. **Then `J1_AUTHORIZATION_V1`** naming: frozen protocol digest, frozen
   pre-registration digest, execution Git SHA, environment authority digest,
   `V1_TRAIN_ONLY`, provenance sink, attempt budget, post-visibility decision
   authority, human approval. **Authorization is a human act — do not perform it
   autonomously.**
3. **J1 collaborators are qualification fixtures.** The real fold evaluator,
   calibration fitter and threshold deriver are unwritten.
4. **The provenance sink is an interface**; its value comes from the
   authorization. The **TRAIN manifest is supplied by** the authorization, never
   discovered by the instrument.
5. **The S3 mirror re-check is still owed and is now blocked.** ECG26 asked for
   a dated re-verification rather than inheriting 2026-08-31. I could not run
   it: `aws sts get-caller-identity` returns
   `Your session has expired. Please reauthenticate using 'aws login'.`
   **Reauthenticate first, then verify** — evidence bucket, Object Lock to 2027;
   drafts bucket, versioned, no lock; 994 files checked by path at the last
   count. Evidence retention expires **2027-08-22**, the first date those
   objects become movable.
6. **Three frozen records name the retired `docs/paper/` files in prose** —
   handoff ECG16 and two audits. Historical, not edited to follow a path.
   Expected, not drift.
7. **The symlink question is still open** (§0): rename the directory back, or a
   controlled reinstall. It went missing between ECG26 and this session, which
   is an argument for settling it.

---

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

**The characteristic failure of this session:** reviewing the question the
author raised instead of the code they wrote. #143 put one judgement call up for
decision, I agreed with it, and I very nearly merged on that agreement — the
forgeable digest was three lines away from the paragraph correctly explaining
why it must not be forgeable.
