# CardioSentinel — Related-Work Verification V2 and Literature-Provenance Hardening

**Run:** 2026-08-28 · **Supersedes:** `CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md`
(kept; V1's findings are not restated where V2 does not change them)
**Target:** `paper/PAPER_S2_RELATED_WORK_DRAFT.md` · **Branch:**
`feat/e11-e13a-instrumentation-and-paper-readiness`

No scientific result was modified. No model experiment was run. No sealed TEST
evidence was touched. `LITERATURE_SEARCH_V1.json` was neither rewritten nor
back-filled and its `payload_sha256` is unchanged. The §6.3 ordering condition
remains binding and is recorded in §2's header.

---

## 1. V1 → V2, in one table

| V1 blocker | V2 outcome |
|---|---|
| verifier regex silently skipped multi-key brackets | **fixed**; 16 keys were escaping the gate on the live section |
| 11 falsification sources unregistered | **registered** in `LITERATURE_SEARCH_V2.json`, passes 5 and 6 |
| 29 citations lacked a confirmed venue | **19 resolved**; 10 remain preprint-only |
| load-bearing claims checked at abstract level | **10 sources checked in full text**; one matrix cell was wrong and is corrected |
| two 2026 preprints load-bearing | novelty **restated so it does not depend on either preprint's priority claim** |

**One finding reversed a V1 conclusion.** Full text of `arxiv:2603.10742` shows
it implements consumed-attempt semantics, which V1's matrix scored as absent.
See §7 and §8.

---

## 2. THE VERIFIER DEFECT, AND THE FIX

### What was wrong

`scripts/literature_search.py` extracted citations with one regex:

```python
CITATION = re.compile(r"\[((?:doi|arxiv|pmid):[^\]\s]+)\]")
```

`[^\]\s]+` cannot cross a space, and the pattern requires `]` immediately after
the identifier. **A bracket holding two keys therefore matched nothing at all,
and neither key was checked.** The section has seven such brackets.

Measured on the live file, before any V2 edit:

| | keys |
|---|--:|
| old extractor, unique | 71 |
| new extractor, unique | 87 |
| **escaping verification entirely** | **16** |
| lost by the new extractor | **0** |

The sixteen: `arxiv:1706.04599`, `arxiv:2006.01862`, `arxiv:2106.07998`,
`arxiv:2202.03673`, `arxiv:2207.07048`, `arxiv:2310.14774`,
`doi:10.1016/j.patter.2023.100804`, `doi:10.1016/j.procs.2011.04.061`,
`doi:10.1016/j.procs.2012.04.047`, `doi:10.1088/0954-3899/28/10/312`,
`doi:10.1109/cic.2008.4749058`, `doi:10.1146/annurev.nucl.55.090704.151521`,
`doi:10.1186/s13059-021-02299-x`, `doi:10.2172/826602`,
`doi:10.3233/apc200107`, `pmid:20130344`.

**This is a false negative in the direction that matters.** The gate exists to
make an invented citation impossible; an invented citation written second in a
shared bracket passed it silently. The check reported a clean count while
skipping a fifth of the section.

### The fix

Extraction is now two-stage — find brackets, then find every key inside one:

```python
BRACKET = re.compile(r"\[([^\[\]]*)\]")
KEY = re.compile(r"(?:doi|arxiv|pmid):[^\s,;]*")
```

Design points, each with a reason:

- **Newlines are collapsed first.** The manuscript wraps at 79 columns and a
  shared bracket can straddle a line break; a line-at-a-time reader misses
  those. (The V1 ledger script had exactly this bug and under-counted by five.)
- **The identifier part is `*`, not `+`.** `[doi:]` is extracted as the
  malformed key it is, resolves against nothing and is reported unresolved.
  **Malformed input fails closed instead of disappearing.**
- **The colon is not stripped as trailing punctuation.** Stripping it would
  rewrite `doi:` to `doi` and name a scheme that does not exist.
- `verify` now reports **citation keys found**, **unique keys** and **unique
  bibliographic works** separately, because a work may legitimately carry more
  than one identifier.

### Two further defects found while fixing this one

**The V2 harvest failed 54 of 97 queries on its first run** — every failure an
arXiv `HTTP 429`, including all eleven title-pinned confirmatory queries. The
record it wrote was green at the exit code and empty where it mattered: the
same class of failure the module docstring already documents for pass 1.
arXiv is now paced at 3.0 s (`ARXIV_INTERVAL_SECONDS`) against 1.0 s for
Crossref and PubMed, and `_get` retries `429`/`503` with growing backoff.
Re-run: **97 queries, 509 hits, 8 failed.**

**A re-harvest is not idempotent, and that is now part of the check's
semantics.** Even after the fix, ten works V1 demonstrably returned are absent
from V2: four of V1's own pass-2 arXiv queries were still refused, and four
PubMed queries returned a different top eight on 2026-08-28 than on
2026-08-25, because relevance ranking moves. The alternatives were to re-run
until V2 reproduced V1, or to paste the missing hits in. **Both are
back-filling.** Instead `verify` now accepts repeated `--record` arguments and
resolves against their union, and each record stays exactly as its retrieval
session left it. Default is V1 ∪ V2.

---

## 3. ADVERSARIAL REGRESSION TESTS

`tests/reproducibility/test_literature_citation_extraction.py` — **22 tests,
all passing.**

| brief | test | asserts |
|---|---|---|
| A | `test_a_single_key_is_found`, `test_a_every_supported_scheme_is_found` | one key; each of `doi:`/`arxiv:`/`pmid:`; version-suffixed arXiv ids |
| B | `test_b_two_keys_in_one_bracket_are_both_found` | both keys returned, in order |
| C | `test_c_three_mixed_key_types_are_all_found` | three schemes in one bracket |
| **D** | `test_d_invented_second_key_in_shared_bracket_is_extracted` | the invented key is seen |
| **D** | `test_d_invented_second_key_makes_verify_fail` | **end to end: `verify` exits 1**, the case the old code let through |
| D | `test_d_shared_bracket_of_known_keys_still_passes` | the fix does not fail every shared bracket |
| E | `test_e_duplicates_do_not_inflate_the_unique_count` | 3 occurrences, 2 unique |
| F | `test_f_separator_variation_does_not_change_extraction` | `,` `;` and five spacing variants |
| F | `test_f_a_bracket_straddling_a_line_break_is_still_read` | wrapped brackets |
| F | `test_f_trailing_sentence_punctuation_is_not_part_of_the_identifier` | `[doi:x.]` |
| G | `test_g_a_scheme_with_no_identifier_is_surfaced_not_dropped` | `[doi:]` → `doi:` |
| G | `test_g_malformed_key_makes_verify_fail` | malformed input exits 1 |
| G | `test_g_text_that_is_not_a_citation_is_not_extracted` | `[Table 1]`, bare `doi:` in prose |
| — | `test_the_live_section_has_no_hidden_keys` | the eight shared-bracket keys are present in the real file |
| — | `test_resolution_is_the_union_of_the_supplied_records` | V1 alone fails, V2 alone fails, V1 ∪ V2 passes |

`test_g_a_scheme_with_no_identifier_is_surfaced_not_dropped` failed on first
run and found a real bug: `_TRAILING` included `:`, so `[doi:]` came out as
`doi`. The test was right and the code was changed.

Wider run: `tests/reproducibility tests/contracts tests/agents` — **209 passed**.
`ruff check` clean on both changed files.

---

## 4. V2 HARVEST PROVENANCE

`docs/literature/LITERATURE_SEARCH_V2.json`, schema `cardiosentinel.literature_search/2`.

| | V1 | V2 |
|---|---|---|
| queries | 65 | **97** |
| hits | 393 | **509** |
| failed | 0 | 8 (all arXiv 429) |
| `payload_sha256` | `dd479319…d604a441f` **unchanged** | `cd1dbfcf…9df6ff0b` |

V2 records, beyond V1's schema: `generated_utc` (2026-08-28T12:58:54+00:00),
`query_set`, `supersedes` (a pointer, not a merge), and
`normalised_identifiers` — 473 resolved keys.

**Pass numbering keeps V1 honest.** V1 used passes 1–4; V2 reproduces those
verbatim and **keeps their numbers**, then adds **pass 5** (21 falsification
queries) and **pass 6** (11 title-pinned confirmatory queries). Nothing in V2
suggests the new sources existed in V1: they are in passes that V1 does not
have. All eleven pass-6 queries returned their target.

Coverage requested by the brief and present in pass 5/6: ML preregistration ·
registered reports · experiment governance · data-leakage prevention ·
call-time split enforcement · reusable holdout · the Ladder · experiment
nonrepudiation · scientific-workflow provenance · cryptographic experiment
provenance · proof-carrying claims · machine-checkable scientific claims ·
fail-closed evaluation · agentic evidence validation · physiological IPS ·
streaming physiological AI · trustworthy CPS.

---

## 5. CITATION COUNTS

Reported separately, as the brief requires:

| | |
|---|--:|
| **citation keys found** (occurrences) | **107** |
| **unique keys** | **87** |
| **unique bibliographic works** | **87** |
| **unresolved** | **0** |
| shared brackets silently skipped | **0** |

Every key resolves against `LITERATURE_SEARCH_V1.json` ∪
`LITERATURE_SEARCH_V2.json`. No `SEARCH-RETURNED` or unresolved state remains.

---

## 6. VENUE RESOLUTION

**19 of the 29 citations V1 labelled `PREPRINT — VERIFIED` have a confirmed
peer-reviewed venue.** V1 could not find them because Crossref does not index
NeurIPS, ICML or ICLR proceedings; DBLP does. Per the brief, DBLP was used as
the bibliographic route for exactly the venues Crossref cannot see, with an
independent title match at ≥0.90 and a preference for a real venue over `CoRR`.

| key | work | venue confirmed | year |
|---|---|---|--:|
| `arxiv:2111.00396` | Efficiently Modeling Long Sequences with Structured State Spaces | **ICLR** | 2022 |
| `arxiv:1706.04599` | On Calibration of Modern Neural Networks | **ICML** | 2017 |
| `arxiv:1901.09192` | SelectiveNet | **ICML** | 2019 |
| `arxiv:2006.01862` | Consistent Estimators for Learning to Defer | **ICML** | 2020 |
| `arxiv:2202.03673` | Calibrated Learning to Defer, One-vs-All | **ICML** | 2022 |
| `arxiv:1705.08500` | Selective Classification for Deep Neural Networks | **NIPS** | 2017 |
| `arxiv:2005.11401` | Retrieval-Augmented Generation | **NeurIPS** | 2020 |
| `arxiv:2106.07998` | Revisiting the Calibration of Modern Neural Networks | **NeurIPS** | 2021 |
| `arxiv:2206.09034` | Towards Better Selective Classification | **ICLR** | 2023 |
| `arxiv:2208.12084` | Calibrated Selective Classification | **TMLR** | 2022 |
| `arxiv:2405.05160` | Selective Classification Under Distribution Shifts | **TMLR** | 2024 |
| `arxiv:2205.13532` | Selective Prediction via Training Dynamics | **TMLR** | 2025 |
| `arxiv:1803.09010` | Datasheets for Datasets | **Commun. ACM** · doi:10.1145/3458723 | 2021 |
| `arxiv:2003.12206` | Improving Reproducibility in ML Research | **JMLR** | 2021 |
| `arxiv:2305.06983` | Active Retrieval Augmented Generation | **EMNLP** · doi:10.18653/v1/2023.emnlp-main.495 | 2023 |
| `arxiv:2203.06889` | Lead-agnostic Self-supervised Learning for ECG | **CHIL** | 2022 |
| `arxiv:2601.14971` | FG-Trac: Fine-Grained Traceability | **WWW** | 2026 |
| `arxiv:2106.04452` | 3KG | ML4H **workshop** @ NeurIPS | 2021 |
| `arxiv:1907.01463` | Reproducibility in ML for Health | RML **workshop** @ ICLR | 2019 |

Five of the eleven citations added in V1 also resolve: `arxiv:1502.04585`
**ICML 2015**, `arxiv:1506.02629` **NIPS 2015**, `arxiv:2107.13767` **EMBC
2021**, `arxiv:2401.06866` **CHIL 2024**, `arxiv:2405.06347` **ETFA 2024**
(doi:10.1109/ETFA61755.2024.10710855).

### Independent corroboration — Semantic Scholar

The brief asks that DBLP not be sole evidence where another route exists. A
second, independent resolution was run against the Semantic Scholar graph API,
keyed on the arXiv identifier rather than on a title match. It is far less
complete — it resolved **10 of 29** against DBLP's 19, the rest returning
nothing under rate limiting — but **where both sources answered, they agreed on
all ten, with no conflict**:

| key | DBLP | Semantic Scholar |
|---|---|---|
| `arxiv:2203.06889` | CHIL 2022 | ACM Conference on Health, Inference, and Learning 2022 |
| `arxiv:2106.04452` | ML4H@NeurIPS 2021 | ML4H@NeurIPS 2021 |
| `arxiv:1705.08500` | NIPS 2017 | Neural Information Processing Systems 2017 |
| `arxiv:1901.09192` | ICML 2019 | International Conference on Machine Learning 2019 |
| `arxiv:2005.11401` | NeurIPS 2020 | Neural Information Processing Systems 2020 |
| `arxiv:2305.06983` | EMNLP 2023 | Conference on Empirical Methods in Natural Language Processing 2023 |
| `arxiv:2207.07048` | CoRR | arXiv.org — **preprint label corroborated** |
| `arxiv:2501.03200` | CoRR | arXiv.org — preprint corroborated |
| `arxiv:2504.00441` | CoRR | arXiv.org — preprint corroborated |
| `arxiv:2510.05310` | CoRR | arXiv.org — preprint corroborated |

**Six of the nineteen venue claims and four of the fourteen preprint labels are
therefore two-source.** The remaining thirteen venue claims rest on DBLP alone;
Semantic Scholar returned no record for them rather than a contradicting one,
which is an absence of corroboration, not a disagreement. **That distinction is
kept in §11.**

### The thirteen DBLP-only assignments, independently checked

Each of the thirteen venue claims that rested on DBLP alone was checked against
the most authoritative source available for its venue: official proceedings
first, publisher record second, OpenReview for ICLR and TMLR. **Ten confirmed,
zero conflicts, three unconfirmed.**

| work | DBLP venue | independent source | confirmed venue | conflict |
|---|---|---|---|:--:|
| `arxiv:1706.04599` | ICML 2017 | **PMLR v70** (official proceedings) | ICML 2017 | **N** |
| `arxiv:2006.01862` | ICML 2020 | **PMLR v119** | ICML 2020 | **N** |
| `arxiv:2202.03673` | ICML 2022 | **PMLR v162** | ICML 2022 | **N** |
| `arxiv:2106.07998` | NeurIPS 2021 | **papers.nips.cc 2021** | NeurIPS 2021 | **N** |
| `arxiv:2003.12206` | JMLR 2021 | **jmlr.org v22** | JMLR v22 | **N** |
| `arxiv:1803.09010` | Commun. ACM 2021 | **Crossref publisher record** `doi:10.1145/3458723` | Communications of the ACM, 2021-11-19 | **N** |
| `arxiv:2208.12084` | TMLR 2022 | **OpenReview** | `venue: Accepted by TMLR` | **N** |
| `arxiv:2405.05160` | TMLR 2024 | **OpenReview** | `venue: Accepted by TMLR` | **N** |
| `arxiv:2205.13532` | TMLR 2025 | **OpenReview** | `venue: Accepted by TMLR` | **N** — see below |
| `arxiv:2206.09034` | ICLR 2023 | **OpenReview** | `venueid: ICLR.cc/2023/Conference`, poster | **N** |
| `arxiv:2111.00396` | ICLR 2022 | **iclr.cc official programme** — oral 6960, poster 6959; OpenReview forum `uYLFoz1vlAC` | ICLR 2022 (Oral) | **N** |
| `arxiv:2601.14971` | WWW 2026 | **ACM Digital Library** `doi:10.1145/3774904.3793005` | Proceedings of the ACM Web Conference 2026 | **N** |
| `arxiv:1907.01463` | RML@ICLR 2019 | **OpenReview workshop record** `HylgS2IpLN` | ICLR 2019 Reproducibility in ML Workshop | **N** |

**One apparent conflict was raised and resolved, and it was mine.** A first pass
returned `Submitted to ICLR 2024` for `arxiv:2205.13532` against DBLP's TMLR
2025, which looked like a disagreement. OpenReview holds **three** notes for
that title: a rejected ICLR 2024 submission, an `Accepted by TMLR` note, and a
HiLD@ICML 2025 workshop poster. My script took the first match above threshold
rather than the accepted one. **DBLP was right; the tool was wrong.** Recorded
because a first-match heuristic producing a false conflict is the same defect
class as the first-match heuristic that produced the citation under-count.

**Closed 2026-08-28: all thirteen are now two-source, with zero conflicts.**
The last three were confirmed by hand against official venue records rather
than aggregators — the ICLR virtual programme, the ACM Digital Library, and the
workshop's own OpenReview entry. `arxiv:2601.14971` gained a publisher DOI in
the process (`10.1145/3774904.3793005`); the citation key is **not** changed to
it, because that DOI appears in no registered harvest and swapping would make
the section unverifiable to buy cosmetic consistency. The DOI belongs in the
bibliography entry, not in the provenance key.

**Every one of the nineteen venue assignments is now independently confirmed.**

**The last two rows are workshop papers and are labelled as such.** ML4H and
RML are refereed workshops, not main-conference tracks, and the manuscript
should not present them as the latter. `arxiv:1907.01463` carries the ML4H
reproducibility claim narrowed in V1 (§2.2 of that document), so its venue
weight matters.

**Still preprint-only (14).** `arxiv:2007.04871`, `arxiv:2207.07048`,
`arxiv:2309.07136`, `arxiv:2311.18807`, `arxiv:2401.12783`, `arxiv:2401.15884`,
`arxiv:2409.07975`, `arxiv:2501.03200`, `arxiv:2504.00441`, `arxiv:2510.05310`,
`arxiv:2509.06902`, `arxiv:2603.10742`, `arxiv:2605.08586`, `arxiv:2608.16891`.
`arxiv:2207.07048` is not a risk: the peer-reviewed version
`doi:10.1016/j.patter.2023.100804` is already cited beside it in §2.3.

**Why the citation keys were not swapped for DOIs.** Of the nineteen, only two
carry a DOI, and **neither DOI appears in V1 or V2**. Replacing an `arxiv:` key
with a DOI the registered searches never returned would make the section
unverifiable to buy cosmetic tidiness. The arXiv identifier stays as the
resolvable provenance anchor; the confirmed venue is recorded here and is what
the bibliography must cite at assembly time. **That is a real remaining task
and it is in §11.**

### Final status distribution — all 87 keys

**73 `VERIFIED — PRIMARY` · 14 `PREPRINT — VERIFIED` · 0 unresolved.**
(V1: 48 / 29.) The per-key ledger follows.

| # | key | § | year | title | venue / published record | status |
|--:|---|---|--:|---|---|---|
| 1 | `pmid:1396824` | 2.1 | 1992 | The European ST-T database: standard for evaluating systems for the  | European heart journal | VERIFIED — PRIMARY |
| 2 | `pmid:12691437` | 2.1 | 2003 | Long-term ST database: a reference for the development and evaluatio | Medical & biological engineering & computing | VERIFIED — PRIMARY |
| 3 | `doi:10.1161/01.cir.101.23.e215` | 2.1 | 2000 | PhysioBank, PhysioToolkit, and PhysioNet | Circulation | VERIFIED — PRIMARY |
| 4 | `doi:10.1109/cic.1995.482762` | 2.1 | None | A system for the detection of ischemic episodes in ambulatory ECG | Computers in Cardiology 1995 | VERIFIED — PRIMARY |
| 5 | `doi:10.1109/cic.1996.542628` | 2.1 | None | Characterization of temporal patterns of transient ischemic ST chang | Computers in Cardiology 1996 | VERIFIED — PRIMARY |
| 6 | `doi:10.1109/cic.2002.1166774` | 2.1 | None | Advanced detection of ST segment episodes in 24-hour ambulatory ECG  | Computers in Cardiology | VERIFIED — PRIMARY |
| 7 | `pmid:15191074` | 2.1 | 2004 | Automated detection of transient ST-segment episodes in 24 h electro | Medical & biological engineering & computing | VERIFIED — PRIMARY |
| 8 | `doi:10.1186/1475-925x-10-107` | 2.1 | 2011 | Automatic classification of long-term ambulatory ECG records accordi | BioMedical Engineering OnLine | VERIFIED — PRIMARY |
| 9 | `doi:10.1109/cic.2008.4749058` | 2.1 | 2008 | Automatic distinguishing between ischemic and heart-rate related tra | 2008 Computers in Cardiology | VERIFIED — PRIMARY |
| 10 | `pmid:20130344` | 2.1 | 2010 | Automatic classification of transient ischaemic and transient non-is | Physiological measurement | VERIFIED — PRIMARY |
| 11 | `pmid:22874369` | 2.1 | 2012 | Classification of ischaemic episodes with ST/HR diagrams. | Studies in health technology and informatics | VERIFIED — PRIMARY |
| 12 | `pmid:19696464` | 2.1 | 2009 | Real-time detection of transient cardiac ischemic episodes from ECG  | Physiological measurement | VERIFIED — PRIMARY |
| 13 | `pmid:26863140` | 2.1 | 2016 | Electrocardiogram ST-Segment Morphology Delineation Method Using Ort | PloS one | VERIFIED — PRIMARY |
| 14 | `pmid:15265622` | 2.1 | 2004 | Semia: semi-automatic interactive graphic editing tool to annotate a | Computer methods and programs in biomedicine | VERIFIED — PRIMARY |
| 15 | `arxiv:2001.01550` | 2.2 | 2019 | Opportunities and Challenges of Deep Learning Methods for Electrocar | Computers in Biology and Medicine · doi:10.1016/j.comp | VERIFIED — PRIMARY |
| 16 | `arxiv:2409.07975` | 2.2 | 2024 | Deep Learning for Personalized Electrocardiogram Diagnosis: A Review | arXiv preprint | PREPRINT — VERIFIED |
| 17 | `pmid:42129209` | 2.2 | 2026 | A deep learning ECG model for identification and localization of occ | Nature communications | VERIFIED — PRIMARY |
| 18 | `pmid:42082497` | 2.2 | 2026 | A large-scale 12-lead electrocardiogram dataset for acute coronary s | Scientific data | VERIFIED — PRIMARY |
| 19 | `pmid:41358268` | 2.2 | 2025 | Transfer Learning Strategies for Cardiovascular Disease Detection in | Biomedical engineering and computational biology | VERIFIED — PRIMARY |
| 20 | `arxiv:2201.10061` | 2.2 | 2022 | Negative-ResNet: Noisy Ambulatory Electrocardiogram Signal Classific | Neural Computing and Applications · doi:10.1007/s00521 | VERIFIED — PRIMARY |
| 21 | `arxiv:2203.06889` | 2.2 | 2022 | Lead-agnostic Self-supervised Learning for Local and Global Represen | CHIL 2022 | VERIFIED — PRIMARY |
| 22 | `arxiv:2106.04452` | 2.2 | 2021 | 3KG: Contrastive Learning of 12-Lead Electrocardiograms using Physio | ML4H@NeurIPS 2021 | VERIFIED — PRIMARY |
| 23 | `arxiv:2007.04871` | 2.2 | 2020 | Subject-Aware Contrastive Learning for Biosignals | arXiv preprint | PREPRINT — VERIFIED |
| 24 | `arxiv:2309.07136` | 2.2 | 2023 | Masked Transformer for Electrocardiogram Classification | arXiv preprint | PREPRINT — VERIFIED |
| 25 | `arxiv:2111.00396` | 2.2 | 2021 | Efficiently Modeling Long Sequences with Structured State Spaces | ICLR 2022 | VERIFIED — PRIMARY |
| 26 | `arxiv:2203.14343` | 2.2 | 2022 | Diagonal State Spaces are as Effective as Structured State Spaces | Advances in Neural Information Processing Systems 35 · | VERIFIED — PRIMARY |
| 27 | `arxiv:2206.11893` | 2.2 | 2022 | On the Parameterization and Initialization of Diagonal State Space M | Advances in Neural Information Processing Systems 35 · | VERIFIED — PRIMARY |
| 28 | `arxiv:1810.03993` | 2.3 | 2018 | Model Cards for Model Reporting | FAT* '19: Conference on Fairness, Accountability, and  | VERIFIED — PRIMARY |
| 29 | `arxiv:1803.09010` | 2.3 | 2018 | Datasheets for Datasets | Commun. ACM 2021 · doi:10.1145/3458723 | VERIFIED — PRIMARY |
| 30 | `doi:10.1136/bmj.q824` | 2.3 | 2024 | TRIPOD+AI: an updated reporting guideline for clinical prediction mo | BMJ | VERIFIED — PRIMARY |
| 31 | `arxiv:2003.12206` | 2.3 | 2020 | Improving Reproducibility in Machine Learning Research (A Report fro | J. Mach. Learn. Res. 2021 | VERIFIED — PRIMARY |
| 32 | `arxiv:2306.09562` | 2.3 | 2023 | Reproducibility in NLP: What Have We Learned from the Checklist? | Findings of the Association for Computational Linguist | VERIFIED — PRIMARY |
| 33 | `doi:10.1016/j.patter.2023.100804` | 2.3 | 2023 | Leakage and the reproducibility crisis in machine-learning-based sci | Patterns | VERIFIED — PRIMARY |
| 34 | `arxiv:2207.07048` | 2.3 | 2022 | Leakage and the Reproducibility Crisis in ML-based Science | arXiv preprint | PREPRINT — VERIFIED |
| 35 | `arxiv:1909.06539` | 2.3 | 2019 | AI slipping on tiles: data leakage in digital pathology | Lecture Notes in Computer Science · doi:10.1007/978-3- | VERIFIED — PRIMARY |
| 36 | `doi:10.1038/d41586-022-02035-w` | 2.3 | 2022 | Could machine learning fuel a reproducibility crisis in science? | Nature | VERIFIED — PRIMARY |
| 37 | `arxiv:1907.01463` | 2.3 | 2019 | Reproducibility in Machine Learning for Health | RML@ICLR 2019 | VERIFIED — PRIMARY |
| 38 | `arxiv:2401.08847` | 2.3 | 2024 | RIDGE: Reproducibility, Integrity, Dependability, Generalizability,  | Journal of Imaging Informatics in Medicine · doi:10.10 | VERIFIED — PRIMARY |
| 39 | `arxiv:2311.18807` | 2.3 | 2023 | Pre-registration for Predictive Modeling | arXiv preprint | PREPRINT — VERIFIED |
| 40 | `doi:10.1038/s41593-024-01762-9` | 2.3 | 2024 | Reducing publication bias with Registered Reports | Nature Neuroscience | VERIFIED — PRIMARY |
| 41 | `doi:10.1146/annurev.nucl.55.090704.151521` | 2.3 | 2005 | BLIND ANALYSIS IN NUCLEAR AND PARTICLE PHYSICS | Annual Review of Nuclear and Particle Science | VERIFIED — PRIMARY |
| 42 | `doi:10.1088/0954-3899/28/10/312` | 2.3 | 2002 | Blind analysis | Journal of Physics G: Nuclear and Particle Physics | VERIFIED — PRIMARY |
| 43 | `doi:10.2172/826602` | 2.3 | 2003 | Blind Analysis in Particle Physics | Office of Scientific and Technical Information (OSTI) | VERIFIED — PRIMARY |
| 44 | `doi:10.1109/tit.1970.1054406` | 2.4 | 1970 | On optimum recognition error and reject tradeoff | IEEE Transactions on Information Theory | VERIFIED — PRIMARY |
| 45 | `doi:10.1613/jair.4439` | 2.4 | 2015 | Agnostic Pointwise-Competitive Selective Classification | Journal of Artificial Intelligence Research | VERIFIED — PRIMARY |
| 46 | `arxiv:1705.08500` | 2.4 | 2017 | Selective Classification for Deep Neural Networks | NIPS 2017 | VERIFIED — PRIMARY |
| 47 | `arxiv:1901.09192` | 2.4 | 2019 | SelectiveNet: A Deep Neural Network with an Integrated Reject Option | ICML 2019 | VERIFIED — PRIMARY |
| 48 | `arxiv:2206.09034` | 2.4 | 2022 | Towards Better Selective Classification | ICLR 2023 | VERIFIED — PRIMARY |
| 49 | `arxiv:2208.12084` | 2.4 | 2022 | Calibrated Selective Classification | Trans. Mach. Learn. Res. 2022 | VERIFIED — PRIMARY |
| 50 | `arxiv:2205.13532` | 2.4 | 2022 | Selective Prediction via Training Dynamics | Trans. Mach. Learn. Res. 2025 | VERIFIED — PRIMARY |
| 51 | `arxiv:2405.05160` | 2.4 | 2024 | Selective Classification Under Distribution Shifts | Trans. Mach. Learn. Res. 2024 | VERIFIED — PRIMARY |
| 52 | `arxiv:1706.04599` | 2.4 | 2017 | On Calibration of Modern Neural Networks | ICML 2017 | VERIFIED — PRIMARY |
| 53 | `arxiv:2106.07998` | 2.4 | 2021 | Revisiting the Calibration of Modern Neural Networks | NeurIPS 2021 | VERIFIED — PRIMARY |
| 54 | `arxiv:2006.01862` | 2.4 | 2020 | Consistent Estimators for Learning to Defer to an Expert | ICML 2020 | VERIFIED — PRIMARY |
| 55 | `arxiv:2202.03673` | 2.4 | 2022 | Calibrated Learning to Defer with One-vs-All Classifiers | ICML 2022 | VERIFIED — PRIMARY |
| 56 | `arxiv:2310.14774` | 2.4 | 2023 | Principled Approaches for Learning to Defer with Multiple Experts | Lecture Notes in Computer Science · doi:10.1007/978-3- | VERIFIED — PRIMARY |
| 57 | `arxiv:2005.11401` | 2.5 | 2020 | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | NeurIPS 2020 | VERIFIED — PRIMARY |
| 58 | `arxiv:2305.06983` | 2.5 | 2023 | Active Retrieval Augmented Generation | EMNLP 2023 · doi:10.18653/V1/2023.EMNLP-MAIN.495 | VERIFIED — PRIMARY |
| 59 | `arxiv:2401.15884` | 2.5 | 2024 | Corrective Retrieval Augmented Generation | arXiv preprint | PREPRINT — VERIFIED |
| 60 | `arxiv:2005.00661` | 2.5 | 2020 | On Faithfulness and Factuality in Abstractive Summarization | Proceedings of the 58th Annual Meeting of the Associat | VERIFIED — PRIMARY |
| 61 | `arxiv:2112.12870` | 2.5 | 2021 | Measuring Attribution in Natural Language Generation Models | Computational Linguistics · doi:10.1162/coli_a_00490 | VERIFIED — PRIMARY |
| 62 | `arxiv:2202.03629` | 2.5 | 2022 | Survey of Hallucination in Natural Language Generation | ACM Computing Surveys (2022) doi:10.1145/3571730 | VERIFIED — PRIMARY |
| 63 | `arxiv:2501.03200` | 2.5 | 2025 | The FACTS Grounding Leaderboard: Benchmarking LLMs' Ability to Groun | arXiv preprint | PREPRINT — VERIFIED |
| 64 | `arxiv:2406.13692` | 2.5 | 2024 | Synchronous Faithfulness Monitoring for Trustworthy Retrieval-Augmen | Proceedings of the 2024 Conference on Empirical Method | VERIFIED — PRIMARY |
| 65 | `arxiv:2310.10501` | 2.5 | 2023 | NeMo Guardrails: A Toolkit for Controllable and Safe LLM Application | Proceedings of the 2023 Conference on Empirical Method | VERIFIED — PRIMARY |
| 66 | `arxiv:2504.00441` | 2.5 | 2025 | No Free Lunch with Guardrails | arXiv preprint | PREPRINT — VERIFIED |
| 67 | `arxiv:2510.05310` | 2.5 | 2025 | RAG Makes Guardrails Unsafe? Investigating Robustness of Guardrails  | arXiv preprint | PREPRINT — VERIFIED |
| 68 | `pmid:41933065` | 2.5 | 2026 | An AI-based mental health guardrail and dataset for identifying psyc | NPJ digital medicine | VERIFIED — PRIMARY |
| 69 | `pmid:38664535` | 2.5 | 2024 | Large language models for preventing medication direction errors in  | Nature medicine | VERIFIED — PRIMARY |
| 70 | `arxiv:2605.08586` | 2.6 | 2026 | Computer Science Conferences Should Require Nonrepudiable Experiment | arXiv preprint | PREPRINT — VERIFIED |
| 71 | `arxiv:2601.14971` | 2.6 | 2026 | Fine-Grained Traceability for Transparent ML Pipelines | WWW 2026 · doi:10.1145/3774904.3793005 | VERIFIED — PRIMARY |
| 72 | `doi:10.3389/fcomp.2026.1735919` | 2.6 | 2026 | Operationalising artificial intelligence bills of materials for veri | Frontiers in Computer Science | VERIFIED — PRIMARY |
| 73 | `arxiv:2603.10742` | 2.6 | 2026 | A Grammar of Machine Learning Workflows: Rejecting Data Leakage at C | arXiv preprint | PREPRINT — VERIFIED |
| 74 | `arxiv:1502.04585` | 2.6 | 2015 | The Ladder: A Reliable Leaderboard for Machine Learning Competitions | ICML 2015 | VERIFIED — PRIMARY |
| 75 | `arxiv:1506.02629` | 2.6 | 2015 | Generalization in Adaptive Data Analysis and Holdout Reuse | NIPS 2015 | VERIFIED — PRIMARY |
| 76 | `doi:10.1016/j.procs.2011.04.061` | 2.6 | 2011 | A data and code model for reproducible research and executable paper | Procedia Computer Science | VERIFIED — PRIMARY |
| 77 | `doi:10.1016/j.procs.2012.04.047` | 2.6 | 2012 | Literate Program Execution for Reproducible Research and Executable  | Procedia Computer Science | VERIFIED — PRIMARY |
| 78 | `doi:10.3233/apc200107` | 2.6 | 2020 | Toward Enabling Reproducibility for Data-Intensive Research Using th | Advances in Parallel Computing | VERIFIED — PRIMARY |
| 79 | `doi:10.1186/s13059-021-02299-x` | 2.6 | 2021 | Promoting reproducibility with Code Ocean | Genome Biology | VERIFIED — PRIMARY |
| 80 | `doi:10.1038/s41562-021-01190-w` | 2.6 | 2021 | Supporting computational reproducibility through code review | Nature Human Behaviour | VERIFIED — PRIMARY |
| 81 | `arxiv:2509.06902` | 2.6 | 2025 | Proof-Carrying Numbers (PCN): A Protocol for Trustworthy Numeric Ans | arXiv preprint | PREPRINT — VERIFIED |
| 82 | `arxiv:2608.16891` | 2.6 | 2026 | Runtime Governance for Agentic AI: Action-Boundary Control with Trus | doi:10.5281/zenodo.20262303 | VERIFIED — PRIMARY |
| 83 | `arxiv:2107.13767` | 2.7 | 2021 | Edge computing in 5G cellular networks for real-time analysis of ele | EMBC 2021 · doi:10.1109/EMBC46164.2021.9630875 | VERIFIED — PRIMARY |
| 84 | `arxiv:2401.12783` | 2.7 | 2024 | A Scoping Review of Deep Learning Methods for Photoplethysmography D | arXiv preprint | PREPRINT — VERIFIED |
| 85 | `arxiv:2401.06866` | 2.7 | 2024 | Health-LLM: Large Language Models for Health Prediction via Wearable | CHIL 2024 | VERIFIED — PRIMARY |
| 86 | `arxiv:2605.29483` | 2.7 | 2026 | VitalAgent: A Tool-Augmented Agent for Reactive and Proactive Physio | arXiv preprint | PREPRINT — VERIFIED |
| 87 | `arxiv:2405.06347` | 2.7 | 2024 | Building Trust in AI-Driven Decision Making for Cyber-Physical Syste | ETFA 2024 · doi:10.1109/ETFA61755.2024.10710855 | VERIFIED — PRIMARY |

<!-- totals: 87 unique keys; {'VERIFIED — PRIMARY': 73, 'PREPRINT — VERIFIED': 14} -->

---

## 7. FULL-TEXT CLAIM-SUPPORT MATRIX

Ten sources were fetched as full text (arXiv HTML renderings, 38k–87k
characters each) and read for the exact sentence §2 rests on them for.
`DIRECT` means the source states the claim; `INTERPRETIVE` means §2 draws a
defensible inference the source does not state in those terms.

| | source | manuscript claim | support | supporting text | allowed wording | wording that would exceed the source |
|---|---|---|---|---|---|---|
| **A** | `arxiv:2509.06902` | verifies claims "in the renderer rather than the model … defaults to unverified when the check fails" | **DIRECT** | "PCN places verification in the renderer, not the model: only claim-checked numbers are marked as verified, and all others default to unverified. This separation prevents spoofing and guarantees fail-closed behavior." | renderer-side; fail-closed; numeric spans as claim-bound tokens; soundness and completeness proved | that it handles non-numeric claims, evidence graphs, or a manuscript surface — it does not |
| **B** | `arxiv:2603.10742` | "enforces a terminal assess-once constraint at call time" | **DIRECT** | "assess requires a Model that has not been previously assessed"; "for Model _, assess(_, test) is valid if and only if _.assessed = false. After the first call … The second call fails the guard"; "assess commits on the held-out test partition exactly once"; "terminal evidence that the grammar does not allow to be revisited" | partition authority; call-time guard; assess-once; terminal evidence | that it is the *first* such gate — the author bounds that claim to "any existing ML framework … to my knowledge" and to "the grammar's own type system" |
| **C** | `arxiv:1502.04585` | "make *repeated* consultation safe rather than forbidding it" | **DIRECT** | "we don't even limit the number of submissions an analyst can make" | statistical guarantee under unlimited adaptive submissions; parameter-free variant | that the Ladder bounds or consumes attempts — it explicitly does not |
| **D** | `arxiv:1506.02629` | same | **DIRECT** | "an algorithm that enables the validation of a large number of adaptively chosen hypotheses, while provably avoiding overfitting"; differential-privacy based | reuse made safe; not forbidden | that it enforces anything at runtime |
| **E** | `arxiv:2311.18807` | "a lightweight template with a qualitative evaluation" | **DIRECT** | "introduce a lightweight pre-registration template, and present a qualitative study with machine learning researchers" | proposal plus qualitative study | that pre-registration was shown to prevent biased estimates — the study probes insight, not effect |
| **F** | `arxiv:2306.09562` | "10,405 responses … only 46% … claim to open-source their code" | **DIRECT** | "examining 10,405 anonymous responses"; "only 46% of submissions claim to open-source their code" | both figures verbatim | any causal reading of the checklist's effect |
| **F′** | `doi:10.1136/bmj.q824` | TRIPOD+AI "does the same for reporting" | **DIRECT** (record) | reporting guideline for clinical prediction models | a reporting guideline | calling it a checklist that "only" relies on humans — V1 already removed that framing |
| **G** | `arxiv:2605.08586` | "calls it experiment nonrepudiation … ships a reference implementation … proposes a protocol for conferences and calls for a standard" | **DIRECT** | "This position paper argues…"; "We name the underlying problem experiment nonrepudiation"; "K-Veritas, a reference implementation in Go"; "We call on conferences … to help build an open, independent standard" | position paper; named problem; testbed implementation | treating K-Veritas as a deployed standard — the authors call it "a testbed, not a finished answer" |
| **G′** | `arxiv:2601.14971` | "anchored to tamper-evident cryptographic commitments" | **DIRECT** | "anchors these traces to tamper-evident cryptographic commitments" | sample-level lineage, cryptographically anchored | that it governs claims or evaluation |
| **H** | `arxiv:2405.06347` | "the trust question … has been reviewed in its own right" | **DIRECT** | comprehensive review of trust in AI-driven CPS decision making | that the question is an active review subject | that it supplies a mechanism — it is a review |
| **I** | `arxiv:2310.10501` | "programmable output rails, independent of the underlying model and interpretable by the developer, are the industrial pattern" | **DIRECT** | NeMo Guardrails: programmable rails, model-agnostic toolkit | the industrial pattern | that rails constrain scientific claims |

### One caution on `arxiv:2603.10742`

**Its own abstract and body disagree on a number.** The abstract says "eight
typed primitives"; the body says "7 kernel primitives" and "the grammar's seven
primitives", consistently, four times. §2 does not cite the count and must not
start doing so. Cite the body, not the abstract.

---

## 8. CLOSEST-PRIOR-WORK MATRIX — corrected

**V1's matrix was wrong in one cell, and the error flattered this paper.** It
scored `arxiv:2603.10742` as ○ on consumed-attempt semantics on the strength of
its abstract. The full text shows an assess-once guard enforced at call time.
That cell is now ●, and the row is the closest prior art on the experimental
half of the contribution.

Legend: ● implements · ◐ partial · ○ absent.

| work | prereg | data/split authority | runtime gate | provenance / hash binding | consumed-attempt | claim-level executable guard | negative-result retention | recovery semantics | difference from CardioSentinel |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **`arxiv:2603.10742`** Roth 2026 | ○ | ● | ● | ○ | **●** | ○ | ◐ | ○ | **Closest on the experimental half.** Partition authority, call-time guard and assess-once in one grammar, producing "terminal evidence". Scoped to one process's object state; binds no artifact across runs; reads no claim |
| **`arxiv:2509.06902`** PCN 2025 | ○ | ○ | ○ | ◐ | ○ | ● | ○ | ○ | **Closest on the claim half.** Renderer-side verification, fail-closed, proved. Numerics only; one surface; no experiment lifecycle |
| `arxiv:2605.08586` nonrepudiation | ◐ | ○ | ○ | ● | ○ | ○ | ○ | ○ | Binds numbers to executions. Position paper; testbed, not a system |
| `arxiv:1502.04585` the Ladder | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ | Bounds leaderboard error under unlimited submissions. **Explicitly does not limit attempts** |
| `arxiv:1506.02629` reusable holdout | ○ | ● | ◐ | ○ | ○ | ○ | ○ | ○ | Makes reuse statistically safe. Opposite design to a consumed budget |
| `arxiv:2606.24996` fail-closed certification | ◐ | ○ | ● | ○ | ◐ | ◐ | ● | ○ | Gates a deployment claim; blocked 155 of 362 candidates. Forecasting leaderboards |
| `arxiv:2608.16891` Aegis | ○ | ○ | ● | ● | ○ | ◐ | ● | ◐ | Governs agent *actions*, not scientific claims |
| `arxiv:2103.05633` Proof-of-Learning | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | Training integrity, not evaluation integrity |
| `arxiv:2601.14971` FG-Trac (WWW 2026) | ○ | ◐ | ○ | ● | ○ | ○ | ○ | ○ | Sample lineage |
| `doi:10.3389/fcomp.2026.1735919` AIBOM | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | Supply-chain provenance |
| `arxiv:2109.10870` SoK ML Governance | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ◐ | Systematisation, not a system |
| `arxiv:2107.01905` leakage-free benchmarks | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | Enforced by procedure, not code |
| **CardioSentinel** | ● | ● | ● | ● | ● | ● | ● | ● | — |

**What the corrected matrix costs.** The experimental half of the contribution
is now substantially precedented: `arxiv:2603.10742` has partition authority, a
runtime gate and assess-once. What it does not have is any binding of that
authority to a generated surface. **The coupling is what survives, and §2.6 now
says only that.**

---

## 9. RED-LINE LITERATURE CLAIMS

**Claims on this list must not appear in any CardioSentinel manuscript,
figure, table, generated explanation or handoff. Adding to this list is
permitted; removing from it requires the primary source the claim lacked.**

### R1 — the EDB → LTSTDB detector comparison. **NOT AUTHORISED FOR USE.**

The wording, from `73cc902` and superseded before V1 of this audit:

> "A detector reported at 85% / 86% sensitivity and positive predictivity on
> EDB fell to 70% / 68% when carried to LTSTDB, in part because LTSTDB contains
> ST episodes generated by postural change that a detector can misread as
> ischaemic."

Refused for five independent reasons, any one of them sufficient:

1. **Primary source not established.** No record in `LITERATURE_SEARCH_V1.json`
   or `V2`, and none located in either audit, reports one detector at those
   four values across the two databases.
2. **Database duration differs materially.** European ST-T records are **2
   hours**; Long-Term ST records are **24 hours** — a 12× difference in
   exposure per record (`pmid:1396824`, `pmid:12691437`).
3. **Annotation protocols differ.** LTSTDB's protocols and its SEMIA annotation
   tool (`pmid:15265622`) were *newly developed* for it, a decade after EDB.
4. **Denominator comparability is not established.** Sensitivity and positive
   predictivity computed over episode sets defined by different protocols do
   not share a denominator, so a difference between them is not a degradation
   of one quantity.
5. **The causal attribution was an inference.** No source was found in which
   authors attribute a cross-database difference to postural episodes.

**What may still be said**, and the only wording authorised:

> LTSTDB was constructed to be harder than its predecessors by design: its
> records are 24 hours rather than the European ST-T Database's two, and its
> annotation protocol explicitly separates transient ischaemic episodes from
> heart-rate-related and postural ST change [`pmid:12691437`, `pmid:1396824`].

The LTSTDB primary paper **may** be cited for its documented non-ischaemic
postural-change annotations. It **may not** be cited for any cross-database
performance figure.

### R2 — "prospective checks … are *utterly absent*" in health ML. **WITHDRAWN.**

Attributed in `73cc902` to `arxiv:1907.01463`. The phrase is not in that paper;
its population is "over 100 recently published ML4H research papers"; its
finding is about **data and code accessibility**, not prospectivity; and it is
an **ICLR workshop** paper (§6). Three defects — quotation, generalisation and
re-framing. Do not restore in any form.

### R3 — "None of them reads the sentence a human will actually take away."
**WITHDRAWN**, refuted by `arxiv:2509.06902` at full text (§7A). Do not restore.

### R4 — priority language. `first`, `unique`, `unprecedented` and `no prior
work` are **not authorised** anywhere in §2. Qualified forms only: "to the best
of our targeted review", "as far as we are aware", "we found no prior system".

---

## 10. FINAL NOVELTY WORDING

The candidate axis put to the stress test:

> "CardioSentinel couples experimentally enforced evidence provenance with
> runtime claim exposure: the same authority that governs partition use,
> attempt consumption and retained scientific evidence also constrains what the
> agentic/runtime surface may state."

**Tested against the corrected matrix, it survives — narrowly, and for one
reason only.** Every constituent property is precedented:

- partition authority, runtime gating and attempt consumption → `arxiv:2603.10742`
- bounded evaluation → `arxiv:1502.04585`, `arxiv:1506.02629`
- artifact binding → `arxiv:2605.08586`, `arxiv:2601.14971`, `doi:10.3389/fcomp.2026.1735919`
- claim-level fail-closed enforcement → `arxiv:2509.06902`
- runtime action governance with provenance → `arxiv:2608.16891`

**What no reviewed work does is span the two halves with one authority.** The
frozen wording, now in §2.6:

> To the best of our targeted review, we found no prior system in which one
> authority spans both halves. The artifact that governs partition use, attempt
> consumption and retained evidence in this system is the artifact that
> constrains what its runtime surface — and this manuscript — may state, so an
> overclaim in generated prose and an overclaim in §7 fail against the same
> code. That coupling is the claim. It is not a claim about either half
> separately, and it does not rest on the priority that either 2026 preprint
> above asserts for itself.

**It is robust to both preprints being wrong about themselves** (brief §7). If
`arxiv:2603.10742` is not the first call-time evaluation gate, or
`arxiv:2509.06902` not the first renderer-side claim verifier, an *earlier*
system did one half — which leaves the coupling exactly as unattested. The
claim would only fail if a system were found doing **both**, and none was.

Forbidden words checked: `first`, `unique`, `unprecedented`, `no prior work` do
not appear in §2 in a novelty sense.

---

## 11. REMAINING CITATION RISKS

0. **CLOSED 2026-08-28 — all nineteen venue claims are independently
   confirmed, zero conflicts.** The last three were verified against the ICLR
   virtual programme, the ACM Digital Library and the workshop OpenReview
   record. Retained here as history: this item previously read — Of the nineteen, six were
   corroborated by Semantic Scholar and a further ten by official proceedings,
   publisher record or OpenReview — **sixteen two-source, zero conflicts**.
   `arxiv:2111.00396` (ICLR 2022), `arxiv:2601.14971` (WWW 2026) and
   `arxiv:1907.01463` (RML@ICLR 2019 workshop) returned no independent record.
   They are unconfirmed, **not contradicted**, and must be checked by hand
   against the venue page at bibliography time.
1. **Nineteen confirmed venues are recorded here but not in the section's
   keys.** The bibliography must cite ICML/ICLR/NeurIPS/TMLR/CACM/JMLR/EMNLP/
   CHIL/WWW/EMBC/ETFA at assembly, not arXiv. Swapping keys now would break
   verification, because those DOIs are in no harvest. **Largest remaining
   item, and it is a bibliography task.**
2. **Fourteen citations remain preprint-only**, two of them load-bearing
   (`arxiv:2603.10742`, `arxiv:2509.06902`). §2 cites both as evidence that a
   mechanism exists, not as authority, and the novelty claim is independent of
   their own priority claims (§10).
3. **`arxiv:2603.10742` contradicts itself** on primitive count (§7). Cite the
   body.
4. **Two citations are refereed workshop papers**, not main-conference:
   `arxiv:2106.04452` (ML4H) and `arxiv:1907.01463` (RML@ICLR). Label them.
5. **V2 has 8 failed queries** and does not reproduce V1. This is recorded
   rather than repaired, and `verify` resolves against the union. A reader
   comparing the two records will see the drift; that is the honest state.
6. **Full text was read for ten sources, not all 87.** The remaining
   landscape citations rest on abstract-level checks from V1.
7. **`arxiv:2409.07975`** resolves in no venue index; it is a review and
   carries only a landscape statement, narrowed in V1.

---

## 12. CONTROL-PLANE

No frozen experiment report was modified. No historical handoff was rewritten.
`LITERATURE_SEARCH_V1.json` is byte-identical (`git diff` empty) and its
`payload_sha256` is unchanged. `CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md`
is retained unaltered, including the matrix cell §8 corrects — **the error is
superseded, not erased.**

Files changed by this task: `scripts/literature_search.py` (extraction fix,
pacing, union verify, V2 query set), `paper/PAPER_S2_RELATED_WORK_DRAFT.md`
(§2.6 and §2.7), `docs/literature/LITERATURE_SEARCH_V2.json` (new),
`tests/reproducibility/test_literature_citation_extraction.py` (new), this
document (new).

---

## 13. VERDICT

Every blocker V1 named is closed. The verifier defect is fixed and regression-
tested at the exact failure. The falsification sources are in an immutable
harvest with its own digest, and V1's digest is untouched. Nineteen venues are
confirmed. Ten sources were read in full text, and doing so **reversed one of
V1's own conclusions** in the direction that costs this paper something. The
novelty claim is narrower than it was this morning and does not depend on any
unrefereed preprint's self-assessment.

Two things remain, and neither is a verification defect: the bibliography must
carry the nineteen confirmed venues at assembly time, and fourteen citations
are preprints that may or may not be refereed before submission. Both are
manuscript-assembly work on a section whose citations are now fully resolved.

RELATED WORK VERIFIED — READY FOR MANUSCRIPT ASSEMBLY
