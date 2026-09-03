# CardioSentinel — handoff to session "ECG 30"

Paste this whole file as the first message of the new chat, or say:
"Read `docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG29.md` in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do **not** use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/CardioSentinel` |
| Branch at handoff | `master` at `9044a21be88bde28ae5513feedcb853c7e1d6023`, clean |
| **Open PR** | **#157, `research/j1-builder-authorization-v2` at `56f79dd`, CI green, NOT MERGED** |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **Never `git add -A`.**

### The working directory drifts. Prefix every command.

`cd /home/AI_POC/tactics/CardioSentinel &&` in **every** command. ECG 28 warned
about this and it still caught me twice.

Once `gh pr checks 157` failed with *"none of the git remotes point to a known
GitHub host"*. Once `ruff check .` ran against the **outer monorepo** and
returned **5366 errors** from unrelated projects — exactly the failure ECG 28
described, in the same shape. **Anything over ~10 ruff errors in a clean tree
means you are in `/home/AI_POC`, not in CardioSentinel.**

A `cd` inside a compound command persists into the *next* Bash call. Both of my
drifts came immediately after a command that ended in a different directory.

### The symlink existed this session. Check anyway.

```bash
ls -ld /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
ln -sfn /home/AI_POC/tactics/CardioSentinel \
        /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
```

### Disk is tighter again

**2.2 GB free at 98%**, against ECG 28's 2.5 GB and ECG 27's 7.0 GB. The B4
neural path needs 2,147,483,648 free output bytes — you are now within ~50 MB of
that. **Clear pure cache before anything neural**: `~/.cache/pip`,
`~/.npm/_cacache`, `/tmp/pytest-of-*`. **Do not delete `~/.cache/hf-bench`
(13 GB)** or the 25 GB under `cardiosentinel-data/`, `-features/`, `-runs/`.

A `--depth 1` clone of this repo is **19 MB** — cheap, and see §4 for why you
want one.

Local suite on the PR branch is **810 passed** in ~45s:

```bash
pytest tests/neural/test_b4b_sealed_test_identity.py tests/journal_extension tests/reproducibility
```

**That command is a subset.** CI runs bare `pytest -q` — 4317 tests. The subset
passing tells you less than it looks like; see §4.

---

## 1. STATE

**J1 science is unchanged and still not authorized.** Everything below is about
the *build environment*.

```text
J1                           PRE-REGISTERED — NOT AUTHORIZED
builder authorization        WRITTEN AS 002, IN PR #157, NOT ON master
controlled-build runs        1        (33800630377, attempt 1, FAILED pre-claim)
qualification claims         0
Actions artifacts            0
BUILD_A / BUILD_B            NONE
environment artifact         ABSENT
environment authority record ABSENT
J1 attempt budget            NOT ESTABLISHED
scientific attempts used     0
```

### THE IMMEDIATE NEXT ACTION

**PR #157 is open, green and mergeable. It is a human-review decision, not a
task to execute.** Do not merge it on your own judgement — it records a human
authorization act, and merging is the moment the repository starts carrying a
live builder authorization.

Before any dispatch is even discussed, re-check the two volatile facts:

```text
controlled-build run history == 1  (still only 33800630377, attempt 1)
qualification claims         == 0
```

**Merging #157 authorizes a builder. It dispatches nothing.** The single
dispatch is a separate deliberate act under
`THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM`, and the owner has not
asked for it.

---

## 2. WHAT THIS SESSION DID

One PR opened: **#157**, two commits, not merged.

### `8871aed` — the authorization act

`J1-ENV-BUILDER-AUTH-002`, transcribed from V4 (`0658525e…`) as ECG 28
instructed. Nothing was copied on trust: the four retained-receipt digests were
recomputed, the five *tracked* build-configuration members were recomputed from
git's object store at `8c7a385d`, the seven-member configuration digest
recomputed to `c9e9b5a6…`, `provenance_destination` came out of
`durable_evidence_destination` and `builder_candidate_id` out of
`require_specific_builder_identity`. `authorization_timestamp` is
`2026-09-03T23:07:13Z`, captured at write time. 001's was not reused.

Plus `J1_BUILDER_AUTHORIZATION_ACT_V2.md`. ACT V1 is byte-unchanged.

### The thing ECG 28 did not know: seven tests asserted absence

**Writing the JSON broke seven tests.** Five sites encoded *"the repository
contains no builder authorization"*. They were written in #155/#156, **after**
001 was retired, which is why #154 never hit them — ECG 28 had no way to see it.

Grep found five. **Running the suite found two more**: the gate now exits `0`, so
`test_the_gate_refuses_and_the_refusal_is_its_own` and
`test_machine_sufficiency_is_still_not_authorization` failed on assertions grep
could not have located. **Do not size this kind of change by grep.**

All seven were rewritten to assert the new truth, not deleted. Fail-closed is
still proven against a tree carrying no authorization.

### `56f79dd` — see §4. It is the whole lesson.

---

## 3. THE TRAP I FELL INTO, AND WHAT THE REPOSITORY DID ABOUT IT

I wrote an assertion that the retired commit `1983616f` appears nowhere in the
002 document. **That is wrong**, and it would have passed review by looking
careful.

`1983616f` is still the legitimate **`workflow_review_commit`**. The workflow
bytes were reviewed there and have not changed since. Only
`authorized_source_commit` moved. Reviewing bytes is not building a tree.

```text
authorized_source_commit  MUST NOT be 1983616f
workflow_review_commit    IS 1983616f, correctly
```

The test now asserts both fields separately. **V4 §2 exists to prevent exactly
this confusion, and I made it anyway while implementing V4 §2.**

---

## 4. THE CHARACTERISTIC FAILURE OF THIS SESSION

# A green CI run is not evidence that your test ran.

The first CI run on #157 was **green**. It was misleading, and I nearly stopped
there.

```text
merged master   4173 passed, 141 skipped
PR #157 run 1   4173 passed, 142 skipped     <- +1 skip, and I had added +1 test
```

The gate admit-path test had moved from **passed to skipped**.
`_require_reviewed_commit_readable` skips when `workflow_review_commit` is absent
from the object store, and at `actions/checkout`'s default depth it is *always*
absent. The claim that the gate admits 002 ran **only in the 335-package
full-history local checkout**. CI reported a pass for a test it never executed.

ECG 28's lesson was *"a test that passes tells you about the environment it ran
in."* This is one layer beneath it: **a test that is reported as passing may not
have run at all**, and a summary line cannot tell you which.

**The only reliable tell is the skip count.** Diff it against the base branch on
every CI run. `4173 → 4173` with a new test added is not neutral, it is a
signal. Nothing in the CI output says "your new test skipped".

### My first fix was wrong, and the repository caught it

I set `fetch-depth: 0` on `ci.yml`. CI failed
`test_no_later_commit_touches_a_build_input`, which guards
`.github/workflows/` between `authorized_source_commit` and HEAD.

**The guard is right.** The Containerfile ends with
`COPY . /opt/cardiosentinel/src-tree` and `Containerfile.dockerignore` excludes
`.git`, bytecode, venvs and build residue — **but not `.github/`**. `ci.yml`
bytes are inside the build context.

I was one step from narrowing the guard to the declared
`BUILD_CONFIGURATION_MEMBERS` paths, which would have been reasonable-sounding
and wrong: **loosening a guard in the same change that trips it is the move the
guard exists to stop.** If you find yourself editing a check so your own commit
passes, stop and re-read what the check protects.

### `git revert` does not clear a pathspec guard

```text
git log <authorized_source_commit>..HEAD -- .github/workflows/
```

lists commits that **touched** those paths. A revert is another commit that
touches them, so the range was still dirty after reverting. I reset the branch
to the authorization commit and force-pushed. **A revert cannot undo a pathspec
guard violation — only dropping the commits can.**

### What actually proves the admit path

A tree the test builds: the real workflow bytes committed into a scratch
repository, so the reviewed commit exists **by construction** and no history of
this repository is needed. Plus a negative case — append one byte to the
checked-out workflow, reviewed commit untouched, and the admission must become
`current workflow differs`. Without the negative, the positive would pass for a
gate that checked nothing.

**Verified in a `--depth 1` clone, which is the shape CI checks out in:**

```text
before   87 passed, 1 skipped
after    89 passed, 1 skipped
```

```bash
git clone --depth 1 --branch <branch> file:///home/AI_POC/tactics/CardioSentinel /tmp/shallow
cd /tmp/shallow && PYTHONPATH=src pytest tests/journal_extension/... -q -rs
```

**19 MB, two seconds. Use it.** It is the cheapest way to find out whether a
check you just wrote will actually execute where it matters. Note the first time
I tried this I cloned *before committing*, so it ran the old file and told me
nothing — clone from a commit, not from an intention.

Final CI on `56f79dd`: **4175 passed, 142 skipped**. The counts reconcile
exactly — `4173 + 141 = 4314` on master, three tests added, one history-dependent
check in the skip column, `4175 + 142 = 4317`.

---

## 5. TRAPS (ECG 27's and ECG 28's still apply — these are new or sharpened)

1. **Diff the skip count, not just the pass count.** §4. This is the one.
2. **Do not size a change by grep.** Grep found five broken assertions; the
   suite found seven. The two it missed were behavioural.
3. **A revert does not clear a pathspec guard.** §4.
4. **Never loosen a guard to make your own commit pass.** §4.
5. **`.github/` is inside the build context.** `.dockerignore` does not exclude
   it and the Containerfile ends with `COPY .`. Treat any `.github/` edit as
   artifact-affecting until you have re-read the dockerignore.
6. **`workflow_review_commit` and `authorized_source_commit` are different
   fields with the same-looking value history.** §3.
7. **Clone from a commit, not from an intention.** A shallow clone made before
   you commit tests the old code and reports success.
8. **`ruff check .` in the wrong directory returns ~5366 errors.** That number
   is the tell, not a real regression.
9. Still true, all still cost time: **`gh pr checks` has no `--json`** (gh
   2.23.0); **`gh pr edit` fails silently** — use `gh api -X PATCH -F body=@file`;
   **`grep` is ugrep** and skips gitignored paths; **never `ruff format`**;
   **poll CI in one background waiter**, not chained sleeps.

---

## 6. WHAT IS OPEN

```text
PR #157 merged (human decision)   <- NEXT, and it is the owner's call
        v
ONE dispatch of the controlled workflow
        v
qualification claim (canonical, single-claim)
        v
BUILD_A + BUILD_B
        v
reproducibility record  ->  BIT_REPRODUCIBLE or DIVERGED
        v
durable evidence PR (human-reviewed, separate task)
        v
environment authority record
        v
J1_AUTHORIZATION_V1
        v
ONE J1 attempt
```

**Reproducibility is still falsifiable, not proven — nothing has been built
twice.**

### Two findings left open on purpose, both wanting an owner decision

- **The CI-skip tension.**
  `test_the_gate_admits_002_and_the_admission_is_its_own` still cannot run in CI
  without full history. Full history in CI means touching `.github/workflows/`,
  which trips the build-input guard and would require re-deriving 002 against a
  new source commit. The synthetic-tree tests close the gap for the *mechanism*;
  the **canonical document's** admission is still proven only where history
  exists. Either CI fetches full history and 002 is re-derived, or the guard is
  narrowed to the declared members. **Do not pick one unilaterally.**

- **`builder_authorization.main()` prints one headline for every exception**
  — *"controlled build refused: builder authorization absent"* — so a refusal
  caused by missing git history names an authorization that is present. ECG 28
  found it and left it; I left it too. One line in `main()`. **It alters gate
  output that receipts quote, so ask first.**

Carried from ECG 27, unchanged:

- **The S3 mirror re-check is still owed and still blocked.**
  `aws sts get-caller-identity` returns session expired. Object Lock retention
  expires 2027-08-22.
- **`tactics` is a witness, not an authority.** One `pip install` destroys the
  match with the frozen V1 environment.

---

## 7. THE SCIENCE IS UNCHANGED

All fifteen V1 one-shot budgets remain spent. **No physiological data,
annotation or reference-episode count was accessed at any point this session.**
No fold, calibrator, threshold, candidate selection or scientific result was
generated. No scientific attempt was claimed. No frozen artifact, attempt
receipt, threshold or experiment identity was touched.

Frozen and byte-unchanged, verified this session:

```text
J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1  cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0
J1_PRE_REGISTRATION_V1                  1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1
J1_FREEZE_RECEIPT_V1                    d116199affdc8488fefc765fee86efcd1aae23dee68b0bd302d4e055b08ee107
J1_AUTHORIZATION_CONTRACT_V1            9aae5a98475444bc8afa50779a4aaf59449a25ae7fbdb8024f4a0d6d8a048d80
```

Retained receipts, never re-pointed: V1/V2/V3/V4 review packets, authorization
act V1, the 001 failure receipt, Protocol V1, Protocol V2, the builder selection
receipt (whose `j1-environment-build.yml` typo stays, by design).

RQ4 **Supported (bounded)**. RQ3 a **negative finding**. RQ1, RQ2 (partial),
RQ5, RQ6, RQ7 open — every one needs a run.

---

**The characteristic failure of this session:** *reading a green CI run as
evidence that the test you just wrote had run.*

ECG 28's was "a test that passes tells you about the environment it ran in".
Mine is beneath it and quieter: the test did not run at all, and every number on
the screen said success. The pass count was **identical** to the base branch
while the branch had added a test — the only thing that gave it away was one
digit in the skip column.

It would have shipped. The apparatus caught the *next* mistake — the guard
refused my `ci.yml` fix — but nothing in this repository was ever going to catch
the first one, because a skipped test raises no error anywhere. **When ECG 30
adds a check, the question is not "does it pass" but "did it execute, in the
environment that matters" — and the only honest way to answer that is to run it
there.**
