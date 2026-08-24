# Experiment Contract

Every experiment must be reproducible, traceable, and bounded by the evidence.

## Prohibitions

- Do not leak patients or subjects across train, validation, and test partitions.
- Do not tune architectures, thresholds, calibration, routing, or personalization
  using the fixed test set.
- Do not manually edit outputs, invent numbers, or report untracked results.
- Do not combine window-level and episode-level conclusions.
- Do not report accuracy alone; include class-aware metrics and prevalence-aware
  interpretation.
- Do not treat raw softmax values as calibrated confidence.
- Do not infer clinical utility or effectiveness from a hardware demonstration.

## Required record

Each run must emit machine-readable outputs containing the resolved
configuration, Git commit and dirty state, random seed, runtime environment,
dataset and annotation provenance, split-manifest digest, command, and timing.
The test partition is fixed before model selection and never changes during a
study.

For benchmark protocol V1, `sealed_test_partition = true`. The committed test
subject list and canonical split hash are immutable after any model result is
observed. Poor performance, unexpected prevalence, hyperparameter or calibration
behavior, and presentation preferences are never reasons to alter it. A change
requires a new versioned benchmark protocol, a new split hash, and a documented
scientific justification; it must not silently replace V1.

Use subject-wise partitions. Use deterministic execution where technically
possible and explicitly record exceptions. Report calibration metrics before
confidence-driven routing. Report window and episode metrics separately,
including false alarms per hour and event-onset delay when applicable.

Every novelty claim requires error analysis and ablation evidence. Preserve
predictions and artefacts outside Git according to dataset access conditions.

## Self-referential digest convention

An experiment lock carries its own digest in `experiment_lock_sha256`. A digest
cannot contain itself, so the field is **excluded from its own input**: the
value is the SHA-256 of the lock object with `experiment_lock_sha256` removed,
serialized canonically (`sort_keys=True`, `separators=(",", ":")`) — the same
serialization `sha256_canonical` applies elsewhere.

This gives the canonical lock payload an in-lock identity and makes later field
changes detectable. `experiment_lock_sha256` and `verify_experiment_lock` in
`cardiosentinel.neural.integrity` implement the convention without mutating the
input lock.

Verify a lock by removing the field and recomputing. Hashing the file's raw
bytes, or hashing the object with the field left in, both produce a mismatch
against a valid lock; neither is evidence of drift. This convention was
undocumented until `PROVENANCE_INCIDENT_V1.md`, where the omission produced a
false report of artifact drift.

The convention has a consequence that is stronger than a naming rule: **a locked
artifact cannot be edited after the fact.** Changing any field changes the
lock's digest, and that digest is registered in downstream protocol documents,
cache manifests and other experiments' locks. Correction of a locked value is
therefore not a repair operation but an invalidation of every artifact that
cites it. **Locked artifacts are not corrected by editing their digest-bearing
fields. If provenance translation is required, it is recorded externally.**
