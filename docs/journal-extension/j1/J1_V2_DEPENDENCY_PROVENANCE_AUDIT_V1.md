# J1 — V2 Dependency Provenance Audit V1 (companion to the CSV ledger)

# `AUDIT ONLY — NO V2 AUTHORITY ACTIVATED — NOTHING REMOVED FROM ANY BUILD`

**Date:** 2026-09-05  
**Derived from commit:** `1ec6dc6a4a0737de128a15598be0d5929c469dca`  
**Canonical ledger:** `J1_V2_DEPENDENCY_PROVENANCE_AUDIT_V1.csv` — 335 rows, one per historical package

The CSV is the machine-readable record. This document explains how each column
was decided and reconciles the counts.

---

## 1. The historical evidence carries two fields

Every one of the 335 package records in the three establishing locks contains
exactly `name` and `version`. **No artifact filename, no hash, no index URL, no
installer.** That single fact determines most of this audit:

```text
wheel_or_sdist_byte_authority = ABSENT     for all 335, without exception
provenance from historical evidence alone  = UNKNOWN_ORIGIN for all 335
```

Everything stronger came from three weaker sources, each labelled in the ledger:
the current `tactics` venv metadata (local, mutable), repository source, and one
index query per package.

## 2. Primary role — mutually exclusive, reconciles to 335

```text
TRANSITIVE_RUNTIME_SUPPORT                    229
TRANSITIVE_SCIENTIFIC                          41
UNRESOLVED                                     35
INTERACTIVE_TOOLING                            15
TEST_TOOLING                                    7
DIRECT_SCIENTIFIC                               6
FIRST_PARTY                                     1
UNRELATED_OR_CONTAMINATING_CANDIDATE            1
TOTAL                                         335
```

How each was decided, from evidence only:

- **DIRECT_SCIENTIFIC** — imported by the J1 static closure and declared in a
  scientific extra of `pyproject.toml`.
- **TRANSITIVE_SCIENTIFIC** — reached from a direct scientific distribution by
  following `Requires-Dist`.
- **TEST_TOOLING** — in the `Requires-Dist` closure of the declared `[dev]`
  extra (`pytest`, `ruff`) and absent from the J1 closure.
- **INTERACTIVE_TOOLING** — required by no installed distribution (an explicit
  install) *and* providing console scripts, with no J1 relation.
- **TRANSITIVE_RUNTIME_SUPPORT** — required by installed distributions, none of
  which is in the J1 closure.
- **UNRESOLVED** — an explicit install, no console scripts, no J1 relation. No
  evidence supports a role, so none is asserted.
- **FIRST_PARTY** — `cardiosentinel`, installed from the source tree.
- **UNRELATED_OR_CONTAMINATING_CANDIDATE** — reserved for the §14 evidence bar;
  exactly one package clears it, and it remains a *candidate*.

**No package was classified from its name.**

## 3. Provenance, necessity, reconstructibility

### provenance_class

```text
PYPI_INDEX                                                331
PYTORCH_CPU_INDEX                                           2
FIRST_PARTY_CARDIOSENTINEL                                  1
LOCAL_EDITABLE                                              1
TOTAL                                                     335
```

### necessity_class

```text
NOT_REQUIRED_BY_J1_STATIC_CLOSURE                         251
REQUIRED_ONLY_TRANSITIVELY                                 41
UNKNOWN                                                    36
REQUIRED_FOR_J1_EXECUTION                                   7
TOTAL                                                     335
```

### reconstructibility_class

```text
RECONSTRUCTIBLE_FROM_IDENTIFIED_SOURCE_BUT_BYTES_UNBOUND  333
FIRST_PARTY_BOUND_TO_SOURCE_COMMIT                          1
LOCAL_ONLY_SOURCE                                           1
TOTAL                                                     335
```

### source_availability

```text
AVAILABLE_FROM_QUERIED_SOURCE                             333
NOT_QUERIED                                                 1
NOT_AVAILABLE_FROM_QUERIED_SOURCE                           1
TOTAL                                                     335
```

### candidate_v2_disposition

```text
UNRESOLVED_DO_NOT_RETAIN                                  230
RETAIN_TRANSITIVE                                          41
UNRESOLVED_DO_NOT_EXCLUDE                                  35
EXCLUDE_IF_HUMAN_APPROVED                                  15
EXCLUDE_TOOLING_FROM_SCIENTIFIC_RUNTIME                     7
RETAIN_DIRECT                                               6
RETAIN_FIRST_PARTY                                          1
TOTAL                                                     335
```

## 4. The J1-required set

```text
direct scientific (imported by the closure)        6
transitive scientific (via Requires-Dist)         41
first-party (cardiosentinel)                       1
                                                 ---
J1-required total                                 48
```

**Every one of the 48 has an identified reconstructible source. None is unresolved.**

## 5. The one package that could not be obtained from its source

```text
incident-management==0.1.0   NOT_AVAILABLE_FROM_QUERIED_SOURCE
```

It is **not** in the J1 closure, so it does not block the candidate. It is
audited separately in §7 of the audit report.

## 6. A correction made during this audit

The first pass probed **PyPI** for `torch==2.13.0+cpu` and
`torchvision==0.28.0+cpu` and recorded them as unavailable. That was the wrong
source: a `+cpu` local version is served by the PyTorch CPU index the
Containerfile configures, not by PyPI. Re-probed against the correct index, both
are available (31 and 18 matching wheels). **Concluding unavailability from
querying the wrong source is the exact error the qualification-003 evidentiary
correction was about**, and it is recorded here rather than quietly fixed.

`cardiosentinel` is likewise recorded as `NOT_QUERIED`: no index is its intended
source, so querying one and reporting absence would be meaningless.

## 7. Installer metadata — a local diagnostic, not provenance

```text
pip                   279
uv                     41
Poetry 2.2.1           13
(none)                  1
poetry                  1
```

CardioSentinel builds with pip/setuptools. The presence of **41 `uv`-installed**
and **14 Poetry-installed** distributions is consistent with a shared environment
serving more than one project. **It is consistent with, and does not prove,
cross-project leakage** — it is recorded as `LOCAL_DIAGNOSTIC` and nothing is
classified from it.

