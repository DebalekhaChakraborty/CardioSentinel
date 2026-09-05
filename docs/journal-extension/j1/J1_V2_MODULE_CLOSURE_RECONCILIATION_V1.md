# J1 — V2 Module Closure Reconciliation V1

# `STATIC ANALYSIS ONLY — NO MODULE IMPORTED, NO DATA TOUCHED, NOTHING AUTHORIZED`

**Date:** 2026-09-05
**Derived from commit:** `76ebcca9bc618b187434b029de2fa01ece962bf8`

PR #164 recorded a J1 scientific code closure of **113 modules**. PR #165
independently re-derived one and reached **108**, disclosed the difference, and
did not investigate it. This closes that item.

The short answer: **#165's traversal was wrong, #164's count was closer to
right, and the difference introduces no new external distribution root.**

---

## 1. What #164 left, and what it did not

`J1_V2_IMPORT_DISTRIBUTION_MAP_V1.json` records the closure **count** (113) and,
for each of 38 external import roots, the number of import sites across the
closure. It does not record the module names, and **no generator script was
committed** with the audit.

# The #164 module set is not present in any committed artifact.

So an element-by-element comparison against it cannot be performed — not because
the analysis is hard, but because one of the two sets does not exist to compare
with. That is a finding about the evidence, and the remedy is in §5: this
document commits the module list, so the next reconciliation has two sets.

What the site-count table *does* support is a fingerprint comparison, since the
counts are additive over modules. §3 uses it.

---

## 2. The defect was in #165

The #165 traversal followed **import statements only**. Several modules in the
closure import `cardiosentinel.features.schema`:

```text
neural.physiology_fusion · neural.m2_persistence · neural.m2_gate_derivation
neural.integrity         · baseline.cache
```

Importing `cardiosentinel.features.schema` also executes
`cardiosentinel/features/__init__.py` — the import system runs every parent
package first — and that `__init__` imports `features.morphology`. **#165 never
added the parent package, so it never parsed that `__init__`, and never reached
`morphology`.**

That single omission explains the root-count difference exactly:

```text
#164 external import roots   38
#165 external import roots   37   <- missing `warnings`
```

`warnings` is imported by `features.morphology` and by nothing else within
reach. `morphology` also contributes `numpy` ×2 and `wfdb` ×1, which is most of
the positive residual #165 could not account for.

**A parent package's `__init__` is a real runtime dependency**, not a traversal
convenience. The corrected rule is stated in §4.

---

## 3. The fingerprint, and what it settles

The counting rule is shared, not merely similar — both closures record
**103 `__future__` sites** and **33 `torch` sites**. So the residual between them
is a set difference and not a method difference.

Against the reconciled closure of §4, every one of #164's recorded roots is
covered:

```text
#164 minus reconciled, by root:
  __future__ -4 · dataclasses -2 · hashlib -1 · importlib -1 · json -2
  numpy -3 · pathlib -3 · re -1 · typing -4

positive residual (a root or site the reconciled closure fails to reach):  NONE
```

# The reconciled closure covers every import site #164 recorded, on every root, with none missing.

It does not resolve to a single set. No subset of modules added to, or removed
from, either closure reproduces #164's vector exactly — the two differ in both
directions — so **#164's exact set remains unrecoverable**, and this document
does not claim to have recovered it.

---

## 4. The reconciled closure

Same four seeds as #164:

```text
cardiosentinel.journal_extension.j1      the J1 apparatus and evaluator
cardiosentinel.neural.p1_experiment      the P1 experiment surface
cardiosentinel.neural.provenance         provenance and determinism
cardiosentinel.signal.preprocessing      causal ECG preprocessing
```

Traversal rule, stated so it can be re-run rather than re-guessed:

```text
fixed point over internal import edges
  + the parent-package edge the import system itself executes:
    importing a.b.c runs a/__init__.py and a/b/__init__.py first
```

```text
reconciled module count   118
```

The count exceeds 113 partly because it now includes package `__init__` modules
as nodes and partly because it includes `v2_runtime_authority`, added by this
PR. The module list is committed in
`J1_V2_MODULE_CLOSURE_RECONCILIATION_V1.json`.

### Classification

```text
SCIENTIFIC_EXECUTION_MODULE      91
APPARATUS/GOVERNANCE_MODULE      17
TRANSITIVE_INTERNAL_MODULE       10   (package __init__ modules)
TEST/UTILITY_MODULE               0
OUTSIDE_FROZEN_J1_EXECUTION_SURFACE  0
```

Every module in the reconciled closure carries a classification in the JSON, and
a test requires that mapping to be total.

---

## 5. The question that gates readiness

> Does any discrepancy introduce a new external distribution root?

```text
#164 third-party roots        numpy · scipy · sklearn · torch · wfdb · yaml
#165 third-party roots        numpy · scipy · sklearn · torch · wfdb · yaml
reconciled third-party roots  numpy · scipy · sklearn · torch · wfdb · yaml

new external distribution roots:  NONE
```

# No seventh external root exists.

The only root that differed between #164 and #165 was `warnings`, which is
standard library and carries no distribution. **The 47-member artifact-bound
dependency set is unaffected**, and PR #165's artifact evidence needs no
regeneration.

---

## 6. What this does not establish

- It does not recover #164's module set. That set was never committed.
- It does not establish runtime completeness. An AST parse cannot see a
  dependency reached only through a plugin registry, an entry point or a
  data-driven import — unchanged from #164 §5 and #165.
- It authorizes nothing.

```text
scientific data accessed   NO
scientific attempts        0
```
