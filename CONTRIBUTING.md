# Contributing to CardioSentinel

Keep changes small, reviewable, and tied to a documented research question.
Read `AGENTS.md`, `docs/control-plane/RESEARCH_SCOPE.md`, and
`docs/contracts/EXPERIMENT_CONTRACT.md` before changing research logic.

Do not commit raw ECG, patient-derived data, credentials, checkpoints, or
experiment outputs. Add or update tests for behavior changes, then run:

```bash
python -m ruff check .
python -m pytest -q
```

Document assumptions, data provenance, and unresolved decisions in the relevant
configuration or documentation change. Do not modify the locked `legacy`
branch or `archive/legacy-v0-tree` tag, or restore their contents to the active
tree, without an explicit archival and data-governance task.

## Publication work belongs outside this repository

This repository is a **computational research artifact**: implementation,
protocols, measured results, decisions and provenance. It should be
understandable, runnable and verifiable by someone who has never heard of any
particular venue.

Venue-specific work therefore lives in a separate workspace — for example
`../publications/CardioSentinel/` — and is never added to Git:

- DOCX manuscripts and final PDFs
- conference-specific figure variants and templates
- reviewer notes and response drafts
- submission metadata, author lists, affiliations
- formatting and page-limit experiments

`.gitignore` carries a narrow set of patterns (`publication-local/`,
`submission-local/`, `paper-drafts/`, `*_TACTiCS_*.docx`, `*.submission.pdf`,
`*_review_notes.md` and similar) that stop such files being tracked by accident.
Those patterns are deliberately specific: there is no blanket `*.docx`, `*.pdf`
or `*.md` rule, because the research handbook ships as `.docx`, the evidence
visualizations ship as `.pdf`, and nearly every scientific record here is `.md`.

**`.gitignore` only affects untracked files.** Material already committed —
including the historical long-form write-up under `docs/paper/` — stays in the
tree and in history until a separate, explicitly authorized change removes it.
Nothing in the repository depends on that material, and no scientific value is
sourced from it.
