# J1 — V2 Dependency Authority Decision Packet V1

# `ARTIFACT-BOUND CANDIDATE ONLY — NO V2 AUTHORITY ACTIVATED — NO BUILD DISPATCH`

# `THIS DOCUMENT DOES NOT AUTHORIZE THE DEPENDENCY AUTHORITY.`

**Date:** 2026-09-05
**Derived from commit:** `73e6b1e8570f69635a64d3aa8abde1ccb9f4c0f2`

PR #164 established *which* packages J1 needs. It could not establish *which
bytes*, because the historical records carry `name` and `version` and nothing
else. This task replaces that pair with an exact artifact, its SHA-256, its
source, its target compatibility and its own dependency metadata — and then
re-derives the closure from those artifacts rather than from anything installed.

**Nothing was authorized. No builder authorization was created. The controlled
builder was not dispatched. No scientific data was accessed.**

---

## 1. What this packet asks you to decide

The candidate is **blocked**, and two of the blockers are yours rather than
mine. Both were found by installing the candidate — which no session has ever
done, because nothing has ever been built even once.

```text
V2-BLOCKER-1   approved_runtime pins the V1 digest
V2-BLOCKER-2   establishing evidence is unreachable from an installed package
```

Neither is a dependency defect. §6 sets them out.

---

## 2. Historical fact, unchanged

```text
historical_package_count      = 335
historical_dependency_digest  = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
```

# `b0fd6eaa…` remains a valid HISTORICAL SNAPSHOT AUTHORITY.

The three establishing locks were read and are byte-unchanged. A test pins them.

```text
B4B_cnn_transformer_v1  5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc
P1B_phys_fusion_v1      fdde6475a02e0249e0238b89168e6b043b3ade1ec2bfd75922628127fb27d2ca
M1L_long_memory_v2      6aa199ea5410dde860fd3fcce9ceef0194a364ed2ed5b01678e0648fea60a452
```

**The V2 candidate is prospective.** It says which artifacts V2 proposes to
execute. It does **not** claim these are the bytes V1 used, and it does not
supersede the historical snapshot.

---

## 3. Seed, and what the artifacts actually said

The #164 candidate — 48 packages, digest `b8bc7968…` — was used as a **version
witness**, not as the answer. The closure was re-derived from the six J1 import
roots by parsing the `METADATA` inside each selected wheel, and the count was
not constrained to 48.

```text
seed_candidate_count               48   (47 external + cardiosentinel)
artifact_derived_package_count     48   (47 external + cardiosentinel)

seed_only_packages                 []
artifact_only_packages             []
version_conflicts                  []
```

# The artifact-derived closure reconciles exactly with the #164 seed.

That is a **result**, not a target. The two derivations are independent: #164
followed `Requires-Dist` from the *currently installed* `tactics` metadata; this
one followed it from the *bytes of the wheels selected for the frozen target*.
They agree on all 47 external members and every version.

### The six direct scientific roots

```text
numpy          2.3.2
scipy          1.18.0
scikit-learn   1.9.0
torch          2.13.0+cpu     PyTorch CPU index, not PyPI
wfdb           4.3.1
pyyaml         6.0.2
```

### Closure shape

```text
nodes                                       47
dependency edges recorded                  595
edges active on the frozen target           58
edges inactive (marker false on target)    537
extras activated                             0
```

Every edge carries its parent's artifact SHA-256 **and** its parent's `METADATA`
SHA-256, so a later metadata change cannot masquerade as the same candidate.

`torch==2.13.0+cpu` declares seven active dependencies and three extras
(`optree`, `opt-einsum`, `pyyaml`) that are inactive on this target. **No
`nvidia-*` or `triton` requirement is active** — this is the CPU build.

---

## 4. Artifact binding coverage

```text
external members                                        47
  with an exact artifact SHA-256                        47
  without                                                0
first-party, source-bound                                1
```

# `wheel_or_sdist_byte_authority` moves from ABSENT for all 48 to PRESENT for all 47 external members.

```text
PYPI_INDEX                    46
PYTORCH_CPU_INDEX              1
FIRST_PARTY_CARDIOSENTINEL     1
```

Every selected artifact is a wheel. **No member required an sdist**, so no
source-build authority is needed and `SDIST_BUILD_AUTHORITY_REQUIRED` is empty.

For all 47, the SHA-256 the index advertised reconciles with the SHA-256 computed
over the bytes actually received. The advertised value is recorded, never trusted
as the authority.

### Version policy

Every transitive requirement was satisfied by the version already present in the
historical 335.

```text
HISTORICAL_VERSION_WITNESS_SATISFIES_BOUND_ARTIFACT_METADATA   all active edges
HISTORICAL_VERSION_CONFLICT                                    0
NEW_TRANSITIVE_DEPENDENCY_REQUIRED_BY_BOUND_ARTIFACT           0
```

No package was modernised. Nothing drifted.

---

## 5. Exact-file selection — a hash is not enough on its own

**8 of the 47 external members have more than one tag-compatible wheel for their
pinned version** on the index: `charset-normalizer`, `fonttools`, `frozenlist`,
`multidict`, `pillow`, `propcache`, `soundfile`, `yarl`.

A `--hash=` line does not tell pip *which* file to fetch; it tells pip which
bytes to accept. With a live index, pip may pick a different compatible wheel and
fail the hash check rather than install the approved bytes.

**Mechanism used: a deterministic local wheelhouse containing only the approved
artifacts, installed with `--no-index --find-links --require-hashes`.**

```text
wheelhouse_member_count                47
wheelhouse_total_bytes                 306,443,579
candidate_wheelhouse_manifest_digest   e6684bd90f2cb6782e1e183d13e81bca14632692881877d78129b703c7dadc0b
```

The wheel bytes are **not** committed. This repository has no governed binary
artifact store and this task does not invent one; only the manifest and the
hashes are persisted.

### Hash mode

`--require-hashes` is now used deliberately, as a boolean flag, because the
authority finally contains hashes. The #159 remediation — which removed a
`--require-hashes` that had been given a value — remains correct; this is not a
reversal of it.

---

## 6. Clean-room qualification, and the two blockers it found

A fresh environment was created from the base CPython 3.12.6 — not `tactics`,
not `debalekha`, not any project venv — and every external member installed from
the wheelhouse with the index disabled and hashes enforced.

```text
pip install --no-index --find-links=<wheelhouse> --require-hashes   PASS
pip install --no-deps <tracked source tree>                          PASS
pip check                                                            PASS
installed inventory        49 = 47 governed + cardiosentinel + pip
version disagreements vs the manifest                                0
```

`pip` is the only non-candidate distribution present. It is venv substrate, not
part of the scientific dependency authority.

### Data-free import qualification

Real data was not merely unmounted: the qualification ran against a tracked-only
source export that **contains no `cardiosentinel-data`, `-features` or `-runs`
directory at all**, from a working directory holding nothing.

```text
numpy 2.3.2 · scipy 1.18.0 · sklearn 1.9.0 · torch 2.13.0+cpu · wfdb 4.3.1 · yaml 6.0.2
six direct scientific roots imported                    PASS

J1 internal modules attempted                           108
  imported, pristine install                            103
  imported, with establishing evidence placed           108
```

# V2-BLOCKER-2 — establishing evidence is unreachable from an installed package

`approved_runtime.REPOSITORY_ROOT` is `Path(__file__).resolve().parents[4]`. From
`site-packages/cardiosentinel/journal_extension/j1/approved_runtime.py` that
resolves to `<venv>/lib/python3.12`, where the three establishing
`EXPERIMENT_LOCK.json` paths do not exist. Five J1 modules then refuse to import:
`approved_runtime`, `build_authority`, `builder_authorization`, `builder_protocol`,
`controlled_build`.

**Cause isolated:** placing *only* those three lock files at the resolved
location, in the same environment, took the qualification from 103/108 to
**108/108**. **No dependency is missing.**

**Bounded:** observed in a site-packages clean-room install. It was **not**
observed in the authorized container image, because none has ever been built.
What that image's layout resolves to is not established here.

### Synthetic and unit qualification

Selected before execution: the 19 modules of `tests/journal_extension`, run from
the data-free tree. Nothing in the selection reads ECG data; the one reference to
a real data root in `test_j1_synthetic_qualification.py` is a *negative*
assertion that `cardiosentinel-runs/j1` does not exist.

```text
854 passed · 6 skipped · 1 failed
```

The 6 skips are the known shallow-checkout packet skips (ECG 29's tension),
unchanged. The single failure:

# V2-BLOCKER-1 — the runtime gate pins the V1 digest

```text
tests/journal_extension/test_j1_approved_runtime.py::test_the_scientific_environment_has_not_drifted

  approved (V1 historical, 335 packages) : b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
  observed (V2 candidate, pristine)      : c8abc3271d2dd0c80dbd39d1f9d80893634d5f5eb5d8aac4ae2680152e7fac03
```

`require_approved_dependencies()` refuses because the candidate environment is
not the V1 environment. **This is the check behaving exactly as written.** It is
also the reason a V2 environment cannot pass a gate pinned to V1 — including an
authorized one.

A related property, worth deciding at the same time: `observed_dependency_digest()`
delegates to V1's own method, which hashes **every** installed distribution.
`pip` is in the historical 335 (`26.0.1`) but is not a candidate member, so the
observed digest is sensitive to whichever pip the base image ships. The replay
below demonstrates this directly.

**What this establishes:** that a V2 environment does not satisfy a V1-pinned
gate. **What it does not establish:** what the gate should say instead. That is
an authority decision, and it alters gate output that retained receipts quote.

### Dependency install replay

Repeated in a second fresh environment with the network removed
(`unshare -rn`; an outbound connection attempt failed under the seal).

```text
governed members            IDENTICAL — 47 external + cardiosentinel, same names and versions
pip check                   PASS
only difference             pip bootstrap 26.2.1 (A, network up) vs 24.2 (B, sealed)
```

Classified `DEPENDENCY_INSTALL_REPLAY`. **Not** `BIT_REPRODUCIBLE_ENVIRONMENT` —
no OCI image has been built, once or twice, and no such claim exists.

One incidental measurement: the two first-party wheel builds differed
(`295cefc1…` / `f4444f67…`) because the clean-room script did not set
`SOURCE_DATE_EPOCH`. Rebuilt twice **with** `SOURCE_DATE_EPOCH=0` — which the
authorized Containerfile does set — both produced `2e3046b7…`. The difference was
the harness, not the build.

---

## 7. `incident-management`

```text
in the artifact-derived J1 closure                       NO
declared as an active dependency by any selected artifact NO
finding                                                  NOT_IN_ARTIFACT_DERIVED_J1_CLOSURE
prospective disposition   EXCLUDE_FROM_V2_J1_SCIENTIFIC_RUNTIME_IF_HUMAN_AUTHORIZED
```

**This is absence from a closure.** It is not a finding that the package is
globally extraneous, not proof of contamination, and not authorization to remove
it from the historical snapshot or from any environment. The exclusion becomes
authoritative only through an explicit human dependency-authority act.

---

## 8. The other 287 historical packages

```text
default                    OUTSIDE_CANDIDATE_SCIENTIFIC_RUNTIME
became reachable from the artifact-derived closure        0
```

None was included merely for having been co-installed, and none had to be added:
the artifact metadata reached exactly the 47. They remain in the V1 historical
snapshot, which this task did not modify.

Had any become reachable from artifact metadata, it would have moved into the
candidate regardless of its #164 classification. Evidence wins over the 48/287
partition. It simply did not have to.

---

## 9. Residual trust

SHA-256 binds the bytes selected for V2. It does **not** prove:

- that those bytes were the ones historically used in V1;
- that upstream artifact authorship was benign;
- that the package index is universally trustworthy;
- that the Python base image is independently reproduced from source;
- that hardware or runtime execution is deterministic.

Those are separate claims and none of them is made here.

---

## 10. Remaining limitations

- The closure came from **present-day metadata for present-day artifacts**. It is
  not proof of what was historically required — the largest disclosed gap from
  #164, narrowed but not closed.
- An artifact-metadata closure cannot see a dependency reached only through a
  plugin registry, an entry point or a data-driven import.
- **No native library below the Python distribution is pinned by any authority.**
  `torch`, `numpy`, `scipy` and `scikit-learn` carry compiled extensions and
  `soundfile` binds `libsndfile`; the wheels vendor these and no authority records
  their versions.
- The clean room ran on a host kernel, **not inside the authorized base image**.
- An independent re-derivation of the J1 internal module closure for this task's
  import qualification reached **108** modules where #164 reached **113**. The
  traversal rules differ; both reach the same six third-party roots and every
  module in the J1 package was reached by both. The difference was not
  investigated and **#164 is not contradicted**.

---

## 11. Readiness

# `ARTIFACT-BOUND V2 DEPENDENCY CANDIDATE BLOCKED — REVIEW REQUIRED`

| Criterion | Result |
|---|---|
| Artifact-derived closure reaches fixed point | ✅ |
| All required packages exact-version resolved | ✅ 48 |
| All required external packages exact-artifact hash-bound | ✅ 47 / 47 |
| All selected artifacts target-compatible | ✅ |
| All `Requires-Dist` edges accounted for | ✅ 595 |
| No historical-version conflict | ✅ 0 |
| No required sdist without separate build authority | ✅ 0 |
| No unresolved required dependency | ✅ 0 |
| `pip --require-hashes` installation succeeds | ✅ |
| `pip check` succeeds | ✅ |
| Data-free imports succeed | ❌ 103/108 pristine — **V2-BLOCKER-2** |
| Approved synthetic tests succeed | ❌ 1 failed — **V2-BLOCKER-1** |
| Scientific data access = NO | ✅ |
| Scientific attempts = 0 | ✅ |

The artifact binding — the thing this task existed to do — succeeded completely.
What blocks the candidate is two properties of the **apparatus** that only an
actual install could reveal, and neither is mine to decide.

---

## 12. Decisions still pending

Unchanged from #164, and none of them is an assistant recommendation:

1. acceptance of exact artifact-byte binding;
2. acceptance of the artifact-derived closure;
3. prospective exclusion of the 287 historical packages outside it;
4. prospective exclusion of `incident-management` from the V2 J1 runtime;
5. acceptance of the remaining source and index trust;
6. acceptance of the limitations in §9 and §10.

Newly added by this task:

7. what `approved_runtime`'s dependency gate should say once a V2 authority
   exists — and whether its digest method should count substrate such as `pip`;
8. how an installed J1 package should reach its establishing evidence.

```text
audit  ->  artifact binding  ->  HUMAN DECISION  ->  authority materialization
       ->  V6 builder review  ->  authorization 004  ->  ONE controlled qualification
```

Still not: candidate → dispatch.

```text
candidate != authority
```
