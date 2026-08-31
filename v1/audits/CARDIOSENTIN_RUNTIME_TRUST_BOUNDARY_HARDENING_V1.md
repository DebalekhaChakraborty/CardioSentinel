# CardioSentinel Runtime Trust-Boundary Hardening V1

Date: 2026-08-29

Branch: `feat/e11-e13a-instrumentation-and-paper-readiness`

Starting HEAD: `1bf366e66739f2990012d05c702a4d78400a06da`

## Outcome

All four reported runtime trust-boundary findings are **CLOSED**. Replay now
distinguishes authoritative EOF from read failure, every inference artifact is
identity checked before deserialization/use, graph lineage reserves
`frozen_by` for verified records, and hosted generation requires explicit user
selection.

Scientific work remained frozen. No training, rescoring, threshold derivation,
TEST access, metric recomputation, or scientific artifact edit occurred.

## Baseline defects reproduced

Tests were written before the fixes. Five characterization cases passed against
the old behavior and demonstrated:

1. an unexpected waveform-reader exception became apparent EOF;
2. a mutated but loadable runtime artifact loaded when the separate bundle
   verifier was omitted;
3. an absent experiment lock still received `frozen_by`;
4. `GOOGLE_API_KEY` plus an available SDK implicitly selected Gemini; and
5. `strict_local=True` could still reach Gemini.

The characterization expectations were then changed to the required hardened
semantics; eight tests failed before implementation, providing the red phase.

## Files changed by this task

- `src/cardiosentinel/edge/replay.py`
- `src/cardiosentinel/edge/artifacts.py`
- `src/cardiosentinel/edge/cli.py`
- `src/cardiosentinel/agents/graph.py`
- `src/cardiosentinel/agents/providers.py`
- `src/cardiosentinel/agents/cli.py`
- `tests/edge/test_runtime_trust_boundary.py` (new)
- `tests/agents/test_evidence_graph.py`
- `tests/agents/test_local_qwen_provider.py`
- `audits/CARDIOSENTIN_RUNTIME_TRUST_BOUNDARY_HARDENING_V1.md` (this report)

The pre-existing tracked deletions under `paper/`, `handbook/`, and `handoffs/`
and their untracked replacements under `docs/` were not modified or repaired.

## Replay semantics: before and after

Before, `stream_windows()` probed for EOF by reading until an exception and
converted every reader exception to normal termination. Corruption,
permissions, channel, calibration, and genuine EOF were therefore
indistinguishable.

After, replay reads WFDB header bounds once, validates the 250 Hz record
contract and channel count, validates sample-aligned non-negative/positive
arguments, and advances only by a positive chunk. Exact EOF is a metadata
boundary. A final short read is passed to the causal generator; complete
10-second windows are emitted, while an incomplete residual is neither padded
nor interpolated. Waveform failures raise `ReplayReadError` with record,
channel, requested sample interval, and chained original exception.

## Runtime artifact integrity chain

The controlled loader emits a `RuntimeArtifactVerification` for every direct
inference artifact. The table below records the contracted demo subject
`ltstdb:s2020`; all observations equalled the expected identities.

| Component | Expected SHA-256 | Expected digest source | Verification mechanism | Status |
|---|---|---|---|---|
| B4-B encoder | `b1301723909c641a0014c31f6daa9549d47ab231f0b07483e0de729aff5591c9` | `DEMO_BUNDLE_SELECTION.json`; research tier: B4-B experiment lock | runtime manifest / experiment lock | verified |
| P1-B physiology transform | `b4fe6dd80c511fa6d9f2750f268f69a0ae9fe4a14181deb8398fe3ab0b5e32fc` | demo manifest; research tier: P1-B experiment lock | runtime manifest / experiment lock | verified |
| M1L memory scorer | `a26b6a18db8c005a051054417156068174a166062a5498f32fd48e473ad58510` | demo manifest; research tier: M1L experiment lock | runtime manifest / experiment lock | verified |
| M1 distance standardizer | `2b0166a1a90a39ba15e11ea2771f782e40c63f7a818883b57d1b7ab3a2421a53` | demo manifest plus M1L lock's canonical-payload digest | manifest + canonical payload + experiment lock | verified |
| U1 calibrator | `acec97c1ebd3bed459ad2d75204b6c82f274b248edbb1d779b844bd46c62fdc1` | demo manifest; research tier: U1 experiment lock | runtime manifest / experiment lock | verified |
| T2 S4D checkpoint | `63ccfbe00c209f94124610f1a22b25d84a2ad2b7e941ecaa3f0c8e9684a6722e` | demo manifest; research tier: T2 checkpoint lock | runtime manifest / checkpoint lock and safe weights-only load | verified |
| T1 fold-03 policy | `daa0e1def15d45cc826516b8478369c92755ec77634429014580161ed7d6d7ed` | demo manifest; research tier: frozen predecessor selection receipt | runtime manifest / selection receipt plus subject-policy identity | verified |

The demo loader verifies every manifest entry before any deserializer runs; a
caller does not have to remember to invoke the standalone verifier. The
research-tree loader reuses existing experiment/checkpoint locks and selection
receipts. No expected digest was invented. Missing artifacts, missing expected
digests, digest mismatches, and digest-consistent wrong identities are all
tested refusals.

Runtime provenance now exposes component, logical artifact identifier,
canonical path, expected and observed SHA-256, expected-digest source,
verification mechanism, and status. It also exposes direct M1L, U1, T2, and T1
identities and an aggregate `runtime_integrity_verified` value.

## Evidence graph semantics: before and after

Before, graph construction added a lock node and `frozen_by` edge even when
`lock_available` was false, and the human summary hid that contradiction.

After, a lock is parsed and its canonical experiment/checkpoint self-digest is
verified. Only a verified lock receives `frozen_by`. An absent or unverifiable
record receives `provenance_unavailable`, and the human summary says whether
the experiment lock is unavailable, present but unverified, or verified.
Artifact lines separately state whether their digest was verified through a
runtime manifest, experiment/checkpoint lock, or selection receipt.

## Provider selection and data-egress policy

Before, generic Google credentials could implicitly select Gemini, including
from a supposedly strict-local path.

After, the default is deterministic. Provider selection is explicit through
`--provider deterministic|local|gemini` or the dedicated
`CARDIOSENTINEL_LLM_PROVIDER` configuration. `GOOGLE_API_KEY` authenticates an
explicit Gemini choice but never selects it. `--no-generative` is mutually
exclusive with `--provider` and always uses the deterministic renderer.
`strict_local=True` refuses hosted choices and raises if an explicitly
requested local provider cannot initialize; local failure never falls back to
hosted generation.

The boundary is documented in code and CLI help:

- deterministic: no model call and no data egress;
- local: pinned, locally cached model/process only, with no hosted fallback;
- Gemini: hosted; the structured physiological/evidence context leaves the
  local machine.

No hosted call was made and no project evidence was sent to Gemini. No legal or
regulatory compliance claim is made.

## Demo compatibility

The committed 27-file demo bundle passed its manifest verification. The locally
available contracted 2400-second `s20201` scenario passed unchanged in the edge
suite: one EVENT run, `00:17:05 -> 00:27:45`, 640 seconds across 129 windows,
peak `p_t` `0.545613`, and zero admitted memory updates. This was a replay of
the existing reproducibility contract, not a new scientific endpoint.

## Verification results

The requested order was followed:

| Check | Result |
|---|---|
| Focused replay | 7 passed |
| Focused artifact loader/integrity | 8 passed |
| Graph/lineage | 16 passed |
| Provider/CLI, including guarded Qwen behavior | 41 passed |
| Complete edge suite | 53 passed |
| Complete agent suite | 193 passed |
| Reproducibility suite | 35 passed, 1 failed (pre-existing relocation path; details below) |
| `ruff check .` | all checks passed |
| `git diff --check` | clean |
| Full `pytest tests -q` | 3564 passed, 1 skipped, 1 failed, 15 warnings |

The first sandboxed full-suite attempt stalled at a PyTorch persistent-worker
test. The exact node passed in 3.80 seconds outside the managed sandbox,
confirming a sandbox multiprocessing limitation. The authoritative full rerun
therefore used the same tactics interpreter outside that boundary:

- start: `2026-08-29T11:49:17Z`;
- observed end: `2026-08-29T12:08:09Z`;
- pytest duration: `1112.91s` (`18m32s`);
- result: `3564 passed, 1 skipped, 1 failed`.

The sole failure was
`tests/reproducibility/test_literature_citation_extraction.py::test_the_live_section_has_no_hidden_keys`.
It reads the tracked legacy path `paper/PAPER_S2_RELATED_WORK_DRAFT.md`, which
is absent because the unrelated in-progress relocation currently has that
tracked file deleted and an untracked byte-equivalent replacement under
`docs/paper/`. Fixing or masking that test would repair the expressly
out-of-scope relocation, so this task leaves it visible and unresolved. No
runtime-hardening test failed.

## Scientific and manuscript integrity

- Manuscript SHA-256 before: `78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2`.
- Manuscript SHA-256 after: `78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2`.
- No task diff touches `cardiosentinel-runs/`, frozen scientific protocols or
  reports, checkpoints, metric values, selection thresholds, experiment
  budgets, or manuscript quantitative claims.
- The existing relocation remains isolated and byte-preserving for the
  manuscript checked above.

## Finding classification and remaining blockers

| Original finding | Classification |
|---|---|
| Reader failures converted to EOF | **CLOSED** |
| Incomplete runtime artifact digest chain | **CLOSED** |
| False `frozen_by` lineage for absent locks | **CLOSED** |
| Implicit Gemini / ineffective strict-local boundary | **CLOSED** |

No runtime artifact lacked an authoritative expected digest, so no provenance
binding was manufactured and no runtime item remains partially fixed.

The remaining blocker is documentation-worktree reconciliation: complete the
existing `paper/ handbook/ handoffs/ -> docs/` relocation and update its stale
test paths in the separately authorized follow-up, then rerun the
reproducibility/full-suite gates. The contradictory demo documentation noted by
the prior audit also remains intentionally out of scope.

RUNTIME TRUST BOUNDARY HARDENED — READY FOR DOCUMENTATION/DEMO RECONCILIATION
