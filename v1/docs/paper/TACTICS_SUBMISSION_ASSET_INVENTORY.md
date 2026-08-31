# TACTiCS submission — asset inventory

**"In package?" is the column that matters.** Most documents below are the
programme's internal governance record. They are what makes the manuscript's
claims checkable, and **none of them is submitted**. A reviewer receives the
paper and its figures; the audits stay in the repository.

Paths reflect the 2026-08-29 V2 path-only migration under `docs/`.

---

## Manuscript

| Path | Purpose | Status | In package? |
|---|---|---|:--:|
| `docs/paper/CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md` | **content-frozen submission source**, `sha256:78863bcc…60029fe2` | AUTHORITATIVE | **YES** — after template mapping |
| `docs/paper/CARDIOSENTIN_TACTICS_MANUSCRIPT_V3_FINAL_CANDIDATE.md` | same body, without the format banner and metadata block | superseded | no |
| `docs/paper/CARDIOSENTIN_TACTICS_MANUSCRIPT_V2_BODY_FROZEN.md` | body freeze, pre-abstract | history | no |
| `docs/paper/CARDIOSENTIN_TACTICS_MANUSCRIPT_V1.md` | first assembly | history | no |
| `docs/paper/MANUSCRIPT_V2_ASSEMBLY_PROVENANCE.md` | where each section came from | internal | **no** |

## Figures — F1–F5 submitted, F6 deliberately absent

| Path | Purpose | Status | In package? |
|---|---|---|:--:|
| `docs/paper/figures/F1_ips_architecture.pdf` | four-layer IPS architecture | **vector, submission** | **YES** |
| `docs/paper/figures/F2_partition_authority.pdf` | partition authority, one-way spend | **vector, submission** | **YES** |
| `docs/paper/figures/F3_episode_reasoning.pdf` | T1 vs W1, per-subject and paired | **vector, submission** | **YES** |
| `docs/paper/figures/F4_representation_geometry.pdf` | class-direction geometry, 3/79 negatives | **vector, submission** | **YES** |
| `docs/paper/figures/F5_guarded_generation.pdf` | three gates passed, fourth refused | **vector, submission** | **YES** |
| `docs/paper/figures/F*.png` (5) | 200 dpi previews | preview | no — unless the venue requires raster |
| `docs/paper/figures/make_f1_f2_f5.py`, `make_f3_f4.py` | generators | source | no — unless artifact submission is offered |
| `docs/paper/figures/README.md` | figure provenance, palette validation | internal | **no** |

**F6 does not exist and is not missing.** §9 records the decision and its reasoning.

## Tables

| Asset | Purpose | In package? |
|---|---|:--:|
| T1 · system components and retention decisions | governance made concrete before results | **YES** (embedded) |
| T2 · primary quantitative results | every headline number with its denominator | **YES** (embedded) |
| T3 · personalization / uncertainty / governance gates | gates written before outcomes, two of which said no | **YES** (embedded) |
| T4 · negative findings and required wording | the credibility table | **YES** (embedded) |
| `docs/paper/PAPER_TABLES_T1_T4_DRAFT.md` | source draft with assembly notes | **no** |

## Bibliography

| Asset | Purpose | Status | In package? |
|---|---|---|:--:|
| 87 unique bibliographic works | 108 keys · 87 unique keys · **0 unresolved** | **VERIFIED** | **YES** — as a formatted reference list, once the style is known |
| `docs/literature/LITERATURE_SEARCH_V1.json` | 65-query harvest, `payload_sha256 dd479319…` | **frozen evidence** | **no** |
| `docs/literature/LITERATURE_SEARCH_V2.json` | 97-query harvest, `payload_sha256 cd1dbfcf…` | **frozen evidence** | **no** |
| `scripts/literature_search.py` | harvester and citation verifier | tooling | no |

## Control documents — none submitted

| Path | Purpose | In package? |
|---|---|:--:|
| `docs/paper/ABSTRACT_CLAIM_AUDIT_V1.md` | every abstract claim mapped to body and authority | **no** |
| `audits/CARDIOSENTINEL_PAPER_READINESS_AUDIT_V1.md` | claim matrix, limitations matrix, red lines | **no** |
| `audits/CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md` | first citation audit | **no** |
| `audits/CARDIOSENTIN_RELATED_WORK_VERIFICATION_V2.md` | verifier fix, V2 harvest, venues, prior-art matrix | **no** |
| `audits/CARDIOSENTIN_SUBMISSION_FORMAT_REVIEW_V1.md` | reviewer simulation, rejection pass | **no** |
| `audits/TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md` | the negative record of the rules search | **no** |
| `docs/paper/TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md` | human input form | **no** |
| `docs/paper/TACTICS_OFFICIAL_INSTRUCTIONS_NEEDED.md` | questions for the organisers | **no** |
| `docs/handoffs/` | session handoff chain, ECG3–ECG24 | **no** |

## Not in the repository, and required before a package exists

| Missing | Blocks |
|---|---|
| Official template / author instructions | the entire layout |
| Author block, affiliations, declarations | the title page |
| A rendered artifact in the required file type | submission itself |

---

**Submitted: one manuscript, five vector figures, four embedded tables, one
formatted reference list. Everything else stays here.**
