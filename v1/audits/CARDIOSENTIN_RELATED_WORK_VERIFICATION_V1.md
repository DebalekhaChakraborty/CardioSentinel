# CardioSentinel — Related-Work Verification and Gap Stress-Test, V1

**Run:** 2026-08-28 · **Target:** `docs/PAPER_S2_RELATED_WORK_DRAFT.md` at
`sha256:ac079abb2aa969bc…` (252 lines) · **Branch:**
`feat/e11-e13a-instrumentation-and-paper-readiness`

No scientific result was changed. No model experiment was run. No sealed TEST
evidence was touched. The manuscript was not rewritten around the B4 outcome.
The §6.3 ordering condition was not relied on and remains binding.

---

## 0. READ THIS FIRST — the task's premise was one revision stale

The brief describes a §2 in which *"most citations are marked SEARCH-RETURNED"*,
which contrasts checklists with executable enforcement using the phrase
*"utterly absent"*, and which carries an **EDB 85% / 86% → LTSTDB 70% / 68%**
detector comparison attributed in part to postural ST episodes.

**None of that is in the file any more.** That text is the version committed at
`73cc902` (237 lines). It was superseded before this task began:

| commit | what happened |
|---|---|
| `73cc902` | E11–E13a branch adds §2 draft **with** `SEARCH-RETURNED` markers, the EDB/LTSTDB comparison and the "utterly absent" quote |
| `e0e3a79` | **PR #127** merged to `master` — a rewritten §2 |
| `2675bc1` | master merged into this branch; commit message: *"PR #127's section 2 supersedes ours"* |

Verified against the live file:

- `grep -c "SEARCH-RETURNED"` → **0**
- `git grep "utterly absent"` / `"postural"` / `"positive predictivity"` at HEAD → **no hits anywhere in the repository**
- All 77 citation keys are inline provenance keys (`doi:` / `pmid:` / `arxiv:`), not status-marked entries

So steps 3 and 7 of the brief target **text that no longer exists**. Both are
still answered below — step 3 because the numbers must never be reintroduced
without the finding recorded here, step 7 because the paraphrase that replaced
the quotation still needs checking. Steps 1, 2, 4, 5, 6, 8, 9, 11 and 12 were
executed against the **live** draft.

**Interpretation of the status-marker rule.** The brief requires every citation
to "finish with" a status. The live draft cites inline inside flowing prose;
appending `VERIFIED — PRIMARY` to 77 inline keys would wreck the section and
contradicts the brief's own "do not rewrite gratuitously". The per-citation
status therefore lives in the §1 ledger of this document, and the draft header
now points at it. No `SEARCH-RETURNED` citation remains, because none exists.

---

## 1. CITATION LEDGER — all 77 audited

Every key was resolved against an authoritative bibliographic API: Crossref for
`doi:`, NCBI E-utilities for `pmid:`, the arXiv API for `arxiv:`.

**Totals: 77 unique keys · 77 resolved · 0 unresolved · 0 fabricated.**
**48 `VERIFIED — PRIMARY` · 29 `PREPRINT — VERIFIED`.**
By scheme: 44 arXiv, 20 DOI, 13 PubMed.

| # | key | §  | source type | year | title | venue / published record | status |
|--:|---|---|---|--:|---|---|---|
| 1 | `arxiv:2605.08586` | header | preprint | 2026 | Computer Science Conferences Should Require Nonrepudiable Experimental Resul | arXiv preprint | PREPRINT — VERIFIED |
| 2 | `pmid:1396824` | 2.1 | primary paper | 1992 | The European ST-T database: standard for evaluating systems for the analysis | European heart journal | VERIFIED — PRIMARY |
| 3 | `pmid:12691437` | 2.1 | primary paper | 2003 | Long-term ST database: a reference for the development and evaluation of aut | Medical & biological engineering & computing | VERIFIED — PRIMARY |
| 4 | `doi:10.1161/01.cir.101.23.e215` | 2.1 | primary paper | 2000 | PhysioBank, PhysioToolkit, and PhysioNet | Circulation | VERIFIED — PRIMARY |
| 5 | `doi:10.1109/cic.1995.482762` | 2.1 | primary paper | None | A system for the detection of ischemic episodes in ambulatory ECG | Computers in Cardiology 1995 | VERIFIED — PRIMARY |
| 6 | `doi:10.1109/cic.1996.542628` | 2.1 | primary paper | None | Characterization of temporal patterns of transient ischemic ST change episod | Computers in Cardiology 1996 | VERIFIED — PRIMARY |
| 7 | `doi:10.1109/cic.2002.1166774` | 2.1 | primary paper | None | Advanced detection of ST segment episodes in 24-hour ambulatory ECG data by  | Computers in Cardiology | VERIFIED — PRIMARY |
| 8 | `pmid:15191074` | 2.1 | primary paper | 2004 | Automated detection of transient ST-segment episodes in 24 h electrocardiogr | Medical & biological engineering & computing | VERIFIED — PRIMARY |
| 9 | `doi:10.1186/1475-925x-10-107` | 2.1 | primary paper | 2011 | Automatic classification of long-term ambulatory ECG records according to ty | BioMedical Engineering OnLine | VERIFIED — PRIMARY |
| 10 | `doi:10.1109/cic.2008.4749058` | 2.1 | primary paper | 2008 | Automatic distinguishing between ischemic and heart-rate related transient S | 2008 Computers in Cardiology | VERIFIED — PRIMARY |
| 11 | `pmid:20130344` | 2.1 | primary paper | 2010 | Automatic classification of transient ischaemic and transient non-ischaemic  | Physiological measurement | VERIFIED — PRIMARY |
| 12 | `pmid:22874369` | 2.1 | primary paper | 2012 | Classification of ischaemic episodes with ST/HR diagrams. | Studies in health technology and informatics | VERIFIED — PRIMARY |
| 13 | `pmid:19696464` | 2.1 | primary paper | 2009 | Real-time detection of transient cardiac ischemic episodes from ECG signals. | Physiological measurement | VERIFIED — PRIMARY |
| 14 | `pmid:26863140` | 2.1 | primary paper | 2016 | Electrocardiogram ST-Segment Morphology Delineation Method Using Orthogonal  | PloS one | VERIFIED — PRIMARY |
| 15 | `pmid:15265622` | 2.1 | primary paper | 2004 | Semia: semi-automatic interactive graphic editing tool to annotate ambulator | Computer methods and programs in biomedicine | VERIFIED — PRIMARY |
| 16 | `arxiv:2001.01550` | 2.2 | preprint | 2019 | Opportunities and Challenges of Deep Learning Methods for Electrocardiogram  | Computers in Biology and Medicine · doi:10.1016/j.compbiomed | VERIFIED — PRIMARY |
| 17 | `arxiv:2409.07975` | 2.2 | preprint | 2024 | Deep Learning for Personalized Electrocardiogram Diagnosis: A Review | arXiv preprint | PREPRINT — VERIFIED |
| 18 | `pmid:42129209` | 2.2 | primary paper | 2026 | A deep learning ECG model for identification and localization of occlusion m | Nature communications | VERIFIED — PRIMARY |
| 19 | `pmid:42082497` | 2.2 | primary paper | 2026 | A large-scale 12-lead electrocardiogram dataset for acute coronary syndrome  | Scientific data | VERIFIED — PRIMARY |
| 20 | `pmid:41358268` | 2.2 | primary paper | 2025 | Transfer Learning Strategies for Cardiovascular Disease Detection in ECG Ima | Biomedical engineering and computational biology | VERIFIED — PRIMARY |
| 21 | `arxiv:2201.10061` | 2.2 | preprint | 2022 | Negative-ResNet: Noisy Ambulatory Electrocardiogram Signal Classification Sc | Neural Computing and Applications · doi:10.1007/s00521-020-0 | VERIFIED — PRIMARY |
| 22 | `arxiv:2203.06889` | 2.2 | preprint | 2022 | Lead-agnostic Self-supervised Learning for Local and Global Representations  | arXiv preprint | PREPRINT — VERIFIED |
| 23 | `arxiv:2106.04452` | 2.2 | preprint | 2021 | 3KG: Contrastive Learning of 12-Lead Electrocardiograms using Physiologicall | arXiv preprint | PREPRINT — VERIFIED |
| 24 | `arxiv:2007.04871` | 2.2 | preprint | 2020 | Subject-Aware Contrastive Learning for Biosignals | arXiv preprint | PREPRINT — VERIFIED |
| 25 | `arxiv:2309.07136` | 2.2 | preprint | 2023 | Masked Transformer for Electrocardiogram Classification | arXiv preprint | PREPRINT — VERIFIED |
| 26 | `arxiv:2111.00396` | 2.2 | preprint | 2021 | Efficiently Modeling Long Sequences with Structured State Spaces | arXiv preprint | PREPRINT — VERIFIED |
| 27 | `arxiv:2203.14343` | 2.2 | preprint | 2022 | Diagonal State Spaces are as Effective as Structured State Spaces | Advances in Neural Information Processing Systems 35 · doi:1 | VERIFIED — PRIMARY |
| 28 | `arxiv:2206.11893` | 2.2 | preprint | 2022 | On the Parameterization and Initialization of Diagonal State Space Models | Advances in Neural Information Processing Systems 35 · doi:1 | VERIFIED — PRIMARY |
| 29 | `arxiv:1810.03993` | 2.3 | preprint | 2018 | Model Cards for Model Reporting | FAT* '19: Conference on Fairness, Accountability, and Transp | VERIFIED — PRIMARY |
| 30 | `arxiv:1803.09010` | 2.3 | preprint | 2018 | Datasheets for Datasets | arXiv preprint | PREPRINT — VERIFIED |
| 31 | `doi:10.1136/bmj.q824` | 2.3 | primary paper | 2024 | TRIPOD+AI: an updated reporting guideline for clinical prediction models | BMJ | VERIFIED — PRIMARY |
| 32 | `arxiv:2003.12206` | 2.3 | preprint | 2020 | Improving Reproducibility in Machine Learning Research (A Report from the Ne | arXiv preprint | PREPRINT — VERIFIED |
| 33 | `arxiv:2306.09562` | 2.3 | preprint | 2023 | Reproducibility in NLP: What Have We Learned from the Checklist? | Findings of the Association for Computational Linguistics: A | VERIFIED — PRIMARY |
| 34 | `doi:10.1016/j.patter.2023.100804` | 2.3 | primary paper | 2023 | Leakage and the reproducibility crisis in machine-learning-based science | Patterns | VERIFIED — PRIMARY |
| 35 | `arxiv:2207.07048` | 2.3 | preprint | 2022 | Leakage and the Reproducibility Crisis in ML-based Science | arXiv preprint | PREPRINT — VERIFIED |
| 36 | `arxiv:1909.06539` | 2.3 | preprint | 2019 | AI slipping on tiles: data leakage in digital pathology | Lecture Notes in Computer Science · doi:10.1007/978-3-030-68 | VERIFIED — PRIMARY |
| 37 | `doi:10.1038/d41586-022-02035-w` | 2.3 | primary paper | 2022 | Could machine learning fuel a reproducibility crisis in science? | Nature | VERIFIED — PRIMARY |
| 38 | `arxiv:1907.01463` | 2.3 | preprint | 2019 | Reproducibility in Machine Learning for Health | arXiv preprint | PREPRINT — VERIFIED |
| 39 | `arxiv:2401.08847` | 2.3 | preprint | 2024 | RIDGE: Reproducibility, Integrity, Dependability, Generalizability, and Effi | Journal of Imaging Informatics in Medicine · doi:10.1007/s10 | VERIFIED — PRIMARY |
| 40 | `arxiv:2311.18807` | 2.3 | preprint | 2023 | Pre-registration for Predictive Modeling | arXiv preprint | PREPRINT — VERIFIED |
| 41 | `doi:10.1038/s41593-024-01762-9` | 2.3 | primary paper | 2024 | Reducing publication bias with Registered Reports | Nature Neuroscience | VERIFIED — PRIMARY |
| 42 | `doi:10.1146/annurev.nucl.55.090704.151521` | 2.3 | primary paper | 2005 | BLIND ANALYSIS IN NUCLEAR AND PARTICLE PHYSICS | Annual Review of Nuclear and Particle Science | VERIFIED — PRIMARY |
| 43 | `doi:10.1088/0954-3899/28/10/312` | 2.3 | primary paper | 2002 | Blind analysis | Journal of Physics G: Nuclear and Particle Physics | VERIFIED — PRIMARY |
| 44 | `doi:10.2172/826602` | 2.3 | primary paper | 2003 | Blind Analysis in Particle Physics | Office of Scientific and Technical Information (OSTI) | VERIFIED — PRIMARY |
| 45 | `doi:10.1109/tit.1970.1054406` | 2.4 | primary paper | 1970 | On optimum recognition error and reject tradeoff | IEEE Transactions on Information Theory | VERIFIED — PRIMARY |
| 46 | `doi:10.1613/jair.4439` | 2.4 | primary paper | 2015 | Agnostic Pointwise-Competitive Selective Classification | Journal of Artificial Intelligence Research | VERIFIED — PRIMARY |
| 47 | `arxiv:1705.08500` | 2.4 | preprint | 2017 | Selective Classification for Deep Neural Networks | arXiv preprint | PREPRINT — VERIFIED |
| 48 | `arxiv:1901.09192` | 2.4 | preprint | 2019 | SelectiveNet: A Deep Neural Network with an Integrated Reject Option | arXiv preprint | PREPRINT — VERIFIED |
| 49 | `arxiv:2206.09034` | 2.4 | preprint | 2022 | Towards Better Selective Classification | arXiv preprint | PREPRINT — VERIFIED |
| 50 | `arxiv:2208.12084` | 2.4 | preprint | 2022 | Calibrated Selective Classification | arXiv preprint | PREPRINT — VERIFIED |
| 51 | `arxiv:2205.13532` | 2.4 | preprint | 2022 | Selective Prediction via Training Dynamics | arXiv preprint | PREPRINT — VERIFIED |
| 52 | `arxiv:2405.05160` | 2.4 | preprint | 2024 | Selective Classification Under Distribution Shifts | arXiv preprint | PREPRINT — VERIFIED |
| 53 | `arxiv:1706.04599` | 2.4 | preprint | 2017 | On Calibration of Modern Neural Networks | arXiv preprint | PREPRINT — VERIFIED |
| 54 | `arxiv:2106.07998` | 2.4 | preprint | 2021 | Revisiting the Calibration of Modern Neural Networks | arXiv preprint | PREPRINT — VERIFIED |
| 55 | `arxiv:2006.01862` | 2.4 | preprint | 2020 | Consistent Estimators for Learning to Defer to an Expert | arXiv preprint | PREPRINT — VERIFIED |
| 56 | `arxiv:2202.03673` | 2.4 | preprint | 2022 | Calibrated Learning to Defer with One-vs-All Classifiers | arXiv preprint | PREPRINT — VERIFIED |
| 57 | `arxiv:2310.14774` | 2.4 | preprint | 2023 | Principled Approaches for Learning to Defer with Multiple Experts | Lecture Notes in Computer Science · doi:10.1007/978-3-031-63 | VERIFIED — PRIMARY |
| 58 | `arxiv:2005.11401` | 2.5 | preprint | 2020 | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | arXiv preprint | PREPRINT — VERIFIED |
| 59 | `arxiv:2305.06983` | 2.5 | preprint | 2023 | Active Retrieval Augmented Generation | arXiv preprint | PREPRINT — VERIFIED |
| 60 | `arxiv:2401.15884` | 2.5 | preprint | 2024 | Corrective Retrieval Augmented Generation | arXiv preprint | PREPRINT — VERIFIED |
| 61 | `arxiv:2005.00661` | 2.5 | preprint | 2020 | On Faithfulness and Factuality in Abstractive Summarization | Proceedings of the 58th Annual Meeting of the Association fo | VERIFIED — PRIMARY |
| 62 | `arxiv:2112.12870` | 2.5 | preprint | 2021 | Measuring Attribution in Natural Language Generation Models | Computational Linguistics · doi:10.1162/coli_a_00490 | VERIFIED — PRIMARY |
| 63 | `arxiv:2202.03629` | 2.5 | preprint | 2022 | Survey of Hallucination in Natural Language Generation | ACM Computing Surveys (2022) · doi:10.1145/3571730 | VERIFIED — PRIMARY |
| 64 | `arxiv:2501.03200` | 2.5 | preprint | 2025 | The FACTS Grounding Leaderboard: Benchmarking LLMs' Ability to Ground Respon | arXiv preprint | PREPRINT — VERIFIED |
| 65 | `arxiv:2406.13692` | 2.5 | preprint | 2024 | Synchronous Faithfulness Monitoring for Trustworthy Retrieval-Augmented Gene | Proceedings of the 2024 Conference on Empirical Methods in N | VERIFIED — PRIMARY |
| 66 | `arxiv:2310.10501` | 2.5 | preprint | 2023 | NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with P | Proceedings of the 2023 Conference on Empirical Methods in N | VERIFIED — PRIMARY |
| 67 | `arxiv:2504.00441` | 2.5 | preprint | 2025 | No Free Lunch with Guardrails | arXiv preprint | PREPRINT — VERIFIED |
| 68 | `arxiv:2510.05310` | 2.5 | preprint | 2025 | RAG Makes Guardrails Unsafe? Investigating Robustness of Guardrails under RA | arXiv preprint | PREPRINT — VERIFIED |
| 69 | `pmid:41933065` | 2.5 | primary paper | 2026 | An AI-based mental health guardrail and dataset for identifying psychiatric  | NPJ digital medicine | VERIFIED — PRIMARY |
| 70 | `pmid:38664535` | 2.5 | primary paper | 2024 | Large language models for preventing medication direction errors in online p | Nature medicine | VERIFIED — PRIMARY |
| 71 | `arxiv:2601.14971` | 2.6 | preprint | 2026 | Fine-Grained Traceability for Transparent ML Pipelines | arXiv preprint | PREPRINT — VERIFIED |
| 72 | `arxiv:2605.19755` | 2.6 | preprint | 2026 | Operationalising Artificial Intelligence Bills of Materials (AIBOMs) for Ver | Front. Comput. Sci. 8:1735919 (2026) · doi:10.3389/fcomp.202 | VERIFIED — PRIMARY |
| 73 | `doi:10.1016/j.procs.2011.04.061` | 2.6 | primary paper | 2011 | A data and code model for reproducible research and executable papers | Procedia Computer Science | VERIFIED — PRIMARY |
| 74 | `doi:10.1016/j.procs.2012.04.047` | 2.6 | primary paper | 2012 | Literate Program Execution for Reproducible Research and Executable Papers | Procedia Computer Science | VERIFIED — PRIMARY |
| 75 | `doi:10.3233/apc200107` | 2.6 | book-chapter | 2020 | Toward Enabling Reproducibility for Data-Intensive Research Using the Whole  | Advances in Parallel Computing | VERIFIED — PRIMARY |
| 76 | `doi:10.1186/s13059-021-02299-x` | 2.6 | primary paper | 2021 | Promoting reproducibility with Code Ocean | Genome Biology | VERIFIED — PRIMARY |
| 77 | `doi:10.1038/s41562-021-01190-w` | 2.6 | primary paper | 2021 | Supporting computational reproducibility through code review | Nature Human Behaviour | VERIFIED — PRIMARY |

**A note on the 29 preprints.** arXiv's `journal_ref` field is author-maintained
and mostly empty, so it cannot be used to decide publication status. Every
preprint-only key was additionally title-matched against Crossref at ≥0.92
similarity; 12 published versions were recovered that way and are shown in the
venue column. The remainder are labelled `PREPRINT — VERIFIED` **because the
venue could not be confirmed from a machine-readable record, not because the
work is unpublished** — Crossref does not index NeurIPS, ICML or ICLR
proceedings, which is where several of them almost certainly sit (S4, Guo et
al. calibration, SelectiveNet, RAG). Confirming those requires a
proceedings-side check that is a manuscript-assembly task, not a verification
one. **This is a live risk and it is listed in §9.**

---

## 2. CLAIM SUPPORT — what the sources actually say

Fourteen load-bearing statements were checked against the source abstract or
record, not against the citation. Ten hold exactly. Four are overstated.

### 2.1 Supported exactly — quote-level match

| draft statement | source | what the source says |
|---|---|---|
| "over 10,405 responses" | `arxiv:2306.09562` | "examining **10,405** anonymous responses" — exact |
| "fewer than half of submissions claim to open-source code" | `arxiv:2306.09562` | "only **46%** of submissions claim to open-source their code" |
| "increases in reported information" | `arxiv:2306.09562` | "an increase in reporting of information on efficiency, validation performance, summary statistics, and hyperparameters" |
| "leakage … across **17 fields**" | `arxiv:2207.07048` | "we find **17 fields** where errors have been found, collectively affecting 329 papers" |
| "lightweight template with a qualitative evaluation" | `arxiv:2311.18807` | "introduce a **lightweight pre-registration template**, and present a **qualitative study** with machine learning researchers" |
| "calls it *experiment nonrepudiation*" | `arxiv:2605.08586` | "We name the underlying problem **experiment nonrepudiation**" — exact |
| "self-reported checklists, optional code sharing and author-controlled logging" | `arxiv:2605.08586` | "relies on **self-reported checklists, optional code sharing, and author-controlled logging**" — exact |
| "threat model spelled out … ships a reference implementation" | `arxiv:2605.08586` | "describe a threat model…"; "we built **K-Veritas**, a reference implementation in Go" |
| "anchored to tamper-evident cryptographic commitments" | `arxiv:2601.14971` | "anchors these traces to **tamper-evident cryptographic commitments**" — exact |
| "LTSTDB … built expressly as a reference for developing and evaluating automated ischemia detectors" | `pmid:12691437` | title and abstract both state exactly this purpose |

**§2.4's self-referential claim also verifies.** The draft says *"Across the 77
records this subsection's queries returned…"*. Recomputed from
`LITERATURE_SEARCH_V1.json`: subsection 2.4 ran 13 queries returning **77 hits**
(73 unique). **Exact.** The stated bound ("a statement about what a recorded
search returned, not a claim about the field") is the correct framing and needs
no change.

### 2.2 Overstated — four narrowings required

| # | draft wording | source | problem | required wording |
|---|---|---|---|---|
| **O1** | "an unavoidable security/usability tradeoff" | `arxiv:2504.00441` | source says strengthening security "**often** comes at the cost of usability" and then proposes "a blueprint for designing better guardrails that **minimize risk while maintaining usability**" — i.e. the authors explicitly do not treat it as unavoidable | "a **recurring** security/usability tradeoff" |
| **O2** | "surveyed systematically in [2001.01550] and, for the personalised setting, in [2409.07975]" | `arxiv:2409.07975` | 2001.01550 **is** "A Systematic Review" (191 papers, 2010–Feb 2020). 2409.07975 is titled "**A Review**"; it claims a "rigorous methodology" but not systematic-review status. The shared adverb over-credits it | "surveyed systematically in [2001.01550] and **reviewed**, for the personalised setting, in [2409.07975]" |
| **O3** | "characterised as **structurally worse** than in neighbouring fields" | `arxiv:1907.01463` | source says ML4H "**compares poorly to more established machine learning fields, particularly concerning data and code accessibility**", from "over 100 recently published ML4H research papers". "Structurally" is an editorial gloss and the sample is not stated | "found to compare poorly with more established machine-learning fields **on data and code accessibility, in a review of over 100 ML4H papers**" |
| **O4** | NeurIPS programme grouped under "measure what checklists changed" | `arxiv:2003.12206` | the report **describes** the deployment of three components and what the organisers learned; it does not measure checklist effect. The measurement is 2306.09562's | attribute description to 2003.12206 and measurement to 2306.09562 separately |

### 2.3 Citation-quality defect

**`arxiv:2605.19755` is cited as a preprint but is published.** The arXiv record
carries `Front. Comput. Sci. 8:1735919 (2026)`, `doi:10.3389/fcomp.2026.1735919`.
Rule 10 prefers the peer-reviewed version. **Replace the key.**

No blogs, vendor marketing, scraped citation pages or untraceable secondary
quotes were found anywhere in the section.

---

## 3. THE EDB → LTSTDB COMPARISON — traced, and the verdict is *do not reintroduce*

The comparison is **not in the live draft**. It was in `73cc902`:

> "A detector reported at **85% / 86% sensitivity and positive predictivity on
> EDB fell to 70% / 68% when carried to LTSTDB**, in part because LTSTDB
> contains ST episodes generated by postural change that a detector can misread
> as ischaemic [**SEARCH-RETURNED**; to be traced to its primary source before
> submission]."

That trace was never done. It has now been attempted.

**What the primary database papers establish.**

| | European ST-T DB (`pmid:1396824`, 1992) | Long-Term ST DB (`pmid:12691437`, 2003) |
|---|---|---|
| records | 90 | 86 |
| channels | 2 | 2 and 3 |
| **duration each** | **2 hours** | **24 hours** |
| subjects | 13 groups, 8 countries | 80 patients, USA + Europe, 1994–2000 |
| annotated events | 372 ST + 423 T changes | 1155 transient ischaemic episodes, plus heart-rate-related ST episodes |
| non-ischaemic annotation | not described in these terms | explicit: events "related to **postural changes** and conduction abnormalities" |

**Findings.**

1. **The postural mechanism is real and primary-sourced.** LTSTDB's own paper
   states that the database annotates non-ischaemic ST events related to
   postural change. That half of the old sentence was correct.
2. **The 85/86 → 70/68 figures could not be traced to a primary source.** No
   record in `LITERATURE_SEARCH_V1.json`, and no source located in this audit,
   reports one detector at those four values across the two databases.
3. **Even if traced, the numbers would not be directly comparable.** EDB
   records are **2 hours**; LTSTDB records are **24 hours** — a 12× difference
   in exposure per record. The databases were built a decade apart, under
   different annotation protocols (LTSTDB's protocols and the SEMIA tool,
   `pmid:15265622`, were *newly developed* for it), against different
   inclusion criteria, and LTSTDB annotates a category — heart-rate-related and
   postural ST change — that EDB does not separate the same way. Sensitivity
   and positive predictivity computed over episode sets defined by different
   protocols have **different denominators**, so the difference between them is
   not a benchmark degradation of a fixed quantity.
4. **The causal attribution was an inference, not an author conclusion.** No
   source was found in which authors attribute a cross-database performance
   drop to postural episodes.

**Exact permitted wording, if any of this is wanted in §2:**

> LTSTDB was constructed to be harder than its predecessors by design: its
> records are 24 hours rather than the European ST-T Database's two, and its
> annotation protocol explicitly separates transient ischaemic episodes from
> heart-rate-related and postural ST change [`pmid:12691437`, `pmid:1396824`].

**Not permitted** without a traced primary source: any pair of numbers presented
as one detector's performance on both databases; any sentence of the form "X%
fell to Y%"; any causal attribution of a cross-database difference to postural
episodes. **Recommendation: do not reintroduce.** The sentence above carries the
whole rhetorical load the old one carried, and it is true.

---

## 4. THE HEALTH-ML PROSPECTIVITY CLAIM — the quotation is correctly gone

The `73cc902` text asserted that prospective checks in health ML are
*"utterly absent"*, attributed to *Reproducibility in Machine Learning for
Health* (`arxiv:1907.01463`).

**The phrase does not appear in that paper's abstract.** What the paper supports:

- **Population:** "over **100** recently published ML4H research papers" — a
  sample, not the field.
- **Method:** "a systematic evaluation … along several dimensions related to
  reproducibility".
- **Conclusion:** ML4H "compares poorly to more established machine learning
  fields, **particularly concerning data and code accessibility**".
- **"Prospective" is not the paper's frame at all.** Its dimensions are
  accessibility of data and code, not prospective versus retrospective design.

So the old sentence generalised a ~100-paper sample to all health ML, quoted
language not evidenced in the abstract, and re-framed an accessibility finding
as a prospectivity finding. **Three defects; the rewrite removed all three.**

The live draft's replacement — "Reproducibility in ML for health specifically
has been characterised as structurally worse than in neighbouring fields" — is
paraphrase, which is safer, but still overstates. See **O3**.

---

## 5. WIDER SEARCH — 18 further queries across the brief's themes A–J

The section rested on 65 recorded queries (`LITERATURE_SEARCH_V1.json`:
393 hits, 354 unique, sources crossref/pubmed/arxiv). This audit added **18
targeted queries** across executable governance, preregistration, runtime
protocol enforcement, provenance-bound pipelines, leakage prevention in code,
consumed-attempt semantics, machine-checkable claims, fail-closed model
selection, trustworthy physical AI, and agentic output validation.

**It found prior art the original search missed, and some of it is close.**

---

## 6. CLOSEST PRIOR WORK MATRIX

Legend: ● implements · ◐ partial · ○ absent.

| work | prereg | data/split authority enforcement | runtime experiment gate | provenance / hash binding | consumed-attempt semantics | claim-level executable guard | negative-result retention | recovery semantics | difference from CardioSentinel |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **`arxiv:2603.10742`** Roth 2026, *Rejecting Data Leakage at Call Time* | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ | **Closest on enforcement.** A typed grammar + DAG whose "terminal assessment gate" is call-time-enforced; claims to be "the **first** call-time-enforced evaluate/assess boundary … in the peer-reviewed ML methodology literature". Governs the *workflow*; binds no artifact and reads no claim |
| **`arxiv:2509.06902`** Solatorio 2025, *Proof-Carrying Numbers* | ○ | ○ | ○ | ◐ | ○ | ● | ○ | ○ | **Closest on the claim guard.** Numeric spans as claim-bound tokens, verified in the **renderer not the model**, fail-closed by default, with soundness/completeness proofs. Numeric claims only, one surface, no experiment lifecycle |
| **`arxiv:2605.08586`** *Nonrepudiable Experimental Results* | ◐ | ○ | ○ | ● | ○ | ○ | ○ | ○ | Already cited. Binds numbers to executions; does not read the sentence |
| **`arxiv:1502.04585`** Blum & Hardt 2015, *The Ladder* | ○ | ● | ● | ○ | ● | ○ | ○ | ○ | **The canonical consumed-evaluation mechanism.** Bounds adaptive holdout reuse algorithmically. Statistical guarantee, not an artifact trail; no claim object |
| **`arxiv:1506.02629`** Dwork et al. 2015, *Holdout Reuse* | ○ | ● | ◐ | ○ | ● | ○ | ○ | ○ | Differential-privacy-based reusable holdout. **Makes reuse safe; CardioSentinel makes reuse impossible.** Opposite design, same problem |
| **`arxiv:2606.24996`** 2026, *Fail-Closed Certification Protocol* | ◐ | ○ | ● | ○ | ◐ | ◐ | ● | ○ | Gates a deployment claim on sufficient evidential conditions; "locked native audit" blocked 155 of 362 candidate claims. Forecasting leaderboards, not an experiment lifecycle |
| **`arxiv:2103.05633`** Jia et al. 2021, *Proof-of-Learning* | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | Proves parameters came from claimed optimisation. Training-integrity, not evaluation-integrity |
| **`arxiv:2608.16891`** 2026, *Aegis runtime governance* | ○ | ○ | ● | ● | ○ | ◐ | ● | ◐ | Mediates agent tool actions, fails closed, records governed-zero counts. Operational side effects, not scientific claims |
| **`arxiv:2601.14971`** *FG-Trac* | ○ | ◐ | ○ | ● | ○ | ○ | ○ | ○ | Already cited. Sample-level lineage |
| **`arxiv:2109.10870`** *SoK: ML Governance* | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ◐ | Systematisation, not a system |
| **`arxiv:2107.01905`** Weytjens & De Weerdt 2021 | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | Leakage-free benchmark *construction*, enforced by procedure not code |
| **CardioSentinel** | ● | ● | ● | ● | ● | ● | ● | ● | — |

### What the matrix costs the paper

**Three of the draft's claims do not survive intact.**

1. **The §2.6 header sentence — "None of them reads the sentence a human will
   actually take away and refuses it because the evidence does not support that
   sentence" — is now false as written.** `arxiv:2509.06902` does exactly that
   for numeric claims, places the verifier in the renderer, and proves
   fail-closed behaviour. It must be cited and the sentence must be narrowed.
2. **Exit property 1 ("the claim, not the computation, is the enforced object")
   is no longer unique.** It is shared with PCN. What remains distinctive is
   *scope*: PCN guards numeric spans; the claim boundary here also carries
   lexical and categorical guards over a closed evidence graph.
3. **"Consumed-attempt semantics" has a literature the draft does not cite.**
   The Ladder and the reusable holdout are the canonical treatments, and their
   design is the *inverse* of CardioSentinel's — they make holdout reuse
   statistically safe, where this system makes it structurally impossible. That
   contrast strengthens the paper; omitting it looks like ignorance of the area.

**Exit property 2 — "one artifact governs two surfaces" — survives the stress
test.** Nothing found governs both a runtime's generated explanation and the
manuscript's own text with the same code. This is now the load-bearing novelty.

---

## 7. REVISED §2.6 NOVELTY STATEMENT

The old formulation ("None of them reads the sentence a human will actually take
away…") is refuted. The strongest **defensible** formulation the search supports:

> Each of these binds a different object. Attestation binds the computation
> [`arxiv:2605.08586`]; provenance chains bind data and environment
> [`arxiv:2601.14971`, `doi:10.3389/fcomp.2026.1735919`]; call-time workflow
> grammars bind the analysis path [`arxiv:2603.10742`]; adaptive-holdout methods
> bind how often a test set may be consulted [`arxiv:1502.04585`,
> `arxiv:1506.02629`]. Claim-level enforcement itself is not new either:
> Proof-Carrying Numbers [`arxiv:2509.06902`] verifies numeric spans against
> structured claims in the renderer rather than the model, and fails closed
> when it cannot. **As far as we are aware, we found no prior system in which a
> single executable claim boundary governs both a deployed runtime's generated
> explanation and the manuscript that reports the system — so that an overclaim
> in either fails against one artifact — within an experimentally enforced
> physiological-AI workflow.** That is a narrower claim than the one this
> section carried in draft, and it is the one the search supports.

**Narrowed from the previous draft in three ways:** claim-level enforcement is
no longer asserted as unprecedented; the *two-surface* property, not the
*claim* property, is now the contribution; and consumed-attempt semantics is
positioned as an inversion of known work rather than as novel.

---

## 8. INTELLIGENT PHYSICAL SYSTEMS COVERAGE — a real gap, now closed

**§2 as drafted contained no IPS literature at all.** No wearable or ambulatory
monitoring, no edge or streaming physiological AI, no trustworthy cyber-physical
systems, no LLM reasoning grounded in physical telemetry. For a TACTiCS
submission under the Intelligent Physical Systems theme, a Related Work that
positions the paper only against ECG classifiers, reproducibility practice and
NLG guardrails leaves the theme fit unargued.

Five verified citations were added as a compact §2.7 — enough to place the
system, not enough to become a healthcare-AI survey:

| key | year | why it is here |
|---|--:|---|
| `arxiv:2107.13767` | 2021 | textile-sensor ECG streamed to a 5G edge device for continuous analysis — the physical-digital loop CardioSentinel sits in |
| `arxiv:2401.12783` | 2024 | scoping review of deep learning on PPG — the wearable-physiology landscape |
| `arxiv:2401.06866` | 2024 | Health-LLM: LLM health inference over wearable sensor data — the generated-language surface applied to physiology |
| `arxiv:2605.29483` | 2026 | VitalAgent: tool-augmented agent doing reactive **and proactive** monitoring over ECG/PPG streams — the closest system-level neighbour |
| `arxiv:2405.06347` | 2024 | review of trust in AI-driven CPS decision-making — the trust framing for physical systems |

---

## 9. REMAINING CITATION RISKS

1. **29 keys are cited as preprints without a confirmed venue.** Twelve
   published versions were recovered from Crossref; the rest could not be
   checked because Crossref does not index NeurIPS/ICML/ICLR. Several
   (S4 `2111.00396`, calibration `1706.04599`, SelectiveNet `1901.09192`,
   RAG `2005.11401`, Datasheets `1803.09010`) are near-certainly published and
   should be cited to their proceedings. **This is a bibliography task before
   submission, and it is the largest remaining item.**
2. **Claim support was checked against abstracts and bibliographic records, not
   full texts.** For the ten exact matches in §2.1 the abstract carries the
   claimed number verbatim, so the risk is low. It is not zero for the
   landscape statements.
3. **Two 2026 preprints are load-bearing** (`arxiv:2605.08586`,
   `arxiv:2603.10742`) and neither is peer-reviewed. `2603.10742` also makes its
   own priority claim ("the first call-time-enforced evaluate/assess
   boundary"), which is asserted, not adjudicated. The manuscript should cite it
   without endorsing its priority claim.
4. **The novelty statement is a negative claim over a targeted search**, now 83
   queries rather than 65. It is not a systematic review and §2.6's hedge
   ("as far as we are aware") is doing real work. Keep it.
5. **`doi:10.2172/826602`** is a DOE technical report — authoritative for blind
   analysis practice, but grey literature; it is one of three citations for that
   point and the other two are journal articles, so the load is carried.

---

## 10. EXACT EDITS APPLIED TO §2

See §11 for the diff. Seven edits, all evidence-driven:

| # | § | change |
|---|---|---|
| E1 | header | added a pointer to this document as the citation-status record |
| E2 | 2.2 | **O2** — "systematically" no longer shared across both surveys |
| E3 | 2.3 | **O4** — NeurIPS programme report described, not credited with measurement |
| E4 | 2.3 | **O3** — ML4H claim narrowed to accessibility, sample size stated |
| E5 | 2.5 | **O1** — "unavoidable" → "recurring" |
| E6 | 2.6 | prior art added (`2603.10742`, `2509.06902`, `1502.04585`, `1506.02629`); the refuted sentence narrowed; exit properties 1 and 3 narrowed; `2605.19755` replaced by its published DOI |
| E7 | 2.7 | new subsection — Intelligent Physical Systems context, five verified citations |

Structure, voice and all surviving prose are unchanged. §2.1, §2.4 and the
positioning paragraphs of §2.2 and §2.3 were not touched.

---

## 11. OUTPUT SUMMARY

| # | item | result |
|---|---|---|
| 1 | total citations audited | **77** (44 arXiv · 20 DOI · 13 PubMed) |
| 2 | verified | **77 / 77** — 48 `VERIFIED — PRIMARY`, 29 `PREPRINT — VERIFIED`; **0 fabricated, 0 unresolvable** |
| 3 | removed / replaced | **1 replaced** (`arxiv:2605.19755` → `doi:10.3389/fcomp.2026.1735919`); **0 removed**; **9 added** (4 prior art + 5 IPS) |
| 4 | unsupported drafted claims | **4 overstatements** (O1–O4), all narrowed; **1 refuted** — §2.6's "none of them reads the sentence" |
| 5 | EDB/LTSTDB status | **not in the live draft; untraceable to a primary source; not directly comparable (2 h vs 24 h records, different annotation protocols, different denominators). Do not reintroduce.** Permitted wording given in §3 |
| 6 | closest prior work matrix | §6 — 11 works; `arxiv:2603.10742` and `arxiv:2509.06902` are the closest and were both missing |
| 7 | revised §2.6 novelty wording | §7 — narrowed to the two-surface property |
| 8 | exact edits | §10, seven edits |
| 9 | remaining risks | §9, five; the venue-confirmation backlog is the largest |
| 10 | submission-ready? | see below |

---

## 12. THE ELEVEN NEW KEYS, AND WHY `verify` NOW REPORTS THEM

`scripts/literature_search.py verify` reports **11 unresolved** after this
audit. That is expected and it is not a defect. Its own message states the rule:

> "Unresolved citations are not necessarily invented — a source read outside the
> registered queries is legitimate — but each one must be justified in the
> search record before it reaches the manuscript."

**`docs/LITERATURE_SEARCH_V1.json` was deliberately not modified.** It is a
`_V1` record carrying a `payload_sha256`; rewriting it to absorb later reading
would destroy the property that makes it evidence. `git diff` confirms the
record and the script are untouched by this task. The justification is recorded
here instead, and a **V2 harvest is required before submission** to close the
gate.

| key | added to | justifying query (this audit, 2026-08-28) |
|---|---|---|
| `arxiv:2603.10742` | §2.6 | `all:"data leakage" AND all:"prevention" AND all:"machine learning"` |
| `arxiv:2509.06902` | §2.6 | `all:"fail-closed" OR all:"policy enforcement" AND all:"model selection"` |
| `arxiv:1502.04585` | §2.6 | `all:"leaderboard" AND all:"overfitting" AND all:"competition"` |
| `arxiv:1506.02629` | §2.6 | `all:"reusable holdout" OR all:"adaptive data analysis" AND all:"holdout"` |
| `arxiv:2608.16891` | §2.6 | `all:"fail-closed" OR all:"policy enforcement" AND all:"model selection"` |
| `doi:10.3389/fcomp.2026.1735919` | §2.6 | published version of the already-registered `arxiv:2605.19755`; resolved directly against Crossref |
| `arxiv:2107.13767` | §2.7 | `all:"edge computing" AND all:"ECG" AND all:"real-time"` |
| `arxiv:2401.12783` | §2.7 | `all:"wearable" AND all:"physiological monitoring" AND all:"deep learning"` |
| `arxiv:2401.06866` | §2.7 | `all:"large language model" AND all:"sensor data" AND all:"physiological"` |
| `arxiv:2605.29483` | §2.7 | `all:"streaming" AND all:"physiological signals" AND all:"continuous monitoring"` |
| `arxiv:2405.06347` | §2.7 | `all:"cyber-physical system" AND all:"trustworthy" AND all:"autonomous"` |

All eleven were resolved against the arXiv API or Crossref in this audit and
appear in the §1 ledger with full bibliographic records.

### A defect in the verifier itself, found while using it

`verify` reports **71 citations**; the section contains **77 unique keys**. The
cause is at `scripts/literature_search.py:445`:

```python
CITATION = re.compile(r"\[((?:doi|arxiv|pmid):[^\]\s]+)\]")
```

`[^\]\s]+` stops at whitespace, so a bracket holding more than one key —
`[doi:10.1016/j.patter.2023.100804, arxiv:2207.07048]`, and five others like it
— matches **nothing at all**, and neither key is checked. **The provenance gate
is silently skipping six brackets.** It is a false negative in the direction
that matters: an invented citation placed second in a shared bracket would pass.
This was not fixed here — changing the verifier is not a Related-Work task and
would alter a check the manuscript's provenance argument depends on — but it
should be fixed before submission, and the section re-verified afterwards.

---

## 12b. THE §6.3 ORDERING CONDITION — CHECKED, AND NOW RECORDED IN §2

`B4_TEST_AUTHORIZATION_V1.md` §6.3 waived §2's completion until manuscript
drafting and attached one condition: **§2, when written, must not be shaped by
the sealed-test result.** The draft honoured this in practice but did not say
so, which meant a reader could not tell compliance from coincidence.

**Mechanical check performed.** The sealed metrics at
`cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/TEST_METRICS.json`
were expanded into **401 numeric surface forms** (raw values, 2–4 decimal
roundings, and percentage renderings), and §2 was searched for each after
stripping citation keys so that DOIs and arXiv identifiers could not produce a
false positive. **No sealed-test value appears in §2.** The single match was
`2026`, a publication year in the citation text.

**The provenance argument is also clean.** §2 derives from
`LITERATURE_SEARCH_V1.json` (harvested 2026-08-25) and from this document.
Neither reads the sealed evaluation. The §2.6 gap statement was narrowed by
`arxiv:2509.06902` and `arxiv:2603.10742` — prior art — and not by any number
this programme produced. The ordering the waiver relies on is intact and its
reason has not become false in retrospect.

The condition is now recorded in the draft's own header, so the next revision
inherits it rather than rediscovering it.

---

## 13. VERDICT

**What is done.** All 77 citations resolve to authoritative records; none is
invented. Four overstatements are narrowed. One refuted novelty claim is
rewritten and the section's contribution is now the two-surface property, which
survived a deliberate falsification search. One preprint is replaced by its
published version. The IPS theme gap is closed with five verified citations. The
EDB/LTSTDB comparison is traced, found untraceable and not directly comparable,
and permitted wording is recorded so it cannot return by accident.

**What blocks submission.**

1. **The provenance gate is red.** `verify` reports 11 unresolved until a V2
   harvest registers the sources in §12. Justified here, not yet in the record.
2. **29 citations carry no confirmed venue.** Twelve published versions were
   recovered; the rest need a proceedings-side check that Crossref cannot do.
3. **The verifier under-counts by six.** The regex at line 445 skips
   multi-key brackets, so part of §2 is not actually being gated.
4. **Claim support was checked at abstract level.** Adequate for the ten
   quote-level matches; not a full-text audit of the landscape statements.
5. **Two load-bearing 2026 citations are unrefereed preprints**, one of which
   (`arxiv:2603.10742`) asserts a priority claim that overlaps this paper's.

None of these is a scientific defect and none requires compute. All five are
bibliography-and-tooling work.

RELATED WORK NOT YET VERIFIED — V2 harvest not run (11 sources justified in §12 but unregistered); 29 citations lack a confirmed venue; the verifier's regex at `scripts/literature_search.py:445` silently skips six multi-key brackets; claim support checked at abstract level only; two load-bearing 2026 citations are unrefereed preprints.
