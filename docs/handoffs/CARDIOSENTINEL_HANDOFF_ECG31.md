# CardioSentinel — handoff to session "ECG 32"

Paste this whole file as the first message of the new chat, or say:
"Read `docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG31.md` in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do **not** use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/CardioSentinel` |
| Branch at handoff | `master` at `73e6b1e8570f69635a64d3aa8abde1ccb9f4c0f2`, clean |
| **Open PRs** | **none.** #157–#164 are all merged |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **Never `git add -A`.**

### The working directory drifts. Prefix every command.

`cd /home/AI_POC/tactics/CardioSentinel &&` in **every** command. It caught me
three times this session, every time immediately after a command that ended
somewhere else — a `cd` inside a compound command persists into the *next* Bash
call, and the `--depth 1` clone checks below are the usual culprit.

The two tells: `gh` failing with *"none of the git remotes point to a known
GitHub host"*, and `ruff check .` returning **5366 errors** from the outer
monorepo. **Anything over ~10 ruff errors in a clean tree means you are in
`/home/AI_POC`.**

### The symlink existed this session. Check anyway.

```bash
ls -ld /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
ln -sfn /home/AI_POC/tactics/CardioSentinel \
        /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
```

### Disk

**2.5 GB free at 98%.** The B4 neural path needs 2,147,483,648 free output bytes,
so you are ~350 MB above the failure ECG 26 chased. Clear pure cache only —
`~/.cache/pip`, `~/.npm/_cacache`, `/tmp/pytest-of-*` (that is where I got the
last 300 MB). **Do not delete `~/.cache/hf-bench` (13 GB)** or the 25 GB under
`cardiosentinel-data/`, `-features/`, `-runs/`.

A `--depth 1` clone is ~19 MB. Use one; see §5.

Local suite is **936 passed** in ~55s:

```bash
pytest tests/journal_extension tests/reproducibility tests/neural/test_b4b_sealed_test_identity.py
```

CI runs bare `pytest -q` — **4303 passed, 140 skipped** on merged master.

---

## 1. STATE

**J1 science is unchanged and still not authorized.** Everything below is the
build environment.

```text
J1                           PRE-REGISTERED — NOT AUTHORIZED
active builder authorization ABSENT
authorization 001            RETIRED, NOT SPENT   (PRE_ARTIFACT_INFRASTRUCTURE)
authorization 002            SPENT, RETIRED       (POST_CLAIM_PRE_ARTIFACT)
authorization 003            SPENT, RETIRED       (POST_CLAIM_PRE_ARTIFACT)
authorization 004            DOES NOT EXIST
controlled-build runs        3   (all attempt 1, all failure)
qualification claims         2   (002 and 003, both preserved in-repo)
Actions artifacts            2   (those two claims; nothing else)
environment artifact         NEVER PRODUCED
environment authority record ABSENT
J1 attempt budget            NOT ESTABLISHED
scientific attempts used     0
```

# THREE DISPATCHES. ZERO ARTIFACTS. NOTHING HAS EVER BEEN BUILT ONCE.

### THE IMMEDIATE NEXT ACTION

**PR #164 merged the V2 dependency audit. The programme is now blocked on a
human decision, not on a defect.**

The audit finished `CANDIDATE READY FOR DEPENDENCY-AUTHORITY REVIEW — NOT
AUTHORIZED`. Four questions are open and **none of them is yours to answer
alone**:

1. **Is artifact-byte binding required** before a V2 authority — a wheelhouse, or
   hashes carried in a new lock? Byte authority is `ABSENT` for all 48 candidate
   members.
2. **Is present-day transitive metadata acceptable evidence** for historical
   dependency relations, or must those be re-established from historical
   artifacts? This is the audit's largest disclosed gap.
3. **What becomes of the 287 packages** with no established J1 relation — in
   particular the 111 reachable from `incident-management`?
4. **Is `incident-management` extraneous?** The audit deliberately did not decide.

The sequence is:

```text
human decision on a V2 dependency authority
  -> authority materialization
  -> V6 builder review packet
  -> human authorization 004
  -> ONE controlled qualification
```

**Not** audit → dispatch.

---

## 2. WHAT THIS SESSION DID

Eight PRs merged, **#157 → #164**. Two authorizations were spent. Two controlled
builds failed. The programme went from "builder authorized" to "the dependency
authority itself is the problem".

| PR | What |
|---|---|
| #157 | `J1-ENV-BUILDER-AUTH-002` recorded from V4 |
| #158 | preserved 002's post-claim failure; retired 002 |
| #159 | apparatus remediation — the pip syntax repair + executable preflight |
| #160 | V5 review packet, re-derived against the corrected object |
| #161 | `J1-ENV-BUILDER-AUTH-003` recorded from V5 |
| #162 | preserved 003's post-claim failure; retired 003 |
| #163 | evidentiary correction — bounded four universal-negative claims |
| #164 | the full 335-member dependency provenance and necessity audit |

### The two spent authorizations, and why they differ

```text
002  run 33902875021   claim recorded, both builds failed
     --require-hashes option does not take a value
     -> pip CLI syntax defect in the authorized Containerfile   (apparatus)

003  run 33984680149   claim recorded, both builds failed
     No matching distribution found for incident-management==0.1.0
     -> dependency-source authority insufficiency               (reconstruction)
```

**They share a failure class and do not share a cause.** The #159 repair worked:
002 died at argument parsing in 0.7 s having installed nothing; 003 parsed,
reached the index, and collected **128 packages** before stopping. Each repair
was correct and each exposed the next layer down.

### What the audit found

`incident-management==0.1.0` was not a one-package accident.

# Every one of the 335 historical records carries `name` and `version` and nothing else.

No artifact filename, no hash, no index URL, no installer. So
`wheel_or_sdist_byte_authority` is **`ABSENT` for all 335 without exception**, and
provenance from the historical evidence alone is `UNKNOWN_ORIGIN` for all 335.

**A package list records what was present. It cannot, by construction, record
where any of it came from.** That is the deficiency — not a wrong digest.

```text
b0fd6eaa…  remains a valid HISTORICAL SNAPSHOT AUTHORITY
b0fd6eaa…  is NOT a V2 RECONSTRUCTIBLE DEPENDENCY AUTHORITY
```

The J1 closure turned out small and clean: **113 modules importing six
third-party distributions** (`numpy`, `scipy`, `scikit-learn`, `torch`, `wfdb`,
`PyYAML`), expanding to **48 required packages**, all with an identified
reconstructible source. **287 of the 335 have no established relation to J1**,
and **111 are reachable from `incident-management`'s own agent-stack closure**.

---

## 3. THE AUDIT ARTIFACTS, AND HOW TO READ THEM

```text
J1_V2_DEPENDENCY_PROVENANCE_AUDIT_V1.csv     335 rows, canonical machine ledger
J1_V2_DEPENDENCY_PROVENANCE_AUDIT_V1.md      how each column was decided
J1_V2_SCIENTIFIC_CODE_CLOSURE_V1.md          the 113-module J1 closure
J1_V2_IMPORT_DISTRIBUTION_MAP_V1.json        import root -> distribution
J1_V2_LOCAL_DEPENDENCY_ORIGIN_DIAGNOSTIC_V1.json   LOCAL_DIAGNOSTIC ONLY
J1_V2_DEPENDENCY_AUTHORITY_CANDIDATE_V1.json CANDIDATE_ONLY / NOT_AUTHORIZED
J1_V2_DEPENDENCY_AUTHORITY_AUDIT_REPORT_V1.md the narrative and the readiness state
```

**The CSV is the authority among these; the prose explains it.** Every row's
classification rests on an AST import site, a `Requires-Dist` edge, a
`pyproject.toml` extra, a `direct_url.json`, or a console-script entry point.
Nothing was classified from a package name, and rows with insufficient evidence
say `UNKNOWN` rather than guessing.

**`incident-management` is `UNRESOLVED_DO_NOT_RETAIN`, not "remove it".** No
CardioSentinel necessity is *established*; that is a different claim from
removability, and a test stops the record drifting into the stronger one.

---

## 4. THE CHARACTERISTIC FAILURE OF THIS SESSION

# Reaching past the evidence to the stronger claim that reads better.

Qualification 003's provider output said one configured source returned nothing.
I wrote that the distribution **"cannot be resolved from any public index"**,
that it **"cannot be obtained"**, that **"one member is not obtainable"**, and —
worst — that an editable install proved **"a distribution that never existed on
any index"**.

A `direct_url.json` records how *one machine* obtained a distribution. It carries
no information whatsoever about publication history anywhere else. **One query
against one source cannot support a universal negative.** All four were merged
before review caught them; #163 bounded them and recorded the correction rather
than quietly rewording a merged receipt.

**Then I did it again inside the audit itself.** Pass one probed PyPI for
`torch==2.13.0+cpu` and recorded it unavailable — but `+cpu` is served by the
PyTorch CPU index the Containerfile configures. PyPI was the wrong source.
Re-probed correctly: 31 wheels, available.

The same error twice in one session, the second time while writing the document
that corrected the first.

**When you write that something is unavailable, name the source you asked.**

---

## 5. TRAPS (ECG 27–30 still apply — these are new or sharpened)

1. **A negative from one source is a fact about that source.** §4. Say which one.
2. **Grepping a document that explains what it forbids will fail.** Hit *three
   times* this session: a receipt saying "002 is **not** retry-eligible", a report
   saying `Not the same claim as "safe to remove"`, and an audit report doing the
   same. **Check headings and structure, not substrings** — or reword the heading
   so the phrase is not there to find.
3. **A test that transforms its input can transform away the defect.** The pip
   preflight's first sanitizer dropped value-taking options *with* their values,
   so a malformed `--index-url` would have vanished instead of being rejected —
   and the "derived from bytes" check was circular. Whenever a harness cleans its
   input, **prove it still fails on a known-bad input**.
4. **`git revert` does not clear a pathspec guard.** `git log <range> -- <paths>`
   lists commits that *touched* the path, and a revert is one. Only dropping the
   commits works.
5. **Verify a source-identity instruction rather than obeying it.** #161 said use
   `bc9337ae`, not the #160 merge. I checked *why*: `git diff` showed #160 changed
   only the packet and its test, and the build-input guard range was empty. The
   instruction was right, and now it is proven right.
6. **PEP 503 normalization collapses `-`, `_` **and `.`**.** I nearly reported six
   packages as drifted between the lock and the venv; it was my `norm()` handling
   only `_`. Under correct canonicalization: 335/335, zero drift.
7. **Diff the CI skip count, not just the pass count** (ECG 29). Still the
   cheapest way to catch a test that silently stopped running.
8. **Check a `--depth 1` clone before pushing.** It caught a newly added test that
   *failed* there while passing locally, and a skip I had re-introduced.
9. Still true: **`gh pr checks` has no `--json`** (gh 2.23.0); **`gh pr edit`
   fails silently** — use `gh api -X PATCH -F body=@file`; **`grep` is ugrep** and
   skips gitignored paths; **never `ruff format`**; **poll CI in one background
   waiter**.

---

## 6. WHAT IS OPEN

```text
human decision on the V2 dependency authority     <- NEXT, and it is the owner's
        v
authority materialization  (wheelhouse? hashes in a new lock?)
        v
V6 builder review packet, re-derived
        v
human authorization 004     (never 001, 002 or 003)
        v
ONE controlled qualification
        v
BUILD_A + BUILD_B -> reproducibility record
        v
durable evidence -> environment authority record
        v
J1_AUTHORIZATION_V1 -> ONE J1 attempt
```

**Reproducibility is still falsifiable and still untested.** Nothing has been
built even once, so BUILD_A/BUILD_B has never run to comparison.

### Findings left open, each wanting an owner decision

- **The four audit questions in §1.** These are the live ones.
- **`builder_authorization.main()` prints one headline for every exception type** —
  *"controlled build refused: builder authorization absent"* — so a refusal caused
  by missing git history names an authorization that is present. Found by ECG 28,
  left by 28, 29, 30 and 31. One line in `main()`. It alters gate output that
  receipts quote, so **ask before changing it**.
- **The CI-skip tension** (ECG 29). Some packet checks need git history and skip
  in CI; full history in CI means touching `.github/workflows/`, which trips the
  build-input guard. Six skips remain in `tests/journal_extension` under a shallow
  checkout, all in the packet module, all loud.
- **Protocol V1 says `cardiosentinel==0.1.0 — no index resolves it`**, arguably
  the same class of universal claim §4 is about. Protocol V1 is a retained
  receipt; flagged, deliberately not edited.
- **The S3 mirror re-check is still owed and still blocked.**
  `aws sts get-caller-identity` returns session expired. Object Lock retention
  expires 2027-08-22.
- **`tactics` is a witness, not an authority.** It still matches the frozen
  snapshot exactly — 335/335, zero version drift. One `pip install` destroys that.

---

## 7. THE SCIENCE IS UNCHANGED

All fifteen V1 one-shot budgets remain spent. **No physiological data, annotation
or reference-episode count was accessed at any point this session.** No fold,
calibrator, threshold, candidate selection or scientific result was generated. No
scientific attempt was claimed. The 335-package audit was static analysis and
index metadata only — no package was imported or executed, and no environment
was mutated.

Frozen and byte-unchanged, verified this session:

```text
J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1  cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0
J1_PRE_REGISTRATION_V1                  1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1
J1_FREEZE_RECEIPT_V1                    d116199affdc8488fefc765fee86efcd1aae23dee68b0bd302d4e055b08ee107
J1_AUTHORIZATION_CONTRACT_V1            9aae5a98475444bc8afa50779a4aaf59449a25ae7fbdb8024f4a0d6d8a048d80
```

The three establishing locks, unmodified by the audit and pinned by test:

```text
B4B_cnn_transformer_v1  5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc
P1B_phys_fusion_v1      fdde6475a02e0249e0238b89168e6b043b3ade1ec2bfd75922628127fb27d2ca
M1L_long_memory_v2      6aa199ea5410dde860fd3fcce9ceef0194a364ed2ed5b01678e0648fea60a452
```

Retained receipts, never re-pointed: V1–V5 review packets, authorization acts
V1–V3, the 001 pre-claim receipt, the 002 and 003 post-claim receipts, the 003
local-origin diagnostic and evidentiary correction, both canonical qualification
claims, Protocol V1 and V2, the builder selection receipt.

RQ4 **Supported (bounded)**. RQ3 a **negative finding**. RQ1, RQ2 (partial),
RQ5, RQ6, RQ7 open — every one needs a run.

---

**The characteristic failure of this session:** *reaching past the evidence to
the stronger claim that reads better.*

ECG 28: a test that passes tells you about the environment it ran in.
ECG 29: a green CI run is not evidence the test you wrote had run.
ECG 30: proving everything about an apparatus except that it runs.
ECG 31 is about the write-up rather than the code. The build log said *this
source returned nothing*. Four times I wrote *it cannot be obtained* — and once
more inside the very document correcting the first three.

The stronger sentence was not more useful. It would have sent the next audit
hunting for a package that may well be sitting in a private index.

**When ECG 32 writes a finding, check what was actually asked and what actually
answered — and let the sentence be exactly that wide.**
