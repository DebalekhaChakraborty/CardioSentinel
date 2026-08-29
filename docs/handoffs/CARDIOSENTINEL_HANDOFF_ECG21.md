# CardioSentinel — handoff to session "ECG 21"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG21.md in the repo and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/CardioSentinel` |

`tactics` holds 335 packages, `installed_packages_sha256 = b0fd6eaa…`,
Python 3.12.6. **Verify with `neural.provenance.dependency_environment()`.**
Never install, upgrade or downgrade anything in it — **a single `pip install`
voids that digest and the reproducibility claim it supports.** Nothing was
installed this session; `literature_search.py` is stdlib only for that reason.

**Shell state:** the Bash working directory silently resets. Always `cd`
explicitly. **Never `git add -A`.**

**Three or four sessions share this one checkout, and the user works in it
directly.** HEAD moves under you. Run `git status` immediately before anything
that assumes a branch or a clean tree, and never clean up untracked files you did
not create.

---

## 1. THE HEADLINE — §2 exists, and its central claim was wrong

ECG 20 was handed one job that four sessions had deferred: the §2 literature
search, and the section that depends on it. **Both are done, and the search
refuted the thing §2 was going to say.**

```
master   652da3d + this session's branch
tests    3405 collected, suite green, ruff clean
env      335 packages, b0fd6eaa…  (unchanged — nothing was installed)
search   65 queries, 393 hits, 372 unique records, 0 failures
```

| Artifact | What |
|---|---|
| `scripts/literature_search.py` | the search, as a program — stdlib only, no new dependency |
| `docs/LITERATURE_SEARCH_V1.json` | 393 hits with request URL and retrieval timestamp per record |
| `docs/LITERATURE_SEARCH_V1.md` | the frozen record: protocol, four passes, limits, findings |
| `docs/PAPER_S2_RELATED_WORK_DRAFT.md` | **§2, drafted. 61 citations, 0 unresolved.** |

**The gap statement is dead and its replacement is narrower.**
`PAPER_OUTLINE_V2.md` §2 instructed the author to close the section with *"none
of them, as far as we are aware, ships the machinery…"*. `arxiv:2605.08586`
(May 2026) names the same problem — it calls it **experiment nonrepudiation** —
makes the same negative argument about checklists and code sharing, and ships a
reference implementation. **Four sessions of deferral is exactly how long the
manuscript went carrying a claim a single query would have refuted.**

What survives is in §2.6 of the draft: **that machinery binds the computation;
this apparatus binds the claim.** A signature proves a number came from a run.
Nothing in the literature reads the sentence a human takes away and refuses it
because the evidence does not support that sentence.

---

## 2. What the search is, and how to check it in one command

```bash
/home/AI_POC/venvs/tactics/bin/python scripts/literature_search.py \
    verify docs/PAPER_S2_RELATED_WORK_DRAFT.md
# 61 citations, 0 unresolved
```

Citations in the draft **are** identifiers — `[doi:…]`, `[arxiv:…]`, `[pmid:…]`
— so `verify` resolves each against the recorded search and fails on anything it
did not return. **A citation that no search produced cannot reach the manuscript
unnoticed.** Re-running `harvest` re-executes all 65 registered queries; the
registry is the protocol and is fixed in the source.

**`verify` proves provenance, not comprehension.** It cannot check that a work
says what §2 says it says, and no program in this repository can. Do not describe
it as more than it is — `LITERATURE_SEARCH_V1.md` §6 lists the rest of the
limits, and they are real: metadata not full text, eight hits per query, three
indices, no snowballing.

---

## 3. Four things about this work that are easy to get wrong

- **Pass 1 of the search is deliberately retained and is worthless.** Its arXiv
  queries were natural-language phrases scoped to `all:`; they returned
  portfolio tail-risk papers for a selective-classification query. It reported
  `0 failed`. **Passes 1 and 2 searched the same five literatures on the same
  day and share zero records.** Deleting pass 1 would delete the evidence.
- **Pass 3 and pass 4 are different kinds of evidence and are segregated.**
  Pass 3 asks whether a named work exists; pass 4 was written to *break* the gap
  statement. Mixing them into the topic passes would make the search look better
  and mean less.
- **Two presence tests failed and the draft cites neither work.** The EDB
  reference paper is unreachable from Crossref by topic query (it resolved
  against PubMed); El-Yaniv & Wiener 2010 did not resolve at all, and §2.4 cites
  their 2015 *JAIR* paper instead. **What did not resolve is not cited.**
- **§9.3 was unblocked by this and is now written**, on the search's footing and
  no wider: the §2.4 queries returned 77 records and none reports a mechanism
  built, gated, and abandoned. That is a statement about a search, not about the
  field, and the draft says so three times.

---

## 4. Open items for ECG 21, in priority order

1. **§4 and §4.6 have no draft, and they are the contribution.** This is now the
   largest unstarted item in the manuscript, and it has been skipped by every
   session that had the choice. `PAPER_OUTLINE_V2.md`'s own writing order puts
   them **first**, ahead of §5.6, ahead of §9, ahead of §2 — and §5.6, §9 and §2
   are all drafted while the section the paper is *about* is not. §3.5 is also
   undrafted. **The sources exist. This is writing, not building.**
2. **Assemble one document.** Six `PAPER_*` files, an outline, and a handbook are
   not a manuscript. ECG 20's honest test was whether a stranger could read a
   file at the end of the session; §2 passes that test for one section, and
   there is still nothing a stranger could read end to end.
3. **Snowballing, if §2 is revisited.** `LITERATURE_SEARCH_V1.md` §9: backward
   citations from `arxiv:2605.08586`, forward citations from
   `doi:10.1016/j.patter.2023.100804`. It is the standard next step and it is
   not automated here.
4. **Not recommended: more queries, a fifth gate, a third model.** See §7.

---

## 5. What this session added to the manuscript, and where

**§2 — drafted in full** (`PAPER_S2_RELATED_WORK_DRAFT.md`, 252 lines).
§2.1–§2.5 as the outline specified; §2.6 replaces the refuted gap statement.

**§5.6 — extended from five findings to nine.** Part A is unchanged: the claim
guard catching five of the authors' own boundary statements. **Part B is new**
— four gates, each of which exists because a real generation got past everything
before it: a truncated reasoning trace scoring 1.000 on every metric; `54.6%`
from `0.545613`, invisible to a metric that extracts two decimals; *"G1 through
G6 passed"* when G4 and G5 were blocked; and the categorical validator rejecting
the deterministic fallback over the English word *normal*, certified correct by
its own fixture.

**§9.3 — written**, having been stubbed pending the search.

**§9.5.5 — new, and it is the section most likely to be read outside this
field.** The pattern is now at **ten instances**: a check that passes or fails
for a reason unrelated to what it claims to verify. Six were inherited. **Four
were produced or exposed this session** — the harvest's `0 failed`; the citation
checker reporting 38 of 61 citations unresolved when all 38 were correct and
differed only by an arXiv version suffix; and
`test_real_model_execution_is_a_separate_unexecuted_manual_record`, which
asserted the string `"Status: NOT EXECUTED"` and **passed for a day after the
run happened**. and a `grep` that answered *"does this literal appear elsewhere?"* while being
read as *"is this exemption dead?"*, which an alias defeated. **Every fix went in
the checker, never in the thing checked.** §9.5.5 also carries one counterweight:
`test_the_context_carries_no_research_prose` caught a bad rewording three files
from the edit, doing exactly what its name says.

---

## 5b. The staleness sweep, and what it found

**Asked to prove no document was stale, the sweep found six that were.** All are
corrected in place, each saying so.

| Document | What was false |
|---|---|
| `QWEN_EVALUATION_RUN.md` | **`Status: NOT EXECUTED`**, and an empty run record, for a day after Arm B ran. Populated from the report; **three of fourteen fields are unrecoverable** and are marked, not reconstructed |
| `EXPLANATION_EVALUATION_REPORT_V1.md` | **§6 said `Qwen3-4B-Instruct-2507` "has not been run" while §4.4 reported its result.** The drift was introduced by `13ba0e4`, the commit that was correcting that report. Footer named one model of two |
| Handbook v1.4 | executive summary still said the guard *"caught all three"* — **the undercount §0.5.2 existed to fix, one level up and missed.** §50.3's §2, §9 and §5.6 rows were all false |
| `CURRENT_STATE.md` | pinned to `84991e1`; asserted §2 "does not exist and its literature search has not been started" |
| `IMPROVEMENT_ROADMAP_V1.md` | §7 "Next action: write §2 … the only unstarted item" |
| `README.md`, `PAPER_OUTLINE_V2.md` | §5.6 at five, §9 "to be written" |

**Handbook §53.2.1 is new** and records the four explanation-layer gates in the
handbook itself, so §5.6's nine has a source for both halves.

**The seventh was in code, was user-facing, and is the one to read closely.**
`agents/claims.py` registered the approved disclaimer *"any claim about the
sealed test, which is unopened"* — from before B4-B was authorized until after
it was **consumed on 2026-08-25**.

**It was first assessed as dead code, and that assessment was wrong.** A `grep`
for the literal found one occurrence, in the file that defines it. But
`APPROVED_DISCLAIMERS` is not only an exemption list: `evidence.py` aliases it
as `CANNOT_SUPPORT`, attaches it to every `EvidenceRecord`, prints it under
*"This alert does not establish:"*, and `graph.py` emits each entry as a
`constraint` node bound to the alert. **The value travelled where the literal
did not, so a false boundary was printed to the user on every alert and stored
as graph structure.** That is §9.5.5 instance 10, and it is the one where a
narrow check nearly licensed a *worse* action than the defect.

**Reworded, not deleted**, on the user's decision after the correction — deleting
would have removed a stated boundary from user output, which is §9.5.3's failure
exactly. Two tests were added: one binding the disclaimer to claim 12's `reason`
so they cannot drift apart, one asserting no registered disclaimer carries
research prose. **The second exists because the first rewording spelled out the
denominators and the interval**, and those words must never enter the closed
generator context — `test_the_context_carries_no_research_prose` caught it three
files away, working exactly as designed.

---

## 6. Standing constraints — verbatim, still in force

- **All fifteen one-shot budgets are spent.** `TEST_ATTEMPT.json` exists and that
  is correct. Consumed attempt directories and the four sealed-test artifacts are
  **immutable**. Every `*_AUTHORIZED` flag on disk is a spent token, not a live
  permission.
- **NO AUTOMATIC RETRY. No M2 / U1 / T2 rerun. No T1 fold retry.**
- Never install/upgrade/downgrade packages, especially in `tactics`.
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- Do not change code in response to scientific results.
- Patient identity selects a namespace and a calibrator; **never** a feature.
- **Disk was at 11 GB free.** The two Qwen snapshots are 12 GB in
  `~/.cache/hf-bench`, outside every repo and safe to delete; the evidence trees
  on the same filesystem are not.

---

## 7. The danger this handoff names

**ECG 20 was warned that the governance layer generates its own work, and it did
it again, in the tooling built to prevent it.**

Watch the shape. §2 needed a search. A search needed to be checkable, so it
became a program. The program had a query-syntax bug, which produced a finding.
The program needed a citation checker, so one was written. The checker had a
surface-matching bug, which produced a second finding. Both findings are true,
both are in §9.5.5, and **§9.5.5 is now one instance longer because of tools
that exist only because §9.5.5 exists.**

That loop is real, productive, and infinite. The one thing that makes this
session different from the four before it is that **the section got written
anyway** — the tooling was in service of a manuscript file, not instead of one.

**The next session inherits the same test in a harder form.** §2 was the item
everyone deferred because it required contact with something outside the
repository. §4 is the item everyone defers because it is *only* writing, with
every source already on disk and nothing to discover. **There is now very little
in this repository that is incorrect, three drafted sections, and still no
manuscript.**
