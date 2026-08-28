# CardioSentinel — submission-format and final reviewer gate, V1

**Run 2026-08-28. Editorial, bibliographic and formatting only.** No experiment
was run, no metric computed, no sealed TEST reopened, no frozen report altered,
no result strengthened, no limitation weakened, no novelty claim added.

**Headline: the manuscript is scientifically final and cannot be made
format-final, because no official TACTiCS 2026 rule could be verified.**

---

## 1. Official rules and sources

**Zero verified rules.** Full record in
`audits/TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md`.

The repository contains no call for papers, author instructions, template or
organizer communication. Every occurrence of `tactics` in this repository is
**the Python virtual environment** (`/home/AI_POC/tactics/…`, "the frozen
`tactics` interpreter, Python 3.12.6, 335 packages"). Three independent web
searches — for the conference by name, by theme, and as a technical-architects
conference — returned only acronym neighbours (Tech Tactics in Education, TACC,
TACAS, TCC, ATC). **All twenty-two requirements are `NOT SPECIFIED`, and none
was inferred.**

A plausible explanation is an internal corporate conference whose rules sit
behind an intranet. That is a hypothesis, it is recorded as one, and **no
formatting decision rests on it.**

## 2. Format compliance

**Undeterminable.** Page limit, column format, fonts, reference style, figure
sizing and abstract limit are all unknown. Compliance cannot be asserted or
denied. **No template was fabricated**; the candidate is labelled
FORMAT-PENDING.

## 3. Size, reported against no constraint

| | |
|---|--:|
| Total words (candidate incl. metadata block) | 14,413 |
| Manuscript body words (from §1) | 13,852 |
| Abstract | **279** |
| Unique bibliographic works | **87** |
| Figures | **5** (F1–F5) |
| Tables | **4** (T1–T4) |
| Appendix / supplement | none |

**The 279-word abstract is neither compliant nor non-compliant** — there is no
verified limit to compare it against, and it was not shortened for aesthetics.

## 4. Venue cleanup — CLOSED, 3 of 3

| work | claimed | authoritative evidence | result |
|---|---|---|:--:|
| `arxiv:2111.00396` | ICLR 2022 | **iclr.cc official programme**: oral 6960 and poster 6959; OpenReview forum `uYLFoz1vlAC` | **confirmed** |
| `arxiv:2601.14971` | WWW 2026 | **ACM Digital Library**, `doi:10.1145/3774904.3793005`, Proceedings of the ACM Web Conference 2026 | **confirmed** |
| `arxiv:1907.01463` | RML@ICLR 2019 | **OpenReview workshop record** `HylgS2IpLN`; ICLR 2019 Reproducibility in ML Workshop | **confirmed (workshop)** |

**All nineteen venue assignments are now independently confirmed, zero
conflicts.** `arxiv:2601.14971` gained a publisher DOI; the citation key was
**not** changed to it, because that DOI is in no registered harvest and the
swap would make §2 unverifiable to buy cosmetic consistency. The DOI belongs in
the bibliography entry.

## 5. Discussion-draft correction

`paper/PAPER_S9_DISCUSSION_DRAFT.md` §9.6 attributed
`0.006683691656635168` against tolerance `0.02` to the ULP composition audit.
**Those numbers are the U1 calibration-agreement guard's**, reached by
copy-paste from the router material above it. Corrected at source to the real
figures — physiology half bit-exact at `0.000e+00` on 64 of 64 rows, embedding
half within **6 ULP** of float32 (max `7.15e-07`, median 2.5 ULP) — with a dated
correction note retained in place rather than a silent edit.

**No frozen report was touched, and the manuscript never carried the error**:
§3.6 was written from `paper/figures/README.md` and has always been correct.

## 6. Handbook claim recount — the old figure does not reproduce

The manuscript asserted, from the §4 source draft, that the guard reports
**"twelve violations, every one a quotation"** over the programme's governance
prose. That figure was produced by the **old first-match guard** over an
unrecorded subset of sections, and it does not reproduce.

Measured now with the corrected all-occurrence guard:

| text | occurrences | distinct claims |
|---|--:|--:|
| Handbook **v1.5** (current) | **8** | 3 |
| Handbook v1.4 (superseded) | 61 | 17 |
| §4 source draft | **8** | 8 |

Handbook v1.5's eight, classified: **six boundary statements** the handbook
makes in order to prohibit what they name ("Never claim medical or diagnostic
performance"; "does not claim … Any medical or diagnostic performance";
"Diagnostic/clinical performance | NO"; RQ1's own question text; "Declined: EDB
external validation" ×2) and **two lexical collisions** with the *statistical*
sense of "diagnostic". **Zero genuine overclaims.**

**The handbook itself never stated the count**, so the statements corrected were
the manuscript's two, at §4.6 and §8.5. They now carry the reproducible figure
with its scope and guard version. The §4-draft figure of **eight** is unchanged
and was independently reproduced. **No handbook source changed, so no DOCX
re-render was required.**

## 7. Bibliography

Content audited; **style cannot be produced** without a verified reference
style. Authority unchanged and re-verified on the submission candidate:

```
108 citation keys found · 87 unique keys · 87 unique bibliographic works · 0 unresolved
```

Every key resolves against `LITERATURE_SEARCH_V1.json` ∪
`LITERATURE_SEARCH_V2.json`. 73 `VERIFIED — PRIMARY`, 14 `PREPRINT — VERIFIED`;
all nineteen venue claims two-source. No duplicate work appears under two
identifiers except `doi:10.1016/j.patter.2023.100804` and `arxiv:2207.07048`,
which are **deliberately cited together** as the peer-reviewed and preprint
versions of one work. No DOI substitution was forced.

## 8. Figure audit — all five inspected as rendered images

| | result |
|---|---|
| **F1** | four layers legible, no clipping, no label collision; ULP audit values correct (`0.000e+00` on 64/64, `7.15e-07` = 6 ULP) |
| **F2** | carries the nesting the prose cannot — a consumed population inside a still-usable partition; status words present, not colour alone |
| **F3** | **seven zero-scoring subjects plotted at zero**, coincident markers drawn as an orange square with the blue circle nested inside; `s2059` visible as the one subject where the comparator scores higher; reference-episode counts beside each id; panel (b) shows 0.1921 [0.0505, 0.3455] and says "one operating point" in its own title |
| **F4** | **outer-train 0/158 vs held-out 3/79** distinction explicit; all **three negative streams** marked by diamond and labelled (`s20021:1`, `s20101:1`, `s20171:0`) |
| **F5** | three quality gates PASS (1.000 / 0 / 1.000), fourth gate **REFUSED** with mode → `DETERMINISTIC`; **G4 and G5 BLOCKED** stated; both mandatory qualifiers drawn into the figure — one evaluated context, and "a demonstrated failure mode — not a failure rate" |

Every series carries a marker shape as well as a colour, and every status
carries a word as well as a colour, so all five survive greyscale.

**What could not be checked: legibility at final column width.** The PNGs are
5.78–7.20 in wide at 200 dpi. Whether they survive reduction to a real column
measure is unknowable without the template. **F6 remains NOT REQUIRED.**

## 9. Table audit

T1–T4 audited for content: denominators present, bounded/fragile labels intact,
negative outcomes intact, no prose duplication introduced. **T2 row 9 now
carries both P1-B denominators** (473,897 windows / 12 subjects pooled; 9
contributing subjects subject-macro) and the recorded FPR caveat.

**Column overflow cannot be assessed.** T2 and T4 are wide — T2 has seven
columns including a long interval/denominator field, T4 has four with quoted
required wording. Under a two-column layout both would need restructuring
(likely T2 split by result family, T4 rotated to a two-column form). **That
restructuring is not attempted here**, because doing it against a guessed
measure would be work to be redone.

## 10. Reviewer simulation

### Reviewer A — ML / methods

| | |
|---|---|
| **Major** | absolute encoder performance is weak (AUPRC 0.0935 at prevalence 0.0461); several experiments inconclusive; one corpus; post-hoc mechanism analysis; no external validation |
| **Where answered** | §1 states plainly that headline predictive numbers are weak; §5.1 gives the four mandatory qualifiers; §5.2 reports E11 Category C and E12d/E13a Decision D as nulls; §10.3 explains why a consumed budget closes a branch; §11 leads on external validity |
| **Residual vulnerability** | a reviewer who reads only §5.1 may still take the paper as a failed classifier paper. The framing depends on §1 and §10.1 being read first |
| **Editorial change needed** | **No.** §5 already opens by handing off from §4 ("the machinery now has to pay for itself") |

### Reviewer B — systems / IPS

| | |
|---|---|
| **Major** | is this an IPS or a documentation exercise? is governance in the runtime or only in prose? is 61× meaningful? |
| **Where answered** | §3.6 proves composition rather than asserting it (bit-exact physiology half, 6 ULP embedding half, one implementation of each decision rule, 555 M2 tests); §9 reports gate admission **0 of 1,079** — a runtime behaviour, not a document; §2.7 places the six-stage chain |
| **Residual vulnerability** | §9 is the shortest section (310 words) and carries the "physical" half of the claim. It is bounded correctly but thin |
| **Editorial change needed** | **No** — §9's brevity is why F6 was refused; adding a figure to pad it would be the wrong fix |

### Reviewer C — trustworthy / agentic AI

| | |
|---|---|
| **Major** | novelty vs prior governance systems; the guard is lexical; Qwen is n=1; is the refusal example cherry-picked?; is negative-result governance oversold? |
| **Where answered** | §2.6 concedes both halves as precedented and cites the prior art (`2603.10742` assess-once, `2509.06902` renderer-side claim verification) before claiming only the coupling; §8.5 states the lexical limit and that 4 of 5 catches were quotations; §8.2 states n=1 twice and model-dependence; §8.4 answers cherry-picking directly — four gates, each earned by a *different* real failure; §10.2 says explicitly that the value of the negatives "is not modesty" |
| **Residual vulnerability** | "one authority, two surfaces" rests on a qualified negative over a targeted search of 97 queries. A reviewer who knows an unindexed system spanning both could refute it |
| **Editorial change needed** | **No.** The hedge is present and load-bearing, and §10 states the claim does not depend on either 2026 preprint's own priority |

## 11. Strongest rejection argument, and the response

> **Reject.** The paper reports a monitoring system whose predictive performance
> is poor — pooled AUPRC 0.0935 at prevalence 0.0461 on a single-use encoder-only
> evaluation — and whose component investigations are mostly null: the
> morphology intervention returned three intervals all containing zero, the
> replication study observed no outer outcome, the geometry study reproduced one
> of two assessable streams, the temporal-arm contrast spans zero, and the
> memory component has no interval at all. The one affirmative result, +0.1921,
> is a comparison against a hand-built memoryless rule at a single operating
> point that the authors chose, with seven of twelve subjects scoring zero.
> Evaluation is confined to one corpus, external validation was declined
> permanently, and there is no edge hardware.
>
> The claimed contribution is therefore not empirical but architectural — and
> the architecture's own Related Work concedes that call-time partition
> enforcement, assess-once semantics, holdout governance, cryptographic
> provenance and renderer-side claim verification all exist in prior work. What
> remains is that the authors connected two existing halves in one codebase.
> That is engineering integration, not a research result, and it is supported by
> a single generative example on one context with two models — an anecdote from
> which no rate, no distribution and no generalisation can be drawn. A governance
> framework that cannot be shown to reduce any measurable harm, evaluated on a
> corpus that cannot be externally checked, is a description of a build.

**Response, from evidence already in V3, and one concession.**

- *"Poor predictive performance"* — **category B, disclosed limitation.** §1,
  §5.1, §11 and §12 all say so; the paper never claims otherwise, and §5.1's
  value is its provenance, not its size.
- *"Mostly null investigations"* — **category B.** Each null is reported as a
  null with its interval, and §10.2 argues they make the retentions credible
  rather than reframing them as successes.
- *"Single operating point, seven zeros"* — **category B.** The qualifier is
  mandatory and undroppable, §6.3 gives the failure distribution in two opposing
  classes, and F3 plots the zeros rather than dropping them.
- *"No external validation, no edge hardware"* — **category B.**
- *"Both halves precedented"* — **conceded in §2.6 before the reviewer raises
  it**, with the prior art cited. The claim is only the coupling, hedged.
- *"Engineering integration, not research"* — **category C, framing.** This is
  the one that can be argued rather than conceded, and the argument is §8.2:
  the coupling produced a **finding** — a generation that passed every
  registered quality metric and was still wrong about the fact that mattered.
  Fidelity, completeness and claim-violation counting cannot see categorical
  state; only checking against the governed evidence can. That is a property of
  the coupling, not of either half, and it is not an integration detail.
- *"n = 1 anecdote"* — **category B for the refusal, category C for the
  architecture.** §8.4's four gates were each earned by a *different* real
  failure, so the architectural argument is not n = 1 even though the headline
  refusal is.

**Nothing in the rejection is category A (fatal), and nothing is category D.**
Every empirical criticism is already disclosed in the manuscript in the
reviewer's own terms.

## 12. Contribution coherence

C1–C4 appear in the abstract, §1.1, §10 and §12, in the same form and the same
order. **No contribution appears first in the conclusion.** The title carries
C1 and C4 only — deliberately, since a title carrying four contributions would
be unreadable — and every surface describes the same set.

## 13. Claim guard — final

**18 patterns · 17 occurrences · 0 genuine overclaims.**

- **Authorized quotations and boundary statements: 14.** Eight are §4.6's
  enumeration of the phrases the guard catches; six are boundary statements
  ("reports no diagnostic capability", "None of that is a diagnostic
  capability", "not autonomous diagnosis", and the three added by §6's
  correction, which name the *statistical* sense of "diagnostic" in order to
  classify it).
- **Lexical false positives: 3.** Two in §2 describing the *literature's*
  diagnostic setting; one in §11 reporting that external validation was
  **declined**.
- **Genuine overclaims: 0. Unresolved: 0.**

The count rose from 15 to 17 because §6's correction had to name the collision
it was describing — the §4.6 recursion reproducing on the sentence that
documents it.

## 14. Red-line pass — ALL CLEAR

All fourteen prohibited implications absent. One automated flag,
`later checkpoint … better`, was inspected and is **two negations**: §5.2's
"says nothing about whether a later checkpoint would have scored better" and
Table T4's `**never** "a later checkpoint is better"`. A false positive of the
audit's own regex — the same lexical class the paper is about.

## 15. Human metadata still required

Author names and order · affiliations · corresponding author and email ·
anonymous-vs-named decision · acknowledgements · funding · conflicts of
interest · organisational approval to publish · AI-use disclosure ·
originality declaration. **All ten are explicit placeholders in the candidate.
None was invented.**

## 16. Internal-material scrub — CLEAN

No filesystem paths, PR numbers, handoff identifiers, TODO notes, assistant
instructions, task prompts, "the user requested" phrasing, or internal
organisational names. One hex string survives — `ce037309cc…206c3`, the
prospective split digest in §4.5 — and it is **scientifically necessary
provenance**, which the brief protects. The assembly-provenance appendix was
removed at V2 and lives separately.

## 17–18. Artifacts

- `paper/CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md`
- **No PDF was produced.** Rendering requires a template; producing one against
  a guessed layout would fabricate the thing §1 refuses to fabricate.

## 19. Remaining blockers

1. **No verified TACTiCS 2026 call for papers, author instructions or
   template.** Blocking, and only a human can clear it.
2. **No rendered artifact, therefore no page-level visual inspection.** Page
   breaks, orphan headings, figure placement, table overflow, reference
   wrapping and page numbering are all unchecked, and the brief forbids
   declaring readiness from source files alone.
3. **Ten author-metadata fields** await human completion.
4. **T2 and T4 will need restructuring** if the venue turns out to be
   two-column.

None is scientific. All four are format or human-input blockers.
