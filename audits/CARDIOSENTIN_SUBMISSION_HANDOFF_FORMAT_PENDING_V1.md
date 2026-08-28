# CardioSentinel — submission handoff, format pending, V1

```
SCIENTIFIC WORK:      COMPLETE
MANUSCRIPT CONTENT:   FROZEN
RELATED WORK:         VERIFIED
CLAIM GUARD:          GREEN
CITATION VERIFIER:    GREEN
FORMAT COMPLIANCE:    UNDETERMINED
BLOCKER:              OFFICIAL TACTiCS 2026 AUTHOR INSTRUCTIONS / TEMPLATE
```

> ## ACTION REQUIRED FROM THE HUMAN OWNER
>
> **Obtain and provide the official TACTiCS 2026 author instructions and
> template. Do not infer submission formatting before they are received.**
>
> The questions to ask are already written out, in the order that unblocks the
> most work: `paper/TACTICS_OFFICIAL_INSTRUCTIONS_NEEDED.md`.

---

## 1. The frozen manuscript

**`paper/CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md`**

| | |
|---|---|
| `sha256` | `72a8d738ec41436d0335f4921ec8371fa2a53f90bf52acfbd59d09a350f3b1b2` |
| Total words | 14,415 |
| Body words (from §1) | 13,854 |
| Abstract | **279 words** |
| Figures | **5** (F1–F5); F6 deliberately not drawn |
| Tables | **4** (T1–T4) |
| Bibliography | **87 unique works** |
| Claim guard | **18 patterns · 17 occurrences · 0 genuine overclaims** |
| Citation verifier | **108 keys · 87 unique · 87 works · 0 unresolved** |

**One edit was made after the first freeze**, which is why the hash differs from
the `7833f6f0…` recorded earlier the same day. The Figures section named a
repository path (`paper/figures/`) that the 2026-08-28 reorganisation made
wrong, and that had no business in a submitted manuscript in any case. The
sentence now says the figures are supplied as vector PDF with PNG previews and
names no path. **No scientific prose, number, qualifier or limitation changed**;
both gates were re-run after the edit and are unchanged.

## 2. Housekeeping — all three closed

| | Item | Status |
|---|---|---|
| **A** | `PAPER_S9_DISCUSSION_DRAFT.md` misattributing `0.006683691656635168` / tolerance `0.02` to the ULP composition audit | **CLOSED.** Corrected to the real figures — physiology half bit-exact `0.000e+00` on 64/64 rows, embedding half within 6 ULP (max `7.15e-07`). The old pairing survives **only inside a dated correction note**, so the record shows the error and its repair rather than hiding either. No frozen report touched |
| **B** | Handbook claim-count statement vs the corrected all-occurrence guard | **CLOSED.** The old "twelve violations" does not reproduce and appears **zero** times in the manuscript. Handbook v1.5 measures **8 occurrences across 3 claims** — six boundary statements, two lexical collisions with the statistical sense of *diagnostic*, zero overclaims. The §4-draft figure of eight reproduced exactly and stands. The handbook itself never carried the count, so no handbook source changed and no DOCX re-render was required |
| **C** | Three literature venues lacking independent confirmation | **CLOSED, 3 of 3, zero conflicts.** `arxiv:2111.00396` → ICLR 2022 (iclr.cc programme, oral 6960 / poster 6959; OpenReview `uYLFoz1vlAC`). `arxiv:2601.14971` → ACM Web Conference 2026 (ACM DL, `doi:10.1145/3774904.3793005`). `arxiv:1907.01463` → ICLR 2019 Reproducibility in ML Workshop (OpenReview `HylgS2IpLN`), cited conservatively **as a workshop paper**. All nineteen venue claims are now two-source |

## 3. What is decided, and what the template decides

**Frozen — the template cannot change these.** Every scientific claim and its
qualifiers; all denominators; every limitation and the external-validity
disclosure; the negative findings; the categorical-generation example; the
one-authority/two-surfaces argument; the title; the 279-word abstract; the
keywords; which figures exist; which tables exist; the set of 87 works.

**Format-dependent — undecidable until the template arrives.**

| Decision | Why it waits |
|---|---|
| Page count | no limit, and no template to measure against |
| Whether any compression is needed | depends on the limit and on whether references count toward it |
| Figure width, and legibility at it | the PDFs are 5.78–7.20 in wide; a real column measure decides whether they survive reduction |
| **T2 and T4 orientation** | both are wide — T2 has seven columns including a long interval/denominator field, T4 four including quoted required wording. Under two columns both need restructuring |
| Reference formatting | style unknown; 87 works cannot be laid out |
| Section spacing and heading hierarchy | template-defined |
| Author block, anonymised or named | unknown, and it changes the title page |
| Appendix / supplement disposition | policy unknown; nothing is currently in an appendix |
| File type, page size, fonts, upload limit | all unknown |

## 4. Procedure when the template arrives

1. **Archive and hash the received template and instructions** into `docs/`, so
   the rules that governed the layout are themselves evidence.
2. Extract every authoritative requirement, with its source.
3. Compare against `audits/TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md`.
4. **Update only `NOT SPECIFIED` fields.** A field the instructions do not cover
   stays `NOT SPECIFIED`; it does not become a default.
5. Map the frozen manuscript into the template. **Content is not reopened.**
6. Apply template-aware compression **only if the verified page limit requires
   it**, following §5 below in order.
7. Render.
8. Inspect **every page**: page breaks, orphan headings, figure placement, table
   overflow, clipped text, reference wrapping, caption placement, page
   numbering, blank pages.
9. Re-run the claim guard on the rendered text.
10. Re-run the citation verifier.
11. Verify figures and tables at **actual publication size**, not full-screen.
12. Obtain the human metadata and approvals
    (`paper/TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md`).
13. Create the final submission artifact.

**No scientific analysis is reopened at any step.** If a step appears to require
it, the step is wrong.

## 5. Compression plan — PREPARED, NOT EXECUTED

**Nothing below has been cut.** Use only against a verified page limit, in
order, stopping as soon as the limit is met.

### SAFE — take these first

| # | Target | Approx. saving | Why safe |
|--:|---|--:|---|
| 1 | §2.1 detector-lineage enumeration | ~120 w | A list of adjacent systems; the positioning paragraph after it carries the argument |
| 2 | §2.2 self-supervised / state-space enumeration | ~90 w | Architectural lineage; §2.2's own positioning says the encoder is not the contribution |
| 3 | §2.5 grounded-generation enumeration | ~100 w | Three sub-lists; the positioning paragraph is what §8 needs |
| 4 | §3.1–§3.5 module prose duplicated by **F1** and **T1** | ~150 w | F1 is topology, T1 is adjudication; prose restating either is redundant |
| 5 | §10.5 cost paragraph detail (keep the ratio and the direction of travel) | ~120 w | The 22.5%/7.5% figures carry the argument; the line items illustrate it |
| 6 | Repeated governance definitions in §4.2 and §8.5 | ~80 w | The one-shot budget and the lexical limit are each stated twice |

**SAFE subtotal ≈ 660 words** with no claim, qualifier or denominator lost.

### MODERATE RISK — only if SAFE is not enough

| # | Target | Approx. saving | Risk |
|--:|---|--:|---|
| 7 | §4.1 `stable_id` allow-list/deny-list exposition | ~130 w | It is the cleanest concrete example of enforcement-in-code; losing it weakens Reviewer B's answer |
| 8 | §8.4's four-gate table → prose summary | ~150 w | The table is the answer to "cherry-picked?"; compressing it costs the strongest response to Reviewer C |
| 9 | §5.2 E12d and E13a detail → one sentence each | ~140 w | Reviewer A reads these as the paper's honesty; thinning them invites "why so brief about the nulls?" |
| 10 | §9 runtime prose | ~80 w | Already the shortest section at 310 words; further cuts make the physical half thin |

### DO NOT CUT

§11 in its entirety and the external-validity disclosure · every denominator ·
every mandatory qualifier ("at the promoted operating point", "in the single
evaluated context", "encoder-only", "laptop simulation", "not a failure rate")
· all negative findings and the two gates that returned no · the
categorical-generation example in §8.2 and its two qualifiers · the
one-authority/two-surfaces argument in §2.6 and §10.4 · Table T4 · the abstract's
scope paragraph.

**If the limit cannot be met without cutting protected material, that is a
finding to report, not a cut to make.** Move implementation detail to a
supplement if one is permitted; if not, say so.

## 6. Human input still required

Fourteen fields in `paper/TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md`:
author names and order, affiliations, emails, corresponding author,
organizational identifiers, co-author approvals, acknowledgements, funding,
conflicts, client attribution approval, internal publication approval, AI-use
disclosure, submission category, presenter. **None was invented.**

**One deserves the owner's attention rather than a form field.** Whether
TACTiCS requires an AI-assistance disclosure is unverified; whether one would
be materially true here is not. This manuscript was assembled with substantial
AI assistance, and the programme's record says so plainly. The wording is the
owner's; the fact is not.

## 7. A note on the repository move

`paper/` and `handoffs/` were moved under `docs/` on 2026-08-28. Git still shows
**35 tracked files as deleted at their old paths** with untracked copies at the
new ones, because the move was not staged. `git add -A docs/paper docs/handoffs`
plus staging the deletions will record it as a rename — **but this repository's
convention forbids `git add -A`**, so stage the specific paths. Nothing is lost;
content hashes are unchanged apart from the one documented edit in §1.
