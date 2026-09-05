# J1 — V2 Scientific Code Closure V1

# `STATIC ANALYSIS ONLY — NO MODULE IMPORTED, NO DATA TOUCHED`

**Date:** 2026-09-05  
**Derived from commit:** `1ec6dc6a4a0737de128a15598be0d5929c469dca`

Every module below was parsed with `ast`. **No scientific module was imported,
no ECG row was read, no subject was enumerated, and no TRAIN, validation, test
or external cohort data was accessed.**

---

## 1. What J1 must execute

The closure is seeded from the frozen J1 execution surface and expanded by
following every internal import transitively:

```text
cardiosentinel.journal_extension.j1      the J1 apparatus and evaluator
cardiosentinel.neural.p1_experiment      the P1 experiment surface
cardiosentinel.neural.provenance         provenance and determinism
cardiosentinel.signal.preprocessing      causal ECG preprocessing
```

Following internal imports from those seeds reaches **113 modules**.

Seeding is the one judgement in this document. It is taken from the repository's
own layout rather than inferred: these are the packages the J1 apparatus, its
evaluator and the frozen pipeline components live in. A module reachable from
none of them is not in the J1 execution path.

## 2. External import roots

The 113 modules import **38 distinct external top-level roots**.
Of these, **32 are Python standard library** and carry no dependency:

```text
  __future__        argparse          ast               collections       contextlib        contextvars       dataclasses       datetime
  enum              hashlib           heapq             importlib         inspect           itertools         json              math
  os                pathlib           platform          random            re                resource          shutil            statistics
  subprocess        sys               tarfile           textwrap          time              traceback         typing            warnings
```

**6 are third-party**, and these are the only distributions J1 imports
directly:

| Import root | Distribution | Import sites | Ambiguous |
|---|---|---|---|
| `numpy` | `numpy` | 55 | no |
| `scipy` | `scipy` | 4 | no |
| `sklearn` | `scikit-learn` | 2 | no |
| `torch` | `torch` | 33 | no |
| `wfdb` | `wfdb` | 8 | no |
| `yaml` | `pyyaml` | 1 | no |

**No import root failed to map to an installed distribution.**

## 3. Conditional, function-local and dynamic imports

Recorded rather than resolved, because an import that only runs on some paths is
still a dependency:

```text
conditional imports (inside try/if/with) : 8
function-local imports                   : 119
dynamic import surfaces                  : 0
```

The lazy-import boundary in `approved_runtime` is deliberate and is the repair
that #155 made: the builder gate must load without the scientific stack. Those
imports are counted here because they are still dependencies of the code that
runs them, even though the gate never reaches them.

## 4. Native-library assumptions

Visible from the source: `torch`, `numpy`, `scipy` and `scikit-learn` carry
compiled extensions, and `soundfile` (reached transitively through `wfdb`) binds
`libsndfile`. **The historical evidence records no native library versions**, so
nothing below the Python distribution level is pinned by any authority. This is
a disclosed gap, not a resolved one.

## 5. What this closure does not establish

- It does not establish that the closure is **runtime**-complete. A dependency
  reached only through a plugin registry, an entry point or a data-driven import
  would not appear in an AST parse.
- It does not establish that the historical environment's dependency metadata
  matched today's; §10 of the audit records that limitation.
- It does not authorize anything.
