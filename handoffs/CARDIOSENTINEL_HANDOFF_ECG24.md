# CardioSentinel — handoff to session "ECG 25"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| Branch | `feat/e11-e13a-instrumentation-and-paper-readiness` |
| GitHub | `DebalekhaChakraborty/CardioSentinel` — **PR #128 is MERGED** |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **The Bash working directory silently resets** — put
`cd` in the same command as the work. **Never `git add -A`.** **Never run
`ruff format`** — see §6.

---

## 1. STATE — everything is green

```
pytest tests -q      3542 passed, 1 skipped, 0 failed     (18m)
ruff check .         All checks passed
citation verifier    108 keys · 87 unique · 87 works · 0 unresolved
claim guard          18 patterns · 17 occurrences · 0 genuine overclaims
git status           clean
```

**Nothing is broken and nothing is half-finished.** The science is complete, the
manuscript is content-frozen, and the repository is organised. Start new work
freely.

**Four commits are on the branch and not pushed:**

```
568c211  Handoff: ECG 24 …
c063b38  Fix: the claim guard reported one violation per pattern, not every occurrence
15ad054  Paper: the TACTiCS submission candidate, its audits, and the V2 harvest
d6dab5f  Docs: reorganise docs/ into categories and repoint every reference
```

PR #128 already merged, so these need a **new** PR. The branch is 4 ahead / 1
behind `origin/master`.

---

## 2. THE ONLY THING BLOCKING SUBMISSION

**The official TACTiCS 2026 author instructions and template do not exist in
this repository and could not be found.** Three independent web searches
returned only acronym neighbours. `audits/TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md`
records **all 22 requirements as `NOT SPECIFIED`**.

**Do not infer any of them. Do not fabricate a template. Do not compress the
manuscript against an assumed page limit.**

The questions to ask the organisers are written out, ordered by how much they
unblock, in `paper/TACTICS_OFFICIAL_INSTRUCTIONS_NEEDED.md`. Fourteen human
metadata fields — authors, affiliations, approvals, AI-use disclosure — are in
`paper/TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md`. **Only a human can clear
either.**

When the template arrives, the procedure is step-by-step in
`audits/CARDIOSENTIN_SUBMISSION_HANDOFF_FORMAT_PENDING_V1.md` §4, and a ranked
compression plan — SAFE / MODERATE RISK / DO NOT CUT, ~660 words of safe
savings — is in §5 of the same document. **It is prepared and deliberately not
executed.**

---

## 3. THE MANUSCRIPT

`paper/CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md`

| | |
|---|---|
| `sha256` | `78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2` |
| Words | 14,415 total · 13,854 body · **279 abstract** |
| Figures / tables / works | 5 (F1–F5, F6 refused) · 4 (T1–T4) · **87** |

**Older digests in the audit documents are stale** — the file changed twice
after they were written, once to drop a repository path from the Figures section
and once when the reorganisation repointed a path in its banner. **Re-hash
before trusting any recorded digest.** No scientific number ever changed; that
was checked each time by diffing every decimal in the file.

**Title, abstract and keywords are final. Content is frozen.** The novelty claim
is the *coupling* of experimental evidence governance with runtime claim
governance — **not** call-time partition enforcement, one-shot evaluation,
claim-bound numeric rendering or provenance binding, all of which
`audits/CARDIOSENTIN_RELATED_WORK_VERIFICATION_V2.md` shows are precedented.
Red lines that must never reappear are in that document §9.

---

## 4. REPOSITORY LAYOUT

```
paper/      31   manuscript, section drafts, figures, tables, submission metadata
audits/      6   readiness audit, Related Work V1/V2, format review, handoff, requirements
handbook/   10   all handbook versions, .md and .docx
handoffs/   23   ECG3-ECG24
docs/      104   experiments/{b4,m1,m2,p1,t2,u1,w1}, contracts, control-plane,
                 provenance, explanation, external-validation, literature, baselines
                 + the seven T1 documents, deliberately flat
```

**`docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md` maps every old path to its
new one**, and separates the 8 documents that are named by path inside immutable
artifacts under `cardiosentinel-runs/` — including the sealed `TEST_ATTEMPT.json`
and `TEST_AUDIT.json`. Those artifacts still record the pre-reorganisation paths
and **were not edited**; the table is how they resolve. This follows the repo's
own `COMMIT_PIN_TRANSLATION_V1` precedent. **If you move a document, add it
there.** The check is one command:

```
grep -roh 'docs/[A-Za-z0-9_.-]*' cardiosentinel-runs --include=*.json | sort -u
```

### Why the seven T1 documents are flat

`tests/neural/test_t1_*.py` assert that `src/cardiosentinel/neural/t1_*.py` are
**byte-identical to recorded SHA-256 digests**, and those sources construct the
T1 document paths. Repointing them at `docs/experiments/t1/` is a correct path
fix and **still a byte change**, so it fails the freeze — sixteen tests, by
design. The guard exists so the executed protocol cannot drift underneath its
record.

Amending the digests is possible and `docs/T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md`
is the precedent, but it costs a human authorisation and an amendment document,
and **tidying a directory does not justify one.** If T1 source has to change for
a scientific reason, move these seven documents in the same amendment.

---

## 5. EVIDENCE

`cardiosentinel-runs/` — **3.4 GB, intact.** The E11/E12d/E13a delta is mirrored
at `s3://cardiosentinel-evidence-341181499761/snapshot-2026-08-28-4c59ff1/`:
196 objects, 1,193,258,795 bytes, GOVERNANCE lock until **2027-08-28**, SSE-S3.
Verified by object count, exact byte total, manifest round-trip (`07fd04be…`)
and 16/16 sample re-hash. Three snapshots now exist in the bucket.

**All fifteen one-shot budgets are spent.** Sealed TEST consumed 2026-08-25,
`repeat_attempt_permitted: false`. The 44-subject / 79-stream geometry
population was consumed by E13a. **No experiment is authorized and none is
designed.** The remaining work needs no compute.

---

## 6. TRAPS — the ones that cost this session the most

1. **Never run `ruff format`.** This repo is ruff-*checked*, not
   ruff-*formatted*; CI is `python -m ruff check .`. A format pass reflowed 128
   unrelated files and turned a table of sealed-test SHA-256 constants in
   `m1_experiment.py` into over-length lines.
2. **Never edit a document's content to fix a path.** About 37 documents under
   `docs/` are content-digest-bound; changing one byte breaks
   `sha256(document)` assertions in source. Move them, then update the code that
   points at them.
3. **T1 and some baseline *sources* are digest-frozen too**
   (`tests/baseline/test_source_verification.py`, `tests/neural/test_t1_*.py`).
   Check before editing anything under `src/cardiosentinel/neural/t1_*`.
4. **Four different path-construction forms exist.** Grep for all of them:
   `"docs/NAME"`, `"docs" / "NAME"`, `DOCS / "NAME"`, `"docs" / f"{NAME}.md"`.
   Fixing three and missing the fourth looks like success until the suite runs.
5. **Any automated line-rewrap must be AST-checked before writing.** Heuristic
   wrapping broke a `lambda` and turned `==` into `=(` + `=`.
6. **`git status` shows `D` for an unstaged `mv`.** A directory move looked like
   deletion and produced a false data-loss alarm. Check the new location before
   concluding anything is gone.
7. **`pgrep -f` self-matches** — a check that greps its own command line always
   reports ALIVE.
8. **The full suite takes ~18 minutes.** Run it in the background; do not poll
   with short sleeps.

---

## 7. WHAT ECG 24 DID

It mirrored 1.11 GiB of irreplaceable evidence to S3 with hash verification.
It fixed a citation verifier that had been silently skipping 16 keys hidden
inside shared brackets, and a claim guard that reported one violation per
pattern instead of every occurrence — both false negatives in the direction that
matters, in tooling whose whole purpose is to catch what a human would miss.
It ran a falsification search that **cost the paper its original novelty claim**
and narrowed it to the two-surface coupling. It confirmed all 19 citation venues
against official sources. It assembled, froze, titled and abstracted a
14,415-word manuscript. And it produced the format review that established there
are no TACTiCS rules to comply with.

**Then it broke the repository trying to tidy a directory**, taking the suite
from 3541 passing to 154 failures before recovering to 3542. Every regression
was self-inflicted, and each was found by running the tests rather than by
thinking about the change first. **The reorganisation should have begun by
enumerating the digest-bound and artifact-named files — the exact list that now
sits in the translation table — instead of ending with it.** The recovery is
complete and the lesson is §6.

**This session's characteristic failure**, stated because the chain requires it:
ECG 24 did excellent work on evidence, tooling and the manuscript, and then
spent its final third repairing damage it caused doing something cosmetic that
nobody's science depended on.
