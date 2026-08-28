# TACTiCS 2026 submission requirements — verification attempt, V1

**Run 2026-08-28. Outcome: NO OFFICIAL RULE COULD BE VERIFIED.**

This document records what was searched, what was found, and what remains
`NOT SPECIFIED`. **No requirement below was inferred.** Where a rule could not
be established from an authoritative source it is recorded as unknown, not
guessed, per the governing instruction.

---

## 1. What was searched

### 1.1 The repository first

`git grep` over `docs/`, `paper/`, `README.md` and the handbooks for a call for
papers, author instructions, template, portal instructions or preserved
organizer communication.

**Result: none exists.** Every occurrence of the string `tactics` in this
repository refers to **the Python virtual environment and its parent
directory** — `/home/AI_POC/tactics/…`, "the frozen `tactics` interpreter
(Python 3.12.6, 335 packages)", "never install, upgrade or downgrade anything
in `tactics`". There is no conference artifact of any kind in the repository.

### 1.2 The open web

| # | Query | Outcome |
|--:|---|---|
| 1 | TACTiCS 2026 conference call for papers submission | No matching venue. Results were *Tech Tactics in Education* (an unrelated education-technology event), ACM SIGOPS ATC 2026, and generic CFP aggregators |
| 2 | TACTiCS conference "Intelligent Physical Systems" call for papers | No matching venue. Results were ICCPS, IntelliSys, IEEE SMC listings — none named TACTiCS |
| 3 | TCS TACTiCS Technical Architects Conference 2026 paper submission guidelines | No matching venue. Results were TCC (Theory of Cryptography), TACAS (ETAPS), ATC — acronym neighbours, not this conference |

**Three independent searches returned no authoritative TACTiCS 2026 source:
no call for papers, no author instructions, no template, no portal
instructions.**

### 1.3 The most probable explanation, stated as a hypothesis and not used as a rule

The manuscript's own drafting criteria have consistently required it to be
"readable by a technical-architect audience", which is consistent with an
**internal corporate technical-architects conference** rather than a public
academic venue. An internal conference's rules live behind an organisation's
intranet and would not be indexed publicly, which would explain all three
negative searches.

**This hypothesis changes nothing.** It is not evidence, it produces no rule,
and no formatting decision below rests on it. It is recorded only so that the
next person knows where to look: **ask the organisers, or retrieve the internal
call for papers.**

---

## 2. Rule status

Every row is `NOT SPECIFIED`. None was inferred, and none may be treated as a
default by a later session.

| Requirement | Status | Source |
|---|---|---|
| Paper / page limit | **NOT SPECIFIED** | — |
| Whether references count toward the limit | **NOT SPECIFIED** | — |
| Abstract word limit | **NOT SPECIFIED** | — |
| Title restrictions | **NOT SPECIFIED** | — |
| Paper size (A4 / Letter) | **NOT SPECIFIED** | — |
| Column format (single / double) | **NOT SPECIFIED** | — |
| Font family and size | **NOT SPECIFIED** | — |
| Heading hierarchy | **NOT SPECIFIED** | — |
| Author / affiliation format | **NOT SPECIFIED** | — |
| Anonymous vs named submission | **NOT SPECIFIED** | — |
| Figure requirements | **NOT SPECIFIED** | — |
| Table requirements | **NOT SPECIFIED** | — |
| Reference style | **NOT SPECIFIED** | — |
| Appendix / supplement policy | **NOT SPECIFIED** | — |
| Allowed file type | **NOT SPECIFIED** | — |
| Maximum file size | **NOT SPECIFIED** | — |
| Mandatory declaration sections | **NOT SPECIFIED** | — |
| AI-use disclosure requirement | **NOT SPECIFIED** | — |
| Conflict-of-interest requirement | **NOT SPECIFIED** | — |
| Plagiarism / originality declaration | **NOT SPECIFIED** | — |
| Submission deadline | **NOT SPECIFIED** | — |
| Presentation requirements | **NOT SPECIFIED** | — |

**VERIFIED OFFICIAL RULES: zero.**

---

## 3. What this blocks, and what it does not

**Blocked — cannot be performed without a template:**

- format-pressure audit against a real page limit (§2 of the task brief);
- abstract length compliance (the 279-word abstract cannot be judged compliant
  or non-compliant);
- title-length compliance;
- figure sizing at final column width;
- table layout under a real font and column measure;
- reference formatting in the required style;
- page count, page breaks, orphan headings, figure placement, bibliography
  wrapping — every check that requires a rendered page;
- production of a template-conformant submission file.

**Not blocked — completed in full and reported separately:** venue
verification, the discussion-draft correction, the handbook claim recount, the
bibliography content audit, intrinsic figure inspection, table content audit,
three reviewer simulations, the rejection pass, contribution coherence, the
claim-guard pass, the red-line pass, the internal-material scrub, the language
pass, and the metadata inventory.

---

## 4. What a human must supply

1. **The official TACTiCS 2026 call for papers or author instructions** — the
   single blocking item.
2. The template, in an editable format, if one is mandated.
3. The submission portal's own constraints, which sometimes differ from the CFP.

Until item 1 exists, the manuscript can be scientifically final and cannot be
format-final, and this document is the reason.
