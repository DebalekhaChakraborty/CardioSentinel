# J1 — V2 Dependency Authority Audit Report V1

# `DEPENDENCY PROVENANCE AUDIT ONLY — NO V2 AUTHORITY ACTIVATED — NO BUILD DISPATCH`

# `CANDIDATE READY FOR DEPENDENCY-AUTHORITY REVIEW — NOT AUTHORIZED`

**Date:** 2026-09-05
**Derived from commit:** `1ec6dc6a4a0737de128a15598be0d5929c469dca`

The first complete forensic audit of the historical V1 dependency snapshot,
package by package, all 335. **Nothing was removed from any build, no authority
was activated, no authorization was created and nothing was dispatched.**

---

## 1. Historical fact

```text
package_count                = 335   (identical in all three establishing locks)
historical_dependency_digest = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a

B4B_cnn_transformer_v1  5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc
P1B_phys_fusion_v1      fdde6475a02e0249e0238b89168e6b043b3ade1ec2bfd75922628127fb27d2ca
M1L_long_memory_v2      6aa199ea5410dde860fd3fcce9ceef0194a364ed2ed5b01678e0648fea60a452
```

# `b0fd6eaa…` remains a valid HISTORICAL SNAPSHOT AUTHORITY.

It is evidence of **what was recorded as installed**. All three locks agree, and
none was modified by this audit.

# It is not, and this audit does not make it, a V2 RECONSTRUCTIBLE DEPENDENCY AUTHORITY.

---

## 2. What failed, precisely

Qualification 003 established that the historical package-list evidence did not
provide a usable source mapping for one member under the authorized
reconstruction path. This audit establishes the general form of that problem:

**Every one of the 335 package records carries exactly two fields — `name` and
`version`.** No artifact filename, no hash, no index URL, no installer.

```text
wheel_or_sdist_byte_authority = ABSENT   for all 335, without exception
provenance from historical evidence alone = UNKNOWN_ORIGIN for all 335
```

A package list records *what was present*. It cannot, by construction, record
*where any of it came from*. That is the deficiency — not a wrong digest.

---

## 3. What this audit establishes

### 3.1 The J1 code closure

Static `ast` parse, seeded from the frozen J1 execution surface and expanded
through internal imports. **No module was imported; no data was touched.**

```text
modules in the J1 closure        113
external import roots             38
  standard library                32
  third-party                      6
  unmapped                         0
```

The six third-party roots are the *only* distributions J1 imports directly:
`numpy`, `scipy`, `scikit-learn`, `torch`, `wfdb`, `PyYAML`.

Full detail in `J1_V2_SCIENTIFIC_CODE_CLOSURE_V1.md`.

### 3.2 Necessity map — mutually exclusive, reconciling to 335

```text
TRANSITIVE_RUNTIME_SUPPORT                229
TRANSITIVE_SCIENTIFIC                      41
UNRESOLVED                                 35
INTERACTIVE_TOOLING                        15
TEST_TOOLING                                7
DIRECT_SCIENTIFIC                           6
FIRST_PARTY                                 1
UNRELATED_OR_CONTAMINATING_CANDIDATE        1
                                          ---
TOTAL                                     335
```

**The J1-required set is 48**: 6 direct + 41 transitive + 1 first-party.
**287 of the 335 have no established relation to the J1 execution closure.**

Every classification came from evidence — an AST import site, a `Requires-Dist`
edge, a `pyproject.toml` extra, a `direct_url.json`, or a console-script entry
point. **No package was classified from its name.**

### 3.3 Source and reconstructibility

```text
PYPI_INDEX                                              331
PYTORCH_CPU_INDEX                                         2
FIRST_PARTY_CARDIOSENTINEL                                1
LOCAL_EDITABLE                                            1

AVAILABLE_FROM_QUERIED_SOURCE                           333
NOT_QUERIED (first-party; no index is its source)         1
NOT_AVAILABLE_FROM_QUERIED_SOURCE                         1
```

**All 48 J1-required members have an identified reconstructible source. None is
unresolved.**

### 3.4 Candidate V2 scientific set

```text
candidate_package_count         = 48
candidate_dependency_set_digest = b8bc79688126a31e5a3d3420d07197e107c55f4a2aec98d5af9a0fdaf16d2b40
status                          = CANDIDATE_ONLY
authorization_status            = NOT_AUTHORIZED
```

That digest is a **review convenience**. A set does not become authority by
hashing.

---

## 4. A correction made inside this audit

The first pass queried **PyPI** for `torch==2.13.0+cpu` and
`torchvision==0.28.0+cpu` and recorded them `NOT_AVAILABLE_FROM_QUERIED_SOURCE`.

That was wrong. A `+cpu` local version identifier is served by the PyTorch CPU
index the Containerfile explicitly configures as a second index — **PyPI is not
their source.** Re-probed against the correct index, both are available (31 and
18 matching wheels for the exact versions).

**Concluding unavailability from querying the wrong source is precisely the error
the qualification-003 evidentiary correction was about.** It is recorded here
rather than quietly fixed, because an audit that hides its own corrections is
worth less than one that shows them.

`cardiosentinel` is recorded `NOT_QUERIED` for the same class of reason: no index
is its intended source, so querying one and reporting absence would be
meaningless.

---

## 5. `incident-management==0.1.0` — the deep audit

### Repository-proven

```text
present in all three locks, index 127            YES
emitted to requirements.pypi.txt, line 126       YES
in the J1 static closure                         NO
mapped from any J1 import root                   NO
declared as a dependency by ANY installed dist   NO
named in pyproject.toml                          NO
named in the requirements generator              NO
repository references outside the locks and the
  003 failure documents                          NONE
resolved from the configured source              NO
```

# `NO CARDIOSENTINEL NECESSITY ESTABLISHED`

### Absence of established necessity is a different claim from removability

**This audit does not conclude that the package may be removed, and the phrase
"safe to remove" appears nowhere in it as a finding.** Absence of an established
necessity is not proof of absence of necessity, and the disposition
recorded in the ledger is `UNRESOLVED_DO_NOT_RETAIN` — keep it out of the
candidate scientific set, and do **not** treat that as authorization to delete
it from the historical record or from any environment.

### Its own dependency closure — a candidate leakage finding

Following `Requires-Dist` from `incident-management`:

```text
its own dependency closure          111 of the 335 historical packages
  of which shared with J1's 48       16
  of which have NO J1 relation       95
```

Its declared dependencies are `google-adk`,
`google-cloud-aiplatform[adk,agent-engines]`, `google-cloud-secret-manager` and
`python-dotenv` — an agent stack, not a scientific one.

Supporting local diagnostic: **41 distributions were installed by `uv` and 14 by
Poetry**, neither of which CardioSentinel uses (it builds with pip/setuptools).

**This is consistent with cross-project environment leakage. It does not prove
it.** The classification stays `UNRELATED_OR_CONTAMINATING_CANDIDATE`, singular,
and the 95 keep their own evidence-based roles.

---

## 6. What this audit does NOT establish

- **No human authorization.** Nothing here is an authorization act.
- **No environment authority.** The Environment Authority Record remains absent.
- **No bit reproducibility.** Nothing has been built, once or twice.
- **No wheel-byte authority.** `ABSENT` for all 335, including every candidate
  member. A version pin fixes which distribution is requested, never the bytes
  that arrive.
- **No scientific execution authority.** J1 remains `PRE-REGISTERED — NOT
  AUTHORIZED`.
- **No proof of historical transitive relations.** The `Requires-Dist` edges came
  from the *currently installed* metadata in the `tactics` venv. That venv is an
  exact name-and-version witness of the snapshot — 335/335, zero drift under PEP
  503 normalization — but dependency metadata can differ between the historical
  artifact and today's. **This is diagnostic evidence, not proof of what was
  historically required**, and it is the single largest epistemic gap in this
  audit.
- **No runtime completeness.** An AST parse cannot see a dependency reached only
  through a plugin registry, an entry point, or a data-driven import.

---

## 7. Readiness

# `CANDIDATE READY FOR DEPENDENCY-AUTHORITY REVIEW — NOT AUTHORIZED`

Against the stated criteria:

| Criterion | Result |
|---|---|
| All J1-required dependencies identified | ✅ 48 |
| All required have an identified reconstructible source | ✅ 0 unresolved |
| Unresolved entries are not required by the J1 closure | ✅ the 36 `UNKNOWN` rows are all outside it |
| Candidate package set complete | ✅ closed under `Requires-Dist` |
| No governance blocker | ✅ no active authorization, nothing dispatched |

**Ready for review is not ready for authorization.** Before a V2 authority is
materialized, a human must decide at least:

1. whether artifact-byte binding (a wheelhouse, or hashes carried in a new lock)
   is required, given that byte authority is currently `ABSENT` for all 48;
2. whether transitive relations derived from present-day metadata are acceptable
   evidence, or must be re-established from historical artifacts;
3. what to do about the 287 packages with no established J1 relation — in
   particular whether the 111 reachable from `incident-management` are removed,
   retained, or investigated further;
4. whether `incident-management` itself is extraneous, which this audit
   deliberately did not decide.

The sequence remains:

```text
audit  ->  human decision on a V2 dependency authority  ->  authority
       ->  V6 builder review  ->  authorization 004  ->  controlled qualification
```

Not: audit → dispatch.
