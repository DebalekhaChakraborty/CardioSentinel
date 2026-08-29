# Repository documentation — layout

Everything is categorised except the seven T1 documents, which are flat for a
reason recorded below.

## Top level

| Directory | Holds | Files |
|---|---|--:|
| `paper/` | the manuscript, its section drafts, figures, tables, abstract claim audit, submission metadata | 31 |
| `audits/` | paper-readiness, Related Work, submission-format, runtime-boundary and documentation/demo reconciliation audits | 8 |
| `handbook/` | the research execution handbook, all versions, `.md` and `.docx` | 10 |
| `handoffs/` | the session handoff chain, ECG3–ECG24 | 23 |
| `docs/` | the experiment record and control plane, categorised below | 104 |

## Inside `docs/`

| Directory | Holds | Files |
|---|---|--:|
| `docs/experiments/b4/` | the B4 encoder: protocol, selection, sealed-test authorization, and the E1–E13a investigations | 35 |
| `docs/experiments/m1/` | patient-relative memory: protocols, failures, retention decision | 7 |
| `docs/experiments/m2/` | the contamination-safe update gate | 8 |
| `docs/experiments/t2/` | longitudinal temporal arm: protocol, plans, comparison, retention | 7 |
| `docs/experiments/u1/` | calibration and the rejected selective router | 4 |
| `docs/experiments/w1/` | the memoryless window comparator | 2 |
| `docs/experiments/p1/` | physiology fusion | 2 |
| `docs/contracts/` | dataset, experiment and signal-processing contracts; split policy; metrics and annotation semantics; baseline and benchmark protocols | 8 |
| `docs/control-plane/` | current state, experiment catalogue, evidence map, research scope, architecture, plans, roadmap, repo audit | 8 |
| `docs/provenance/` | commit-pin and document-path translation, the provenance incident, cross-dataset provenance, the runtime integrity sentinel | 5 |
| `docs/explanation/` | explanation evaluation protocol and report, local-LLM protocol, Qwen run contract, demo scenario | 5 |
| `docs/external-validation/` | the Route A decline and the strategy that preceded it | 2 |
| `docs/literature/` | the two frozen literature-search harvests | 2 |
| `docs/baselines/` | classical baseline results | 1 |
| `docs/` itself | the seven T1 documents — **deliberately flat**, see below | 7 |

## Why the T1 documents are flat

`docs/T1_*.md` and `docs/t1_episode_reasoning.md` were the one category the
reorganisation could not take.

The T1 canonical driver's source files are frozen by SHA-256:
`tests/neural/test_t1_*.py` assert that `src/cardiosentinel/neural/t1_*.py` are
byte-identical to recorded digests, and those files construct the document
paths. Repointing them at `docs/experiments/t1/` is a correct path fix and
**still a byte change**, so it fails the freeze — sixteen tests, by design. The
guard exists so the executed protocol cannot drift underneath its record.

Amending the digests is possible; `docs/T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md`
is the precedent for how. It costs a human authorisation and an amendment
document, and **tidying a directory does not justify one**. If T1 source has to
change for a scientific reason, move these seven documents in the same
amendment and record them in the translation table.

## Before you move a document

**Eight of these documents are named by path inside promoted artifacts under
`cardiosentinel-runs/`**, including the sealed single-use test evidence. Those
artifacts are immutable and still record the pre-2026-08-28 paths.
`docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md` maps every old path to its
current one, and is how a stale pointer in frozen evidence resolves.

If you move something else, add it to that table. The check is one command:

```
grep -roh 'docs/[A-Za-z0-9_.-]*' cardiosentinel-runs --include=*.json | sort -u
```

Every path it prints must appear in the translation table.

## Before you edit a document's content

**38 documents are digest-pinned — and only 29 of those are pinned by code.**
The other nine are pinned *by other documents*: a decision record quotes the
SHA-256 of the protocol it decided on, a report quotes the digest of the plan it
executed. **No test fails when one of those is edited.** The break is silent and
only shows up when someone re-derives the chain.

The full set is whatever this produces — hash every document, then look for that
digest anywhere else in the repository:

```python
# for each file under docs/, paper/, audits/, handbook/:
#   h = sha256(file); if h appears in src/, tests/, scripts/, configs/,
#   protocols/, recovery/, reproducibility/, cardiosentinel-runs/*.json,
#   or in any OTHER document -> that file's bytes are frozen.
```

Nine documents currently carry stale internal paths for exactly this reason and
were deliberately left alone: `B4_GLOBAL_ENCODER_SELECTION_V1.md`,
`B4_TEST_DEFERRAL_DECISION_V1.md`,
`T2_ARM_COMPARISON_ANALYSIS_PLAN_AMENDMENT_V1_1.md` and
`EXTERNAL_VALIDATION_STRATEGY_V1.md` among them. The translation table
resolves them.

**A provenance generator is also a document's content.**
`scripts/provenance/gen_*.py` emit path strings *into* reports that must
regenerate byte-for-byte, so an emitted string is as frozen as the report.
Where a constant is both emitted and opened, it is split in two — see
`AMENDMENT` and `AMENDMENT_PATH` in `gen_t2_arm_comparison_report.py`.

## Two more things that were deliberately left alone

**`docs/literature/LITERATURE_SEARCH_V2.json`** records
`"supersedes": "docs/LITERATURE_SEARCH_V1.json"` inside its hashed payload.
Correcting that string would change `payload_sha256` — the digest that makes it
evidence rather than a file. The pointer is stale by design; the translation
table resolves it.

**The handoffs and the superseded handbook versions** are byte-identical to
their committed form. A stale path in a historical document is a broken link,
not a false statement, and corrections belong in the current control plane.
