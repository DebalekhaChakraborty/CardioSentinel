# CardioSentinel — handoff to session "ECG 31"

Paste this whole file as the first message of the new chat, or say:
"Read `docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG30.md` in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do **not** use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/CardioSentinel` |
| Branch at handoff | `master` at `fd16ae5bd03f807c8a02b335a3adf0f486f683aa`, clean |
| **Open PR** | **the apparatus remediation, `research/j1-build-apparatus-remediation-v3`, NOT MERGED** |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **Never `git add -A`.**

### The working directory drifts. Prefix every command.

`cd /home/AI_POC/tactics/CardioSentinel &&` in **every** command. It caught me
twice again this session, both times immediately after a command that ended in a
different directory — a `cd` inside a compound command persists into the *next*
Bash call.

The two tells, both seen this session: `gh` failing with *"none of the git
remotes point to a known GitHub host"*, and `ruff check .` returning **5366
errors** from the outer monorepo. Anything over ~10 ruff errors in a clean tree
means you are in `/home/AI_POC`.

### The symlink existed this session. Check anyway.

```bash
ls -ld /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
ln -sfn /home/AI_POC/tactics/CardioSentinel \
        /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
```

### Disk

**~2.2 GB free at 98%.** The B4 neural path needs 2,147,483,648 free output
bytes, so you are within tens of megabytes of the failure ECG 26 chased. Clear
pure cache only — `~/.cache/pip`, `~/.npm/_cacache`, `/tmp/pytest-of-*`. **Do not
delete `~/.cache/hf-bench` (13 GB)** or the 25 GB under `cardiosentinel-data/`,
`-features/`, `-runs/`.

A `--depth 1` clone of this repo is ~19 MB. Use one; see §5.

---

## 1. STATE

**J1 science is unchanged and still not authorized.** Everything below is the
build environment.

```text
J1                           PRE-REGISTERED — NOT AUTHORIZED
active builder authorization ABSENT
authorization 001            RETIRED, NOT SPENT   (PRE_ARTIFACT_INFRASTRUCTURE)
authorization 002            SPENT, RETIRED       (POST_CLAIM_PRE_ARTIFACT)
authorization 003            DOES NOT EXIST
controlled-build runs        2   (33800630377 attempt 1; 33902875021 attempt 1)
qualification claims         1   (canonical, under 002, preserved in-repo)
Actions artifacts            1   (that claim; nothing else)
BUILD_A / BUILD_B            NEVER PRODUCED AN ARTIFACT
environment artifact         ABSENT
environment authority record ABSENT
J1 attempt budget            NOT ESTABLISHED
scientific attempts used     0
```

### THE IMMEDIATE NEXT ACTION

**The apparatus remediation PR is open and unmerged.** It is a human-review
decision. After it merges, the next act is a **V5 review packet re-derived
against the merged remediation commit** — and then, separately and only by human
decision, **authorization 003**.

# NOTHING IS AUTHORIZED. THE REMEDIATION IS NOT AN AUTHORIZATION.

Merging the repair does not authorize a builder, does not create 003, and does
not permit a dispatch. A third controlled-build run requires all three of: human
review of the remediated object, a **new** `builder_authorization_id`, and a new
qualification lineage. `require_retry_permitted` enforces this and will refuse.

---

## 2. WHAT HAPPENED SINCE ECG 29

ECG 29 ended holding on PR #157. Four things have happened since, and the middle
two are the ones that matter.

### #157 merged — authorization 002 became active

Merged at `8e3f9023ac173bacc5731b476007cad056bf6100`.

### Controlled run `33902875021` — dispatched exactly once

```text
dispatched  2026-09-04T17:52:26Z, one command, never re-issued
run_number  2      run_attempt  1
head_sha    8e3f9023ac173bacc5731b476007cad056bf6100

Builder authorization gate   SUCCESS   <- the first gate that ever admitted
Build capability             SUCCESS
Qualification claim          SUCCESS   <- 17:52:46Z. 002 IS SPENT FROM HERE
BUILD_A                      FAILURE
BUILD_B                      FAILURE
Reproducibility gate         SKIPPED
```

**The claim was recorded, so 002 is spent — not retryable, not resumable.**

### Both builds failed before producing an artifact

Identical error, identical step, in both:

```text
--require-hashes option does not take a value
```

`Containerfile:38` passed `--require-hashes=false`. **`--require-hashes` is a
boolean flag**; pip exits 2 during argument parsing before installing anything.
Deterministic on every runner, every time.

```text
failure_class                  = POST_CLAIM_PRE_ARTIFACT
reproducibility_classification = NONE
```

**Not `DIVERGED`.** No OCI manifest was produced on either side, so there were
never two things to compare. Labelling it `DIVERGED` would send a future reader
to investigate a comparison that never happened. **Not
`PRE_ARTIFACT_INFRASTRUCTURE` either** — that is 001, which recorded no claim,
and the difference between the two is the entire question of whether an
authorization can be used again.

### #158 — preserved the claim, retired 002

The provider's claim bytes, byte-identical, at
`docs/journal-extension/j1/evidence/environment-build/J1-ENV-BUILDER-AUTH-002/j1-qualification-claim.json`
(`75716bd8…`). No BUILD_A record, no BUILD_B record, no OCI archive, no
reproducibility record — **none of those ever existed**, and a placeholder would
turn an honest absence into a false record. The canonical authorization file was
removed; `ACT_V2` and `V4` are byte-unchanged and pinned.

### This PR — the apparatus repair

One line:

```diff
-RUN python -m pip install --no-deps --require-hashes=false \
+RUN python -m pip install --no-deps \
```

```text
containerfile              44b755cb…  ->  a6c914b0…   CHANGED
six other members                          unchanged
build_configuration_digest c9e9b5a6…  ->  54f40d31…   CHANGED
dependency_digest          b0fd6eaa…      unchanged
workflow sha256            6bf187e2…      unchanged
```

Hash checking was **omitted**, not disabled a second way. `--no-require-hashes`
does not exist, and adding `--require-hashes` would demand a hash for every pin —
a different guarantee than the frozen mapping currently provides, and not
something to change while repairing a syntax defect.

---

## 3. WHY THIS DEFECT SURVIVED EVERY REVIEW

# No build had ever executed that layer.

Run `33800630377` died in its authorization gate on a `numpy` import, so the
`RUN` instruction had **never once been reached**. Every check that existed
proved things *about* the Containerfile — its SHA-256, its membership in the
build configuration, its presence at the authorized source commit, its `COPY`
lines, its base image pin — and not one of them proved that the command inside
it was a command pip would accept.

The apparatus was reviewed exhaustively. The apparatus was never run.

This PR adds the missing boundary: `tests/journal_extension/test_j1_containerfile_pip_invocation.py`
invokes `python -m pip install` as a subprocess against an **empty** requirements
file with `--no-index`, so pip parses arguments and then has nothing to do. It
includes a **regression case** proving `--require-hashes=false` still exits
non-zero with the historical message — a guard that only confirms the current
file is fine cannot tell you whether it would have caught the defect.

**The commands are derived from the committed Containerfile bytes**, never
retyped: a hand-written copy would drift from the file it guards and then pass
while the real build failed. The extraction **fails closed** — an option in
neither the known-boolean nor the known-value-taking table raises, because
silently treating an unknown option as boolean would drop the token after it and
test a command nobody wrote.

### The first version of that guard was itself wrong, and review caught it

# Options are preserved. Only values are replaced.

The sanitizer originally did `index += 2` on every value-taking option, dropping
the option **together with** its value — `--index-url https://pypi.org/simple`
and `-r requirements.pypi.txt` disappeared before pip saw the command.

That erased the grammar under test. A malformed `--index-url` would have
vanished instead of being rejected, and the "derived from the committed bytes"
check was **circular**: it compared against the options that survived the
sanitizer, so an option the sanitizer dropped was also absent from the set it
checked.

Now a requirement path becomes a controlled empty file and an index location
becomes the `file://` URI of an empty directory, while every option survives.
Structure is validated rather than assumed: a value-taking option at the end of
a command, or one followed by another option, raises **before** pip is invoked —
so `--index-url -r requirements.txt` cannot swallow `-r` as a URL and report
success for a command nobody wrote. Sanitization is defined per option; a
recognised value-taking option with no explicitly safe test value raises rather
than falling back to a guess.

The test that keeps this honest is
`test_the_sanitizer_preserves_the_historical_defect`: the *historical* broken
command is passed through the same sanitizer and pip must still reject it. **A
sanitizer that erases grammar returns a valid command there, and the guard is
worthless.**

**The lesson generalises: a harness that "cleans up" its input can clean away the
defect it exists to find.** Whenever a test transforms what it tests, prove the
transformation still fails on a known-bad input.

---

## 4. THE TRAP THAT ALMOST CAUGHT ME

Two packet tests failed after the one-line repair — correctly. They recomputed
the build-configuration members from the **working tree** and compared them
against **V4**, which describes the object 002 authorized.

The tempting fix is to update V4's numbers. **That would erase the record of
what was actually authorized and built.** V4 is frozen; the tree moved.

They were split instead:

- a **live** check, which never skips, asserting the tree has moved away from V4
  and that *only* `containerfile` moved — a second member drifting there would
  mean this was not the single-defect repair it claims to be;
- a **historical** check, recomputing V4's members from git at the commit V4
  named, guarded by `_require_commit`;
- an **internal-consistency** check needing neither tree nor history: the
  packet's own recorded members must recombine to the packet's own recorded
  configuration digest.

---

## 5. TRAPS (ECG 27–29 still apply — these are new or sharpened)

1. **A test proving things *about* a file is not a test that the file works.**
   This session's whole lesson. Digests, membership, presence at a commit — all
   passed, for a command pip would reject.
2. **A guard must be shown to fail on the real defect.** Add the historical
   broken form as a regression case, or you have only proved that today is fine.
3. **Derive from committed bytes; never keep a second copy of a command.**
   Two truths drift, and the copy is the one that passes.
4. **Probe optional tooling rather than assuming it.** `pip --dry-run` arrived in
   pip 22.2 and CI resolves its own pip; passing an unsupported option would
   fail the corrected command for a reason unrelated to the Containerfile. Probe
   is not the same as skip — the test still runs.
5. **Diff the skip count against the base branch on every CI run** (ECG 29).
   Baseline for this PR is merged master `fd16ae5b`: **4198 passed, 141 skipped**.
6. **When the tree legitimately diverges from a frozen packet, split the test;
   do not update the packet.** §4.
7. **`git revert` does not clear a pathspec guard** (ECG 29) — only dropping the
   commits does.
8. **`.github/` is inside the build context**: no `.dockerignore` entry, and the
   Containerfile ends with `COPY .`.
9. Still true: **`gh pr checks` has no `--json`** (gh 2.23.0); **`gh pr edit`
   fails silently** — use `gh api -X PATCH -F body=@file`; **`grep` is ugrep**
   and skips gitignored paths; **never `ruff format`**; **poll CI in one
   background waiter**.

---

## 6. WHAT IS OPEN

```text
apparatus remediation PR merged (human decision)   <- NEXT
        v
V5 review packet, re-derived against the MERGED REMEDIATION COMMIT
        v
human authorization 003        (never 001, never 002)
        v
ONE dispatch of the controlled workflow
        v
qualification claim -> BUILD_A + BUILD_B -> reproducibility record
        v
durable evidence PR -> environment authority record
        v
J1_AUTHORIZATION_V1 -> ONE J1 attempt
```

# SOURCE IDENTITY CHANGED — RE-DERIVATION REQUIRED

V5's `authorized_source_commit` must point at the **future merged remediation
commit**. It must **not** be `8c7a385d…` (what 002 named) and must **not** be
`8e3f9023…` or `fd16ae5b…`.

**This handoff is bound by that too.** Handoff bytes are repository source, and
`COPY . /opt/cardiosentinel/src-tree` makes the source tree image content with
`.dockerignore` not excluding `docs/`. So this file is inside whatever artifact
V5 eventually authorizes, and the V5 source commit binds this update as much as
it binds the Containerfile.

**Reproducibility remains falsifiable, not proven.** Nothing has ever been built
twice — nothing has ever been built once.

### Findings left open, each wanting an owner decision

- **`builder_authorization.main()` prints one headline for every exception** —
  *"controlled build refused: builder authorization absent"* — so a refusal
  caused by missing git history names an authorization that is present. Found by
  ECG 28, deliberately not fixed by ECG 28, 29 or this session. It alters gate
  output that receipts quote.
- **The CI-skip tension** (ECG 29). Some packet checks need git history and skip
  in CI; full history in CI means touching `.github/workflows/`, which trips the
  build-input guard.
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
generated. No scientific attempt was claimed.

**Two controlled builds have now been dispatched in this programme's history and
neither produced an artifact.** No image exists. No OCI digest exists anywhere.

Frozen and byte-unchanged, verified this session:

```text
J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1  cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0
J1_PRE_REGISTRATION_V1                  1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1
J1_FREEZE_RECEIPT_V1                    d116199affdc8488fefc765fee86efcd1aae23dee68b0bd302d4e055b08ee107
J1_AUTHORIZATION_CONTRACT_V1            9aae5a98475444bc8afa50779a4aaf59449a25ae7fbdb8024f4a0d6d8a048d80
```

Retained receipts, never re-pointed: V1/V2/V3/V4 packets, authorization acts V1
and V2, the 001 pre-claim failure receipt, the 002 post-claim failure receipt,
the canonical 002 qualification claim, Protocol V1, Protocol V2, the builder
selection receipt.

RQ4 **Supported (bounded)**. RQ3 a **negative finding**. RQ1, RQ2 (partial),
RQ5, RQ6, RQ7 open — every one needs a run.

---

**The characteristic failure of this session:** *proving everything about an
apparatus except that it runs.*

ECG 28's was "a test that passes tells you about the environment it ran in".
ECG 29's was "a green CI run is not evidence the test you wrote had run". This
one is the same family and cost the most: a one-shot human authorization was
spent discovering a **syntax error**. Every digest was correct. Every membership
proof held. The file was byte-identical to what a human reviewed. And the first
time anything executed the command inside it, pip rejected it in 0.7 seconds.

**When ECG 31 reviews an apparatus, find the boundary nothing has ever
crossed — and cross it cheaply, before an authorization does it expensively.**
