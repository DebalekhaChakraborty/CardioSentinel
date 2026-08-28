# Literature Search, V1

**This document searches and reports. It authorizes no protocol change, no
experiment, no code change and no claim.** Its single purpose is to close the
one item `PAPER_OUTLINE_V2.md` has listed as blocking since V1: §2 cannot be
written, and its gap statement cannot honestly be asserted, until a search has
been attempted and recorded.

**The headline finding is negative for the manuscript and should be read
first.** §2's gap statement — *"none of them, as far as we are aware, ships the
machinery that makes the outcome checkable by a third party who does not trust
the authors"* — **does not survive this search and must not be written.** A 2026
position paper names the same problem, names it *experiment nonrepudiation*,
argues it is unsolved by checklists and code sharing, and ships a reference
implementation. §5 states what remains true after that, and it is narrower and
more defensible than what the outline planned to claim.

| | |
|---|---|
| Executed | 2026-08-25, 18:33:16–18:34:34 UTC |
| Machinery | `scripts/literature_search.py`, stdlib only, no new dependency |
| Record | `docs/LITERATURE_SEARCH_V1.json`, `payload_sha256 dd479319d4139875428d069b823f5ed39dc8489935dac0c1d941c0fd604a441f` |
| Sources | Crossref REST, arXiv API, NCBI E-utilities (PubMed) |
| Volume | **65 queries, 393 hits, 372 unique records, 0 request failures** |
| Data reaching disk | bibliographic metadata only; **no article text, no dataset** |

---

## 0. Why the search is a program and not a reading session

Every other claim in this repository is backed by an artifact a reader can open.
A literature search conducted by reading and remembering would have been the one
place that stopped being true, and it would have been the place where it mattered
most: **a fabricated citation is the same class of error the entire apparatus
exists to prevent**, and unlike a leaked threshold it leaves no trace in a run
directory.

So the queries are a fixed tuple in `scripts/literature_search.py`, the results
are whatever the three APIs returned, and each record carries the request URL and
the retrieval timestamp that produced it. **No record in the JSON was typed by an
author.** `literature_search.py verify` closes the loop from the other end: it
extracts every `[doi:…]`, `[arxiv:…]` and `[pmid:…]` key from a draft and fails
on any key the recorded search did not return, normalising arXiv version
suffixes on both sides and asserting no other equivalence. It currently reports
**61 citations, 0 unresolved** for `PAPER_S2_RELATED_WORK_DRAFT.md`.

That check is deliberately weaker than it looks and §7 says so.

---

## 1. What was searched

Four passes, each recorded under a `pass` field in the JSON, run in one
retrieval session so the whole record is internally consistent.

| Pass | Queries | Hits | What it asks |
|---|---|---|---|
| **1** | 22 | 161 | *As registered.* Topic queries for each of §2.1–§2.5. |
| **2** | 19 | 126 | The same literatures, after pass 1's arXiv syntax was found to be broken (§2). |
| **3** | 14 | 59 | **Presence tests** for named works the authors expected to exist (§3). |
| **4** | 10 | 47 | **Adversarial queries written to break the gap statement** (§5). |

Coverage by outline subsection: 2.1 — 47 hits, 2.2 — 62, 2.3 — 126, 2.4 — 77,
2.5 — 81. The weighting toward §2.3 is pass 4, and it is where the finding is.

---

## 2. The instrument failed before the literature did

**Pass 1 reported `22 queries, 161 hits, 0 failed`, and its arXiv half was
worthless.** Every pass-1 query was handed to arXiv as a natural-language phrase
scoped to `all:`, which the API scores loosely across the whole record. For
§2.3 the query *"preregistration machine learning research"* returned a survey of
learning curves, a reinforcement-learning library, and a fake-news benchmark. For
§2.4, *"selective classification risk coverage deep networks"* returned portfolio
tail-risk measurement and operational-loss severity distributions. **Not one hit
was on the subject the query named**, and nothing in the run said so.

The exception is instructive: *"learning to defer to an expert classification"*
returned the actual learning-to-defer literature, because that phrase happens to
match the titles. **The query that worked and the queries that failed are
indistinguishable from the run's output.**

Pass 2 re-ran the same literatures with field-scoped, quoted queries
(`ti:"selective classification"`, `abs:"electrocardiogram" AND
abs:"self-supervised"`). It first failed outright — 17 consecutive `HTTP 400`s,
because the harvester was still prefixing `all:` to a query that already named a
field — and that failure was visible, was fixed, and is the only part of this
episode that behaved correctly.

**The measurement that makes the point:**

| | Unique arXiv records |
|---|---|
| Pass 1 (`all:` + natural-language phrase) | 86 |
| Passes 2–4 (field-scoped, quoted) | 141 |
| **In both** | **0** |

Two searches of the same five literatures, on the same day, against the same
API, with **no record in common**. Pass 1 is retained in the registry and in the
JSON unedited, because deleting it would delete the evidence.

**This is the failure class `PAPER_S9_DISCUSSION_DRAFT.md` §9.5 is about, found
in the act of writing §2.** `0 failed` measured reachability of the arXiv
endpoint. It was read as coverage of the arXiv corpus. Nothing in the harness
could tell the difference, and no assertion in this repository would have caught
it — the check passed for a reason unrelated to what it claimed to verify. It is
the seventh instance of that pattern and it is recorded in §8 for §9.5.

---

## 3. Presence tests, and the two that failed

Pass 3 asks a different question from passes 1 and 2 — not *what does this
literature contain* but *is this specific work really there, and what does its
metadata actually say*. **A search that only returns what you already knew is
not a search**, so these are segregated in the record and §2 of the draft marks
which citations came from them.

Ten of twelve resolved on the first authority. Two did not, and both outcomes
stand as recorded:

- **The European ST-T Database reference paper is not retrievable from Crossref
  by a bibliographic query that names it.** `"European ST-T Database evaluation
  of algorithms ST segment analysis"` returned eight items, none of them the
  1992 paper. It resolved against PubMed as `pmid:1396824` — Taddei, Distante,
  Emdin *et al.*, *European Heart Journal*, 1992. The cohort audited in
  `CROSS_DATASET_PROVENANCE.md` is discoverable in one index and not the other.
- **El-Yaniv & Wiener's 2010 *JMLR* paper did not resolve at all**, on either of
  two Crossref queries. The same authors' 2015 *JAIR* paper did
  (`doi:10.1613/jair.4439`). **The draft cites what resolved and does not cite
  what did not**, which is the whole reason the presence tests are run
  separately.

**Twenty-three Crossref records carry no publication year**, including three
IEEE *Computers in Cardiology* proceedings the draft cites. Where the year is
recoverable from the container title (*"Computers in Cardiology 1995"*) the
draft uses it and says so here; it is not inferred anywhere else.

---

## 4. What the five literatures actually contain

Compressed. The draft in `PAPER_S2_RELATED_WORK_DRAFT.md` carries the
positioning; this is the census.

**§2.1 — ST-episode detection.** A small, coherent, largely closed literature,
concentrated in one group and its collaborators. The database this project
trains on is itself the subject of `pmid:12691437`; the detector lineage runs
from `doi:10.1109/cic.1995.482762` and `doi:10.1109/cic.1996.542628` through
`doi:10.1109/cic.2002.1166774`, `pmid:15191074` and `doi:10.1186/1475-925x-10-107`,
with the ischemic/heart-rate-related discrimination problem treated directly in
`doi:10.1109/cic.2008.4749058` and `pmid:20130344`. **The universe being small
is consistent with `EXTERNAL_VALIDATION_STRATEGY_V1.md`'s finding and is
independent evidence for it.**

**§2.2 — deep learning for ambulatory ECG.** Large, active, and pointed almost
entirely at 12-lead resting or short-strip diagnosis rather than long ambulatory
streams (`arxiv:2001.01550`, `arxiv:2409.07975`). Self-supervised ECG
representation learning is a well-populated subfield
(`arxiv:2203.06889`, `arxiv:2106.04452`, `arxiv:2007.04871`). The encoder's
architectural lineage resolves cleanly to `arxiv:2111.00396`,
`arxiv:2203.14343` and `arxiv:2206.11893`.

**§2.3 — reproducibility, pre-registration, result-blind analysis.** The
largest of the five and the one that matters. Three distinct traditions, and
they are not the same tradition: *documentation* (`arxiv:1810.03993`,
`arxiv:1803.09010`, `doi:10.1136/bmj.q824`), *empirical study of whether
documentation works* (`arxiv:2306.09562`, `arxiv:2003.12206`,
`doi:10.1016/j.patter.2023.100804`), and *machinery* — which is pass 4 and §5.
Result-blind analysis has a mature literature outside ML, in nuclear and
particle physics (`doi:10.1146/annurev.nucl.55.090704.151521`,
`doi:10.1088/0954-3899/28/10/312`), and pre-registration for predictive
modelling has been proposed as a lightweight template (`arxiv:2311.18807`).

**§2.4 — selective prediction, calibration, deferral.** Deep, formal, and
continuous from `doi:10.1109/tit.1970.1054406` to the present
(`arxiv:1705.08500`, `arxiv:1901.09192`, `arxiv:2208.12084`, `arxiv:2206.09034`),
with calibration (`arxiv:1706.04599`, `arxiv:2106.07998`) and learning-to-defer
(`arxiv:2006.01862`, `arxiv:2202.03673`, `arxiv:2310.14774`) beside it.
**A census point the paper should make carefully:** across the 77 hits in this
subsection, the abstracts describe methods that improve a risk-coverage curve or
a deferral rule. The search surfaced **no** paper reporting that a selective
mechanism was built, evaluated against a prespecified gate, and abandoned. That
is an observation about what this search returned, not a claim about the field,
and §9.3 must state it that way.

**§2.5 — grounded generation and guardrails.** The newest and fastest-moving.
Grounding in retrieved documents (`arxiv:2005.11401`, `arxiv:2305.06983`,
`arxiv:2401.15884`), measurement of whether output is supported
(`arxiv:2112.12870`, `arxiv:2005.00661`, `arxiv:2202.03629`,
`arxiv:2501.03200`), and programmable output rails (`arxiv:2310.10501`,
`arxiv:2504.00441`). **`arxiv:2504.00441` is the one to read against §4.6:** it
measures the security/usability trade-off across industrial guardrails and finds
no free lunch — which is the honest frame for this system's deterministic
fallback.

---

## 5. The gap statement, attacked

Pass 4 exists because a gap statement that was never attacked is a claim about
the authors' reading, not about the literature. Ten queries were written to find
exactly the thing §2 said does not exist. **They found it.**

| Found | What it does |
|---|---|
| `arxiv:2605.08586` | Names the problem **experiment nonrepudiation**: binding the numbers in a paper to an executed computation the author cannot later alter or deny. Argues checklists, optional code sharing and author-controlled logging do not answer *"did the code the paper describes produce the numbers the paper reports?"* Ships **K-Veritas**, a reference implementation. |
| `arxiv:2601.14971` | **FG-Trac** — sample-level lifecycle traceability across an ML pipeline, anchored to tamper-evident cryptographic commitments. |
| `arxiv:2605.19755` | **AIBOM** — a CycloneDX extension for model lineage and environment provenance, with automated reproducibility auditing. |
| `doi:10.1016/j.procs.2011.04.061`, `doi:10.1016/j.procs.2012.04.047` | Executable papers: code and data bound into the publication object. Fifteen years old. |
| `doi:10.3233/apc200107`, `doi:10.1186/s13059-021-02299-x` | Whole Tale, Code Ocean — platforms that make a published computation re-runnable by a stranger. |
| `arxiv:2501.03200` | A leaderboard with a **private split**, so a reported score does not depend on trusting the reporter. |

**`arxiv:2605.08586` is the closest neighbour this manuscript has, and it states
the paper's motivating problem more sharply than the outline does.** It was
published in May 2026. §2's *"as far as we are aware"* would have been written
in ignorance of it.

**It also is not this paper**, and the difference is the only positioning claim
§2 is now entitled to make:

- **Those systems attest to the computation. This one enforces the claim.**
  K-Veritas signs a report; FG-Trac proves a sample was used; AIBOM records what
  the environment was. None of them reads a sentence and refuses it because the
  evidence does not support it. `enforce()` and the numeric, categorical and
  lexical gates operate on **the natural-language claim**, which is the object a
  reader actually consumes.
- **One artifact governs two surfaces.** The claim boundary that binds the
  manuscript is the same code that binds the runtime's generated explanation.
  Nothing in pass 4 does both, because nothing in pass 4 has a second surface.
- **Attestation records what happened; this apparatus also produces evidence of
  what did not.** A zero-capability counter written by a run is a different kind
  of artifact from a signed hash of a run that occurred.
- **Scope.** `arxiv:2605.08586` proposes a conference-level protocol and calls
  for a standard. This is a single project's machinery, applied at authoring
  time, reported with the cost it imposed (§9.6). Those are complements, and §2
  should say so rather than compete.

**What the section must now say, in place of the gap statement:** the problem is
real, it has been independently named, and the neighbouring work binds *numbers,
data and environments*. **The claim itself — the sentence a reader takes away —
is the artifact none of this literature binds, and it is where this work sits.**

---

## 6. What this search did not do

Stated so that a reader can discount the section correctly rather than trust it.

- **It read metadata, not papers.** Titles, authors, venues, years, and — for the
  eleven works in §5 and the load-bearing citations — abstracts, fetched from the
  arXiv API. **No full text was retrieved for any work**, so every positioning
  claim in the draft is a claim about what an abstract says.
- **Eight hits per query, ranked by the provider's relevance.** Geifman &
  El-Yaniv 2017 did not appear in the top eight of `ti:"selective
  classification"` and had to be found by a presence test. **Anything the
  authors did not think to name may be absent and the record cannot show it.**
- **Three indices, not five.** No Scopus, no Web of Science, no ACM DL, no IEEE
  Xplore beyond what Crossref carries, no Google Scholar. Conference proceedings
  in ML are covered only where Crossref or arXiv carries them.
- **English-language, and title/abstract matching only.** No citation-graph
  expansion, no forward or backward snowballing — which is the standard next
  step, is not automated here, and is the most valuable thing a subsequent
  session could add.
- **`verify` is weak on purpose and must not be oversold.** It proves a cited
  identifier was returned by a recorded query. **It does not check that the work
  says what the draft says it says**, and no program in this repository can. The
  guarantee is against a citation appearing from nowhere; it is not a guarantee
  against misreading.

---

## 7. Provenance of one citation, stated because it is an exception

`arxiv:2605.08586` was first seen in a general web search run while scoping this
document, **before** any registered query existed, and was then resolved by a
registered presence test (`ti:"Nonrepudiable Experimental Results"`, pass 4)
against the arXiv API. Its metadata in the record came from arXiv like every
other entry.

**It is recorded here because the honest version of §5 is uncomfortable:** the
single work that refutes the manuscript's sharpest claim was not found by any
topic query in passes 1–3, and would not have been found by pass 1 at all. The
adversarial pass found it because it was told what to look for by something
outside the protocol.

---

## 8. For §9.5 — the seventh instance

`PAPER_S9_DISCUSSION_DRAFT.md` §9.5 argues from cases where a check passed or
failed for a reason unrelated to what it claimed to verify. **This search
produced another one, and it is the first that occurred while writing the paper
rather than while building the system.**

`22 queries, 161 hits, 0 failed` is a true statement about HTTP. It was read as a
statement about literature coverage. The two are unrelated, the run could not
distinguish them, and the zero-overlap measurement in §2 is how far apart they
turned out to be. **The instance is worth §9.5's space precisely because the
apparatus that caught it was a human reading eight titles and finding them
absurd** — not a gate, not a test, and not anything this repository could have
automated.

**And then the checker built for this document did it too, within the hour.**
`verify`'s first run over the §2 draft reported **38 of 61 citations
unresolved**. Every one was an arXiv key whose only difference from a harvested
record was a trailing version suffix: the draft cited `arxiv:2005.11401`, the
record held `arxiv:2005.11401v4`. **The tool built to catch invented citations
reported thirty-eight invented citations, and there were none.** It was
comparing surface forms and calling the difference a provenance failure — which
is §5.6 finding 4 exactly, in a new costume: *an identifier matched against a
surface form is a bug waiting for a version suffix.*

**The fix went in the checker, not the draft.** Rewriting sixty-one citations to
carry version suffixes would have made the tool quiet and the manuscript worse,
and it is the same move §9.5.3 names as a governance failure. The normalisation
is declared in `literature_search.py`, applies to both sides of the comparison,
and is the only equivalence the checker asserts.

---

## 9. What follows

1. **§2 is unblocked and is drafted** in `PAPER_S2_RELATED_WORK_DRAFT.md`. Its
   gap statement is §5's, not the outline's.
2. **§9.3 is unblocked.** `PAPER_S9_DISCUSSION_DRAFT.md` §9.3 was stubbed
   pending this search. §4's §2.4 census is what it was waiting for, and its
   bound is stated there: *the search returned no such paper*, which is not the
   same as *no such paper exists*.
3. **`PAPER_OUTLINE_V2.md` §2 is now wrong on its own terms** — it instructs the
   author to write a gap statement this search refutes. The outline is not
   edited here; §2's draft supersedes it and says so.
4. **Snowballing is the obvious next step and is not done.** Backward citations
   from `arxiv:2605.08586` and forward citations from
   `doi:10.1016/j.patter.2023.100804` are where a further neighbour would be, if
   one exists.
