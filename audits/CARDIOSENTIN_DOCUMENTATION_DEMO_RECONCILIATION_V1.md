# CardioSentinel documentation relocation and demo reconciliation, V1

**Date:** 2026-08-29

**Branch:** `feat/e11-e13a-instrumentation-and-paper-readiness`

**HEAD:** `1bf366e66739f2990012d05c702a4d78400a06da`

**GitHub base:** `master` at
`2da1fe695bcec57a4f529b0d97d8a7c0b0a2ce6c` (PR #128 merged)

**Open pull requests:** PR #129 only at the time of reconciliation

**Interpreter:** `/home/AI_POC/venvs/tactics/bin/python`

## Scope and freeze

This was a repository-coherence task. It did not authorize or perform an
experiment, training, rescoring, threshold derivation, sealed TEST access,
scientific-result modification, manuscript rewrite, or runtime refactor. The
runtime implementation and tests present in the final worktree are the input
from the preceding Runtime Trust-Boundary Hardening V1 task; this task did not
alter those files.

## 1. Authoritative final directory structure

The authoritative publication and governance directories are at repository
root:

| Directory | Final file count | Purpose |
|---|---:|---|
| `paper/` | 31 | manuscript, drafts, figures, tables and submission metadata |
| `handbook/` | 10 | all handbook versions, Markdown and DOCX |
| `handoffs/` | 23 | ECG3 through ECG24 and the handoff index |
| `audits/` | 8 | independent audit and reconciliation records, including this one |
| `docs/` | 104 | categorized experiment, contract, control-plane and provenance records |

This layout was selected because all four governing authorities agree:

1. PR #129 describes the root-level hoist;
2. the latest handoff, ECG24, inventories the same root directories;
3. `DOCUMENT_PATH_TRANSLATION_V1.md` maps the temporary/nested paths to the
   root-level destinations; and
4. committed HEAD contains the root-level files.

PR #128 was confirmed merged. PR #129 was confirmed open at the exact working
HEAD. No newer human-authorized record superseded the organization, so there
was no stop-gate conflict.

## 2. Files restored and byte identity

The initial worktree held 64 tracked deletions under `paper/`, `handbook/` and
`handoffs/`, plus 64 untracked counterparts under `docs/paper/`,
`docs/handbook/` and `docs/handoffs/`. Every counterpart was compared with the
corresponding committed root file before movement:

| Tree | Files restored | Byte mismatches before restore | Byte mismatches after restore |
|---|---:|---:|---:|
| `paper/` | 31 | 0 | 0 |
| `handbook/` | 10 | 0 | 0 |
| `handoffs/` | 23 | 0 | 0 |
| **Total** | **64** | **0** | **0** |

The nested directories were moved back to their authoritative root locations.
Because their bytes and final paths now match committed HEAD, the repair leaves
no artificial 64-file relocation diff.

## 3. Path-translation and live-reference audit

The translation document contains 95 literal old-to-current file mappings.
All 95 current files exist. Its additional hoisted-directory patterns match the
root structure above.

The eight distinct old document paths found inside immutable JSON evidence
under `cardiosentinel-runs/` exactly match the translation table's first eight
rows. No artifact was edited. The seven digest-constrained T1 documents remain
flat in `docs/`; no source hash or frozen T1 path was changed.

A tracked-text scan found 193 occurrences of old mapped paths outside the
translation document. The ten occurrences on code/test/living-document
surfaces were all intentional:

- three are in a frozen test fixture;
- six are archival provenance-generator strings emitted into frozen reports;
- one is the current `docs/README.md` explanation of the intentionally stale
  literature payload.

The remaining occurrences are historical, frozen or superseded records. There
was no unclassified live stale path. The only broken live Markdown target found
after the move was the relative `legacy/v0/` link in the relocated historical
repository audit; its target was corrected from one directory too shallow to
`../../legacy/v0/README.md`.

## 4. Living-state corrections

`docs/control-plane/CURRENT_STATE.md` was regenerated where state is live. It
now records:

- PR #128 merged and PR #129 open;
- the current branch, HEAD and GitHub base;
- handbook v1.5;
- the 14,415-word content-frozen manuscript candidate;
- the root-level repository organization and current file/code/test counts;
- 3,566 collected tests;
- the completed runtime trust-boundary hardening;
- explicit deterministic/local/hosted provider semantics; and
- official TACTiCS instructions/template plus human metadata as the remaining
  submission blockers.

Historical scientific values were preserved as historical facts and were not
recomputed.

`docs/README.md` now carries the actual top-level counts. The provenance-script
index now records the post-relocation T2 generator digest
`a516095b7686124dc879250bb184a5d5c425d88782111440d846cd8465d25daa`.
That generator intentionally emits its historical plan/amendment paths while
opening the translated current amendment path.

## 5. README and installation contract

The README changes are limited to objective reconciliation:

- handbook v1.4 became v1.5;
- the manuscript is content-frozen and format-pending rather than unwritten;
- the sealed-test check now requires exactly one consumed attempt and no
  repeat, rather than claiming the test was never opened;
- evidence-graph example output distinguishes a manifest-verified runtime
  artifact from an experiment lock unavailable in the demo bundle;
- provider selection and data egress are stated factually; and
- the demo installation includes the `neural` extra because checkpoint loading
  imports `torch`.

The minimum documented demo installation is therefore:

`pip install -e ".[dev,data,signal,ml,neural]"`

This was verified from a clean `git archive` in a disposable virtual
environment. Installed dependencies from tactics were exposed read-only to
avoid network access and to avoid modifying tactics. Editable installation with
all documented extras succeeded; `cardiosentinel`, `torch` 2.13.0+cpu and
`wfdb` 4.3.1 imported; the imported CardioSentinel source resolved to the clean
archive; and `cardiosentinel --help` succeeded. The disposable environment was
removed. No package in tactics was installed, removed or upgraded.

## 6. Demo and provider contract

The authoritative scenario is the tested 2,400-second replay. README,
`RUN_DEMO.md`, `DEMO_SCENARIO.md`, the runtime and
`test_demo_scenario.py` now agree on:

- 479 windows over 40 simulated minutes;
- one EVENT, `00:17:05 -> 00:27:45`;
- 640 seconds and 129 windows in that event;
- peak calibrated probability `0.545613`; and
- zero admitted memory updates.

Wall time and real-time factor are explicitly machine-dependent. A longer
replay is explicitly a different, uncontracted scenario.

Provider documentation matches the hardened runtime:

- `deterministic` is the default, makes no model call and has no model-data
  egress;
- `local` is an explicit pinned local-cache choice with no hosted fallback;
- `gemini` is an explicit hosted choice and sends the structured evidence
  context off-machine; and
- `GOOGLE_API_KEY` authenticates an explicit Gemini choice but never selects
  it by itself.

No privacy or compliance claim was added.

## 7. Link integrity

A local-link scan covered README and every Markdown file under `docs/`,
`paper/`, `handbook/`, `handoffs/`, `audits/` and `reproducibility/`.

| Measure | Result |
|---|---:|
| Markdown files scanned | 161 after this report was added |
| Local Markdown links checked | 42 |
| Broken live links | **0** |
| Intentionally historical unresolved Markdown links | **0** |
| External links excluded from the local-target gate | 14 |

Historical non-link path strings are handled by the translation audit in §3,
not misreported as live Markdown links.

## 8. Generator reproducibility

No provenance generator was edited in this task and no final diff touches a
frozen generated scientific report.

- `gen_t1_post_hoc_analysis.py` regenerated to scratch and matched the tracked
  report byte-for-byte.
- `gen_u1_reliability_report.py` regenerated to scratch; the sole diff was its
  documented generated-at commit stamp. All scientific/report content matched.
- `gen_t1_descriptive_report.py` retains an archival absolute path to an older
  checkout name and could not run directly from this checkout. It was not
  relocation-affected, was not edited, and its report was not overwritten.
- The relocation-aware T2 and W1 generators were not rerun because they perform
  governed rescoring/reopening that this task expressly does not authorize.
  The organization commit records their relocation verification, and their
  sources have not changed since that commit. Their historical emitted path and
  current opened path remain explicitly separated.

The four source digests recorded in `scripts/provenance/README.md` now match the
four current files. No frozen report regenerated differently beyond an
authorized execution stamp.

## 9. Scientific and manuscript integrity

| Frozen item | SHA-256 before | SHA-256 after |
|---|---|---|
| Final manuscript candidate | `78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2` | `78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2` |
| Handbook v1.5 Markdown | `78780c4033edfbc8260d6fa280723e0d074e5af841154e81832ebc8a06f9c5fc` | `78780c4033edfbc8260d6fa280723e0d074e5af841154e81832ebc8a06f9c5fc` |
| Related Work V2 verification | `7273183c97d915571b7e16ee865ee5edac97afed080f0a46d95bf46631aded61` | `7273183c97d915571b7e16ee865ee5edac97afed080f0a46d95bf46631aded61` |
| Literature search V1 JSON | `166f25f76b3cfd6966b15d8b0e2340deb72cce18c4ae01e2b2e85911e59b90d1` | `166f25f76b3cfd6966b15d8b0e2340deb72cce18c4ae01e2b2e85911e59b90d1` |
| Literature search V2 JSON | `f9a1b681315a541feef1a6c12c8debaeba447c8349b253124ac0560bc948679b` | `f9a1b681315a541feef1a6c12c8debaeba447c8349b253124ac0560bc948679b` |
| Runtime-hardening report | `3809ed1da98448156ecc1db2c41d6c9b24d58df5aa23cd6b25750c0edbdfacab` | `3809ed1da98448156ecc1db2c41d6c9b24d58df5aa23cd6b25750c0edbdfacab` |

The required manuscript digest is unchanged. No frozen scientific document,
run artifact, checkpoint, metric, interval, threshold, attempt budget or
manuscript scientific prose changed.

## 10. Verification results

The required order was followed:

| Gate | Result |
|---|---|
| Literature citation extraction | 22 passed |
| Documentation/path focused tests | 60 passed |
| Reproducibility suite | 36 passed |
| Edge suite | 53 passed |
| Agent suite | 193 passed |
| Runtime trust-boundary focused tests | 72 passed |
| `ruff check .` | all checks passed |
| `git diff --check` | clean |
| Full `pytest tests -q` | **3,565 passed, 1 skipped, 0 failed**, 15 warnings, 1,104.83 s (18:24) |

The first full invocation exposed a stale local environment inherited from the
repository rename: source code objects referred to the former
`Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` path, and subprocesses
could not follow the tactics editable-install pointer to that absent directory.
That invalid run produced nine environmental failures. All nine nodes passed
when rerun with the current absolute `src/` path and a fresh disposable bytecode
cache. The authoritative complete rerun used those same non-mutating settings
outside the managed sandbox (required for the already-confirmed PyTorch worker
constraint) and produced the result above. Tactics itself was not modified.

## 11. Final diff classification and status

| Class | Files/actions |
|---|---|
| A — relocation/path repair | 64 files restored to root with no residual content diff; `docs/control-plane/REPO_AUDIT.md`; relocation-aware generator digest record |
| B — living-state documentation | `README.md`; `docs/README.md`; `docs/control-plane/CURRENT_STATE.md`; this audit |
| C — demo documentation reconciliation | `README.md`; `reproducibility/RUN_DEMO.md` |
| D — test path repair | none; restoring the authoritative file path fixed the literature test without weakening or editing it |
| E — unintended | **0** |

The remaining modified runtime and runtime-test files are exactly the preceding
trust-boundary-hardening task's reviewed scope:
`src/cardiosentinel/{agents,edge}/`, two agent tests,
`tests/edge/test_runtime_trust_boundary.py`, and its authoritative runtime audit.
No such file changed during this reconciliation.

The final worktree has no deletion/untracked-copy pair for `paper/`,
`handbook/` or `handoffs/`. It contains only the predecessor runtime-hardening
changes plus the five living/path/demo records, the provenance index correction,
and this audit. One stale stash remains deliberately unpopped, as documented in
`CURRENT_STATE.md`; there is one worktree.

## 12. Remaining blockers

Repository/document/demo coherence has no remaining blocker. Submission itself
still requires official TACTiCS 2026 instructions/template and human-controlled
metadata (authors, affiliations and venue declarations). Edge-hardware
evaluation and external validation remain scientifically open and unauthorized;
they are not PR #129 merge blockers.

DOCUMENTATION AND DEMO RECONCILED — REPOSITORY READY FOR PR #129 FINAL REVIEW
