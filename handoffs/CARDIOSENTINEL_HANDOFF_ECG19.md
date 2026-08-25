# CardioSentinel — handoff to session "ECG 19"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG19.md in the repo and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use here) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/CardioSentinel` |
| Master at handoff | `01f035e`, CI **green** |

Python `3.12.6`, torch `2.13.0+cpu`, numpy `2.3.2`. Never install, upgrade or
downgrade anything in `tactics`.

**Shell state:** the Bash working directory silently resets, and a `cd` inside
one command persists into the next. Always `cd` explicitly, and never write to a
relative path without checking where you are — ECG 18 lost one file write that
way and only noticed because the target directory did not exist. Never
`git add -A` anywhere near `/home/AI_POC`.

**You share the checkout with two other workers**, one of them the user at the
keyboard. `HEAD` moves under you between commands. Run `git status` before
anything that assumes a branch or a clean tree, stage explicit paths only, and
do not clean up untracked files you did not create — the user commits drafts
that other sessions leave untracked, and that is the actual workflow.

---

## 1. THE HEADLINE — the documents are true again, and every budget is spent

ECG 18's job was §4.1 of the previous handoff: the sealed test had been consumed
and every living document still said it was unopened. **That is done and merged.**

| PR | What |
|---|---|
| **#112** | CI repair — master had been red since #107 |
| **#113** | §4.1 — six living documents made true |
| **#114** | §4.2 — the sealed-test row in paper §7, executing §9.8 |
| **#115** | the experiment catalogue, missed by #113 |

**All fifteen one-shot budgets are spent. There is no unspent access anywhere in
this programme**, and nothing further can be measured without a new human
authorization, a re-scoring run, or data the project does not have.

What the governance machinery now protects is the **record**, not a budget.
Consumed attempt directories are immutable, the four sealed-test artifacts are
immutable, and every `*_AUTHORIZED` flag sitting `True` on disk is a spent token.

`docs/CURRENT_STATE.md` was regenerated wholesale against `61d9009` and is the
place to start. Its §4.1 carries the sealed-test result with its full boundary,
and §10 carries eight defects.

---

## 2. What was NOT changed, and why you must not "fix" it

**Roughly a hundred files still contain `"sealed_test_state": "unopened"`, and
they are correct.** Each is an attestation about the run that wrote it — P1's
lock says the test was unopened at P1's execution time, and that stays true
forever. They are historical records, not a status board.

Measured 2026-08-25, over artifacts and source, excluding documentation prose
and excluding `__pycache__` and `.pytest_cache`: **97 files** — 67 `.json` (58
under `cardiosentinel-runs/`, 13 of them `EXPERIMENT_LOCK.json`), 29 `.py` in
`src/` and `tests/`, one `.log`. Handbook §43 carries this with its date and its
exclusions.

**Read `sealed_test_state` as "the state when this artifact was written."**
Handbook §43 says so; §54.2 and the README's lineage example carry the note
beside the two places that quote such a lock verbatim.

Also frozen and not edited: `B4_TEST_DEFERRAL_DECISION_V1.md` and every dated
`_V1` record. They were not wrong when written. Rewriting them destroys the
evidence that a decision was reconsidered rather than never taken.

---

## 3. Traps ECG 18 hit. Every one of them looked fine first.

### 3.1 The guard that had become the failure

`tests/neural/test_b4b_sealed_test_identity.py`'s autouse fixture asserted
`no TEST_ATTEMPT exists anywhere under cardiosentinel-runs/`. **That conflates
two claims:** *"this suite created no attempt"*, which is the property the
module exists to protect, and *"no attempt has ever been taken"*, which stopped
being true at 00:17:57Z on 2026-08-25.

All 23 tests in the module errored at setup on any machine holding the evidence
tree, reporting a violation of something they were never asked to protect.

Fixed in #112 by comparing an **inventory** — path plus content digest for every
recorded attempt — before and after each test. Strictly stronger for the
intended purpose: a count of one would still have passed if the bytes had
changed underneath it.

**Generalise this.** A safety assertion written as a fact about the world
expires when the world changes. Written as an invariant on change, it does not.

### 3.2 Two digests with the same name and different values

`TEST_AUDIT.json`'s own `test_audit_sha256` is **`79447d4d…`** — self-referential,
SHA-256 of the payload with that field removed, `sort_keys=True`,
`separators=(",", ":")`, the same rule the experiment locks use.
`TEST_ATTEMPT.json`'s field of the **same name** is **`2f6af19c…`** — the SHA-256
of the `TEST_AUDIT.json` file bytes.

Both recomputed and confirmed. **Both correct about themselves.** The ECG 18
handoff quotes the first without saying which it is. `CURRENT_STATE.md` §4.1
now states the distinction. Say which one you mean.

### 3.3 Two inherited counts, neither of which survived being counted

The previous handoff said B4-B's lock digest is registered in **28 files**; it
is **32**. The handbook and catalogue said **80 artifacts** read
`sealed_test_state: unopened`; that matched no partition of the real count.

Both had been passed forward unmeasured. **Re-count anything you are about to
repeat.** Note also that `grep -r` from the repository root silently omits the
evidence tree, because it is gitignored — which is how a count can be run
honestly and still be wrong.

### 3.4 A count that changed the thing it counted

Writing *"the string occurs in N files"* into the handbook made the handbook one
of them. Fixed by naming a population that excludes documentation prose, and by
saying in the text why the exclusion exists — a reader who re-runs the grep gets
a different number and should be able to see immediately where it comes from.

### 3.5 Master was red, and the red tick said nothing

`ruff check .` had failed since #107 landed. **PR #111 — two markdown files —
was failing a check it could not have caused.** A red tick that is inherited is
worse than no tick: it trains everyone to ignore it.

The E402s in `b4b_sealed_test.py` were suppressed in `pyproject.toml` rather
than fixed by hoisting the imports, because that file's source order is asserted
by `inspect.getsource` in two tests — the identity gate must precede the attempt
claim, and only one arrangement refuses before writing a receipt.

---

## 4. Open items for ECG 19, in priority order

### 4.1 §2 Related Work — the blocker, still unstarted

Still does not exist, still blocks §9.3, and carries the §6.3 condition of
`B4_TEST_AUTHORIZATION_V1.md`: **it must not be shaped by the sealed-test
result.** The literature search has not begun. The gap statement must be written
*after* the search, not to fit the contribution.

**This is the only unstarted item in the paper plan and it has been the top
open item for three sessions.** Every previous session found something else to
do first, and each of those things was genuinely worth doing. That is what makes
it the danger this handoff names.

### 4.2 Back up the sealed-test artifacts — the highest-consequence defect

`CURRENT_STATE.md` defect 6. Four files, **one copy**, on one machine, outside
git and outside the S3 mirror:

```
cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/
  TEST_ATTEMPT.json  TEST_METRICS.json  TEST_PREDICTIONS.npz  TEST_AUDIT.json
```

Every other result in the programme could in principle be recomputed. This one
cannot: `repeat_attempt_permitted` is `false` and no authorization can make it
true. The S3 snapshot is `snapshot-2026-08-22-1bbbd47` — **three days older than
the artifacts** — and a headcount on it still passes.

The AWS session has **expired again**, one day after the mirror was verified, so
defect 1 is reopened and the mirror cannot currently be checked at all. Renewing
needs a human at a browser (`aws login`, MFA, no static root keys).

ECG 18 wrote a step-by-step runbook and ran none of it. **Ask the user where it
went** — it was left outside the repo per the scratch-file constraint. It
includes one unresolved discrepancy worth carrying: the manifest covers 785
files, the trees now hold 788, and 785 + 4 new ≠ 788. **Resolve that before
trusting any count.**

### 4.3 The runtime still asserts the test is unopened, in seven places, and
two safety gates are now permanently pinned because of it

`CURRENT_STATE.md` defect 7 named three of these. **There are more, and one
group is worse than a stale string.** ECG 18 found them by running the full
suite locally, which CI cannot do — see §5.

**Group A — user-visible text that is simply false.**

| | |
|---|---|
| `edge/console.py:39` | emits *"The sealed neural test is unopened."* as a demo limitation |
| `agents/claims.py:216` | registers *"any claim about the sealed test, which is unopened"* as an approved disclaimer |
| `agents/claims.py:107` | Appendix A claim 12 rationale: *"The neural chain is unopened."* |

`docs/DEMO_SCENARIO.md` §4 and §5 mirror the console strings and
`tests/edge/test_demo_scenario.py` pins them (`len(LIMITATIONS) == 5`, each item
present in the output), so **console, contract and test must move together.**

**Group B — hardcoded provenance.** `edge/artifacts.py:101` and
`agents/research.py:95, 167, 258` write `"sealed_test_state": "unopened"` into
the provenance dict the runtime reports. **These are constants, not values read
from a lock**, so unlike the ~97 files in §2 they are *not* attestations about a
past run and they are *not* protected — they are the live system answering a
question wrongly. `tests/edge/test_demo_scenario.py:95` asserts one of them.

**`tests/agents/test_research_assistant.py::test_the_sealed_test_claim_matches_the_tree`
is failing right now**, and its docstring reads *"The one fact a reviewer will
check first."* It compares the assistant's `sealed_test_unopened` topic against
`rglob("TEST_ATTEMPT.json")` and finds 0 claimed against 1 present. **That test
is doing its job.** Do not weaken it; make the claim true.

**Group C — and this is the one to look at first. Two readiness gates are now
permanently pinned to a single answer.**

`m1_experiment.scan_test_artifacts()` walks
`REPOSITORY_ROOT/cardiosentinel-runs/**/TEST_*` **by design** — its docstring
says a hardcoded `False` "would make the firewall decorative". That was correct
and is still correct. But its result feeds:

- `m1_preflight`, where `test_artifact_present_human_review_required` is the
  **highest-precedence** status, and
- `p1_preflight`, where it is second, above `embedding_cache_materialization_required`.

So on any machine holding the evidence tree, **M1 and P1 preflight now return
`test_artifact_present_human_review_required` for every run, forever**, masking
cache readiness, encoder verification and challenge validation underneath it.

**This is not a bug and it is not unsafe** — it fails closed, which is the
design. It is a gate whose trigger condition became permanently true because
four legitimate, authorized, recorded artifacts now exist. The gate has no way
to say *"these four are known and expected"*.

**Deciding what it should say instead is a governance decision, not a coding
one**, which is why ECG 18 left it. The options are roughly: pin the four known
artifact paths and their digests as expected, and fire only on anything else; or
accept that both preflights are now uninformative on a research machine and
record that. **Do not simply relax the gate.**

Related: `tests/neural/test_m1_experiment.py::test_test_artifact_scan_actually_walks_the_supplied_roots`
asserts `scan_test_artifacts(tmp_path) == []`. Its *intent* — prove the function
walks the supplied root rather than hardcoding `False` — is still right; its
assertion encodes the old world. **Same shape as §3.1, for the third time
today.**

### 4.4 Drafts merged and unreviewed

`PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`, `PAPER_S9_DISCUSSION_SKELETON.md`,
`PAPER_S9_DISCUSSION_DRAFT.md` (#105). §9.3 is deliberately stubbed on §2.
§9.7 exists as prose in the **draft** but the skeleton still lists the
provenance-incident subsection as accepted-and-unwritten; reconcile the two.

### 4.5 RQ5 / edge

Still open. A laptop replay is not an edge measurement. Nothing has changed.

---

## 5. CI is green and the local suite has seven failures. Read them; they matter.

Measured on master `01f035e` with `/home/AI_POC/venvs/tactics/bin/python -m
pytest -q`: **7 failed, 3343 passed, 1 skipped**, 17m34s. CI on the same commit
is **green**.

**The divergence is not the pre-existing defect handbook §47 describes.** All
seven failures are consequences of the sealed test being consumed, and every one
of them is invisible to CI because `cardiosentinel-runs/` is gitignored and the
runner has no evidence tree:

```
tests/agents/test_research_assistant.py::test_the_sealed_test_claim_matches_the_tree
tests/neural/test_m1_bounded_memory.py::test_preflight_flags_a_staging_directory_for_human_review
tests/neural/test_m1_experiment.py::test_test_artifact_scan_actually_walks_the_supplied_roots
tests/neural/test_m1_experiment.py::test_preflight_reports_partial_cache_for_human_review
tests/neural/test_m1_experiment.py::test_preflight_refuses_an_orphan_standardizer
tests/neural/test_m1_experiment.py::test_preflight_absent_cache_is_healthy_initial_state
tests/neural/test_p1_experiment.py::test_preflight_is_read_only
```

Six of the seven are the §4.3 Group C gate; the seventh is the research
assistant's claim. **None is a regression from #112–#115** — those touched
documentation and two test modules, all of which pass.

**Which means the machine that can see the problem is the one whose test suite
nobody trusts.** CI is authoritative for *"did I break something"* and blind to
*"is the system still telling the truth about the evidence on disk"*. Run the
full local suite before you believe the second thing, and read the failures
rather than counting them.

When you touch a test, run that module locally **and** in a tracked-files-only
copy, which is what CI sees:

```bash
SB=/tmp/ci-sim && rm -rf $SB && mkdir -p $SB
cd /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
git ls-files -z | cpio -0pdm $SB          # rsync is not installed here
cd $SB && /home/AI_POC/venvs/tactics/bin/python -m pytest tests/... -q
```

That copy is what CI sees, and it is how #112's evidence-gating was verified
before it was pushed rather than after.

---

## 6. Standing constraints — unchanged except where noted

- **The sealed test is consumed. There is no second attempt and no budget left
  to protect.** What remains to protect is the record: the four artifacts are
  immutable. Do not regenerate, amend or "fix" any of them.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- **Do not change any number, threshold or claim in light of the result.** Not a
  thesis, not a hedge, not an emphasis. §9 was drafted before the test opened and
  §9.8 clause 1 binds.
- **§2 must not be shaped by the sealed-test result** — §6.3 of the
  authorization.
- No M2 / U1 / T2 rerun. No T1 fold retry. No second continuation. Consumed
  attempt and continuation directories are immutable.
- Never install/upgrade/downgrade packages, especially in `tactics`.
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- Keep scratch files **outside the repo**.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; **never** a
  predictive feature.
- Labels never determine memory-stream membership, ordering or update
  eligibility.

---

## 7. Provenance — read before following any commit pin

A history rewrite on 2026-08-24 changed **268 commit identifiers**. File
contents did not change; every tree is identical. **69 commits cited across 71
tracked files stopped resolving.**

- `COMMIT_PIN_TRANSLATION_V1.md` — 326 exact mappings, both directions.
- `PROVENANCE_INCIDENT_V1.md` — the dated chronology.

**Experiment locks cannot be corrected in place.** `experiment_lock_sha256` is
self-referential, and B4-B's appears in **32 files** — 9 of them other
experiments' locks. Translate; never edit.
`neural.integrity.verify_experiment_lock()` implements the check.

**Do not run `git gc --prune=now`.** `refs/original/*`,
`refs/local-backup/pre-coauthor-rewrite` and
`~/cardiosentinel-recovery/pre-coauthor-rewrite.bundle` hold the pre-rewrite
history — which also means **`git cat-file -t` on an old SHA succeeds here and
fails on a fresh clone.** It is not a test of whether a pin resolves.

The handbook v1.4 header pin `fb758dd` is pre-rewrite; it translates to
`05f28d2`.

---

## 8. Facts that are easy to get wrong

- The selected encoder is **B4-B** `B4B_cnn_transformer_v1` /
  `B4BTransformerCNN`. B4-A `B4_raw_compact_cnn_v1` was **rejected** and is
  retained only as the efficient-CNN reference. The sealed evaluator was
  originally bound to the rejected one; handbook **§43.2** records it.
- Subject-macro discrimination on the sealed test is over **8 of 12** subjects.
  F1, NPV, PPV and specificity are over 12 of 12. **Never quote one without its
  denominator.**
- The MCC interval **[-0.033876, 0.221346]** includes zero.
- The threshold `0.8329097628593445` came from **validation**,
  `test_informed: false`, and was never recomputed.
- Scores are **uncalibrated sigmoid model scores, not calibrated probabilities.**
- Conduction-change challenge evidence — 8 of 10 windows, **one** subject — is
  exploratory and descriptive. Never bootstrapped, never headlined.
- All three B4 locks read `status: locked_for_one_shot_test` with `test: null`,
  **including B4-B's, after the test ran.** The lock is frozen at development
  time; it is not a record of the test.
- `cardiosentinel-runs/`, `cardiosentinel-features/`, `cardiosentinel-data/` are
  gitignored. The B4-B checkpoint and lock are mirrored in
  `reproducibility/demo_bundle/` and **are** tracked.

---

## 9. Open defects — recorded, not resolved

The full list with reasoning is `CURRENT_STATE.md` §10. The four that should
shape ECG 19's plan:

1. **§2 Related Work does not exist** and the literature search has not started.
2. **The sealed-test artifacts have one copy** and cannot be regenerated (§4.2).
3. **M1 and P1 preflight are permanently pinned** to
   `test_artifact_present_human_review_required` on any machine holding the
   evidence, masking every other readiness signal (§4.3 Group C).
4. **The S3 mirror is unverified**, the session expired one day after it was
   last checked.
5. **Seven runtime assertions that the test is unopened are false**, four of
   them hardcoded provenance rather than frozen attestations, and one test is
   correctly failing on it (§4.3).

**`CURRENT_STATE.md` §10 defect 7 understates this** — it was written before the
full local suite had been run. Items 3 and 5 above supersede it.

---

## 10. The danger this handoff names

**Making true documents truer, instead of writing §2.**

ECG 18 was handed one job — make the documents true — and it did that, then
found five more things wrong and fixed those too. Every one of them was real:
CI was genuinely broken, the counts were genuinely wrong, the catalogue
genuinely contradicted the ledger. None of them was §2.

There is now very little left in this repository that is *incorrect*. There is
still no §2, no literature search, and no manuscript. **The next defensible task
is the one that has been top of the list for three sessions and produces prose
rather than corrections.**
