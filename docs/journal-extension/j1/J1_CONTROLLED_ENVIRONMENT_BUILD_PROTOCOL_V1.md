# J1 — Controlled Environment Build Protocol, V1

# `FROZEN BUILD CANDIDATE — NOT EXECUTED`

An **engineering and reproducibility protocol**, not a scientific experiment
protocol. It freezes every result-affecting build choice *before* the first real
artifact build, so that no choice is made while looking at a build failure.

**Date:** 2026-09-02
**Frozen against:** `master` at `6ed8af52f74eaf462f836eaa0285fe2105695c8d`
**Builder:** [`J1_BUILDER_SELECTION_RECEIPT_V1.md`](J1_BUILDER_SELECTION_RECEIPT_V1.md) — `CANDIDATE`, human authorization `PENDING`
**Implemented by:** `src/cardiosentinel/journal_extension/j1/builder_protocol.py`
**Qualified by:** `tests/journal_extension/test_j1_builder_protocol.py` — 73 tests

**No image was built. No artifact digest exists. Nothing here has executed.**

---

## 1. Artifact type — the ambiguity resolved, because it is real

"Image SHA-256" names at least two different objects. Resolved read-only from
the registry on 2026-09-02, the tag `python:3.12.6-slim-bookworm` gives:

| Object | Digest |
|---|---|
| OCI image **index** (what the tag resolves to) | `sha256:ad48727987b259854d52241fac3bc633574364867b8e20aec305e6e7f4028b26` |
| linux/amd64 image **manifest** (inside that index) | `sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |

Two different values for the same tag. **The manifest digest was verified by
recomputing SHA-256 over the fetched manifest bytes**, not by trusting a
response header.

### Frozen

| | |
|---|---|
| `artifact_type` | `oci_single_platform_image_manifest` |
| OCI media type | `application/vnd.oci.image.manifest.v1+json` |
| Target platform | `linux/amd64` |
| Digest-bearing object | the canonical **image manifest bytes** |
| Digest algorithm | SHA-256 |

```text
artifact_sha256 = SHA-256 over the canonical OCI image manifest bytes
```

**Explicitly not:** a `docker save` tar digest; compressed registry transfer
bytes; a filesystem directory hash; an image tag; a registry URL; or an OCI
**index** digest.

An index is chosen only if a future protocol version says so explicitly. J1 runs
on one platform, so an index would add a layer of indirection between the
authorization and the thing that executes.

---

## 2. Artifact identity versus location

| | |
|---|---|
| `output_artifact_digest` | `sha256:<64 hex>` — **identity** |
| `artifact_location` | a resolvable registry reference — **provenance** |

`registry/name@sha256:…` is **refused** in `output_artifact_digest`. Two mirrors
of the same artifact share one identity and have two locations; storing the
location inside the identity would make a mirrored copy look like a different
artifact.

---

## 3. Target platform — traced, not assumed

All three V1 experiment locks agree, and this is the evidence the choice rests
on:

| | B4B / P1B / M1L |
|---|---|
| `device` | `cpu` |
| `gpu_model` | `None` |
| `cuda_version` | `None` |
| `cudnn_version` | `None` |
| `amp_enabled` | `False` |
| `deterministic_algorithms` | `True` |
| `torch_version` | **`2.13.0+cpu`** |
| `platform` | `Linux-6.1.0-52-cloud-amd64-x86_64-with-glibc2.36` |

### Frozen

```text
os                    linux
architecture          amd64
container platform    linux/amd64
libc                  glibc 2.36  (Debian 12 bookworm)
compute device        cpu
accelerator           none
```

**No GPU, and this is not a preference.** The approved dependency set contains
`torch==2.13.0+cpu` — a CPU-only wheel that cannot use CUDA. Introducing an
accelerator would require a different torch build, which would change the
approved dependency digest and therefore break the runtime authority J1
inherits. No STOP is required: the authority resolves it.

---

## 4. Base image identity

Required form: `<repository>@sha256:<digest>`. **A tag alone is refused.**

| | |
|---|---|
| Descriptive tag | `python:3.12.6-slim-bookworm` — metadata for a human reviewer |
| **Authoritative digest** | the linux/amd64 image manifest digest resolved at build time and recorded |
| Resolved 2026-09-02 | `sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |
| Index it was resolved from | `sha256:ad48727987b259854d52241fac3bc633574364867b8e20aec305e6e7f4028b26` |

The tag matches the frozen target: CPython 3.12.6 on Debian 12 (glibc 2.36).

**The recorded digest is a resolution, not a commitment.** Base image digests
for a tag change when the upstream image is rebuilt. The build **re-resolves and
records**, and the recorded value must be verified by recomputation before use.
`python:3.12`, `python:3.12.6` and `ubuntu:latest` are all refused without a
resolved digest.

---

## 5. Dependency reconstruction

The build reproduces the **exact** approved dependency authority. It does not
create a new one.

### Three named sources — a finding, not a design choice

Inspection of the frozen 335-package set:

| Source | Count | Why |
|---|---|---|
| `PYPI` | **332** | ordinary releases |
| `PYTORCH_CPU_INDEX` | **2** | `torch==2.13.0+cpu`, `torchvision==0.28.0+cpu` — local version suffixes, **not on PyPI** (verified: HTTP 404 on PyPI, 200 on `download.pytorch.org/whl/cpu`) |
| `FIRST_PARTY_SOURCE` | **1** | `cardiosentinel==0.1.0` — no index resolves it; installed from the source tree, and it is the **source commit** that pins it, not the version string |

A build that pointed only at PyPI would fail on two packages and silently
mis-resolve a third.

### Derived build input ≠ new dependency authority

The generated requirements/constraints artifact is a **derived build input**. It
carries its own digest, and `require_derived_input_matches_authority`
mechanically proves it is exactly the frozen mapping — refusing any package
added or dropped.

> **No package version may be added, removed or changed to make an image build
> succeed.** If the frozen environment cannot be reproduced, that is a finding
> to record and escalate, not a set to edit.

Unconstrained `pip install -r requirements.txt` against ranges is refused;
`require_pinned_dependency_specifier` accepts only `name==version`.

---

## 6. Protecting the live `tactics` reference

`tactics` is a **verification witness**, not the builder authority and not the
artifact.

Read-only verification procedure, recorded each time:

```text
python_version
installed_package_count
dependency_digest
check_timestamp
```

**Do not install, update or uninstall anything in it.**

> **Failure of the live reference later does not rewrite frozen environment
> authority.** It removes a convenient witness. The authority is the frozen V1
> experiment locks and the compiled digest constant, both of which survive the
> venv.

---

## 7. Build configuration

`build_configuration_digest` is computed over a canonical manifest of **every
build-affecting file**, each identified by SHA-256:

```text
containerfile
dependency_input
build_script
workflow
artifact_validation_script
```

**Not the container file's digest alone.** Four other file classes influence the
image, and a configuration digest that missed them would call two materially
different builds identical. A missing input is refused.

---

## 8. Build tooling

Third-party actions are pinned by **immutable commit SHA**; `@v4`, `@main`,
`@master` and unpinned references are refused. Version tags are recorded
separately as human-readable metadata. Resolutions are in §5 of the builder
selection receipt.

The runner label is pinned. **`ubuntu-latest` is a moving target.**

---

## 9. Network policy

```text
network_access_required = true
```

No offline mirror of the approved package set exists.

**Permitted sources, and only these:**

| Source | For |
|---|---|
| the configured PyPI index | the 332 PyPI packages, each exactly pinned |
| `download.pytorch.org/whl/cpu` | `torch` and `torchvision` CPU wheels |
| the container registry holding the base image | the base image, **by digest** |
| the repository source at `source_commit` | `cardiosentinel` |

Every fetched artifact is version- or digest-constrained. **Mutable package
resolution is prohibited**, the build must not silently select newer versions,
and arbitrary build-time downloads from URLs absent from the build provenance
are not permitted.

---

## 10. Two-build reproducibility procedure

The artifact is built **twice, independently**, before anything is promoted.

Build A and Build B share exactly:

```text
source_commit · base_image_digest · dependency_digest
build_configuration_digest · target platform · builder protocol
```

They must come from **separate clean runs**. Build B **must not consume Build
A's artifact** — it would then reproduce a copy rather than the build.

Each build independently emits: artifact digest · build manifest · builder
provenance · logs.

The #148 reproducibility contract is then applied.

| Outcome | Action |
|---|---|
| `artifact_digest_A == artifact_digest_B` | `BIT_REPRODUCIBLE` — the preferred outcome |
| digests differ | **STOP.** Promote neither digest. |

**A divergence is not automatically reclassified as
`NOT_REPRODUCIBLE_DOCUMENTED`.** That classification weakens the authority model
and requires separate human review. Choosing one of two digests is exactly the
decision this procedure exists to prevent being made quietly.

---

## 11. Provenance requirements

No build output without provenance may become an environment artifact candidate.
Each real build retains:

```text
builder identity          workflow identity        workflow commit/digest
source commit             base image digest        dependency authority identity
dependency digest         build configuration digest
target platform           build start/end timestamps
artifact digest           artifact media type      artifact location
manifest digest           build logs/reference     provenance/attestation reference
```

---

## 12. What this protocol does not do

No image built. No image pushed. No artifact digest created or promoted. No
build manifest for a real artifact. No environment promoted. **No builder
authorized.** No `EnvironmentAuthorityRecord`, no `environment_sha256`, no
`J1_AUTHORIZATION_V1`, no attempt budget, no TRAIN authority, no execution SHA,
no scientific data accessed.

**No workflow file was added to the repository.** A file under
`.github/workflows/` is live on push; adding one here would be an uncontrolled
build attempt. The protocol specifies the workflow; it does not ship it. A test
asserts `ci.yml` remains the only workflow.

```text
builder candidate  ≠  builder qualified  ≠  builder human-authorized
                   ≠  environment authorized  ≠  J1 execution authorized
```

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
