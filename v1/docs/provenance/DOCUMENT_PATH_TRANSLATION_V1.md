# Document path translation, V1

**2026-08-28. `docs/` was reorganised from a flat directory into categories, and
`handbook/`, `audits/`, `paper/` and `handoffs/` were hoisted to the repository
root.** This table maps every old path to its new one.

**Why a table instead of leaving the files alone.** This repository already has
the precedent: `COMMIT_PIN_TRANSLATION_V1.md` exists because a 2026-08-24
identifier migration invalidated 69 commit pins across 71 files, and the answer
was a translation table rather than reverting the migration. The same answer
applies here.

## The part that matters — paths named inside frozen evidence

**8 of the moved documents are named by path inside promoted artifacts under
`cardiosentinel-runs/`**, including the sealed single-use test evidence
(`TEST_ATTEMPT.json`, `TEST_AUDIT.json`). Those artifacts are immutable —
`repeat_attempt_permitted` is `false` — so **they still record the old path and
were not edited.** They are not wrong; they record where the document was when
the run happened. Resolve them through this table.

| old path (as recorded in frozen evidence) | current path |
|---|---|
| `docs/B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md` | `docs/experiments/b4/B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md` |
| `docs/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md` | `docs/experiments/b4/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md` |
| `docs/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_PLAN_V1.md` | `docs/experiments/b4/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_PLAN_V1.md` |
| `docs/B4_GLOBAL_ENCODER_SELECTION_V1.json` | `docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.json` |
| `docs/M2_DEVELOPMENT_ATTEMPT1_FAILURE_AND_RECOVERY_DECISION_V1.md` | `docs/experiments/m2/M2_DEVELOPMENT_ATTEMPT1_FAILURE_AND_RECOVERY_DECISION_V1.md` |
| `docs/M2_DEVELOPMENT_RECOVERY1_FAILURE_AND_RECOVERY2_DECISION_V1.md` | `docs/experiments/m2/M2_DEVELOPMENT_RECOVERY1_FAILURE_AND_RECOVERY2_DECISION_V1.md` |
| `docs/M2_STRESS_INTERVAL_ELIGIBILITY_DECISION_V1.md` | `docs/experiments/m2/M2_STRESS_INTERVAL_ELIGIBILITY_DECISION_V1.md` |
| `docs/RUNTIME_INTEGRITY_SENTINEL_V1.md` | `docs/provenance/RUNTIME_INTEGRITY_SENTINEL_V1.md` |

## Everything else that moved

| old path | current path |
|---|---|
| `docs/ANNOTATION_SEMANTICS.md` | `docs/contracts/ANNOTATION_SEMANTICS.md` |
| `docs/ARCHITECTURE.md` | `docs/control-plane/ARCHITECTURE.md` |
| `docs/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` | `docs/experiments/b4/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` |
| `docs/B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md` | `docs/experiments/b4/B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md` |
| `docs/B4_E10_REPRESENTATION_GEOMETRY_PLAN_V1.md` | `docs/experiments/b4/B4_E10_REPRESENTATION_GEOMETRY_PLAN_V1.md` |
| `docs/B4_E10_REPRESENTATION_GEOMETRY_REPORT_V1.md` | `docs/experiments/b4/B4_E10_REPRESENTATION_GEOMETRY_REPORT_V1.md` |
| `docs/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_REPORT_V1.md` | `docs/experiments/b4/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_REPORT_V1.md` |
| `docs/B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1.md` | `docs/experiments/b4/B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1.md` |
| `docs/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_REPORT_V1.md` | `docs/experiments/b4/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_REPORT_V1.md` |
| `docs/B4_E13A_HELD_OUT_GEOMETRY_RELIABILITY_PLAN_V1.md` | `docs/experiments/b4/B4_E13A_HELD_OUT_GEOMETRY_RELIABILITY_PLAN_V1.md` |
| `docs/B4_E1_REPRESENTATION_PROBE_ANALYSIS_PLAN_V1.md` | `docs/experiments/b4/B4_E1_REPRESENTATION_PROBE_ANALYSIS_PLAN_V1.md` |
| `docs/B4_E1_REPRESENTATION_PROBE_REPORT_V1.md` | `docs/experiments/b4/B4_E1_REPRESENTATION_PROBE_REPORT_V1.md` |
| `docs/B4_E2_E3_ANALYSIS_PLAN_V1.md` | `docs/experiments/b4/B4_E2_E3_ANALYSIS_PLAN_V1.md` |
| `docs/B4_E6A_PRECISION_ANALYSIS_REPORT_V1.md` | `docs/experiments/b4/B4_E6A_PRECISION_ANALYSIS_REPORT_V1.md` |
| `docs/B4_E6_FEASIBILITY_AUDIT_V1.md` | `docs/experiments/b4/B4_E6_FEASIBILITY_AUDIT_V1.md` |
| `docs/B4_E7A_SCORE_SCALE_MECHANISM_PLAN_V1.md` | `docs/experiments/b4/B4_E7A_SCORE_SCALE_MECHANISM_PLAN_V1.md` |
| `docs/B4_E7A_SCORE_SCALE_MECHANISM_REPORT_V1.md` | `docs/experiments/b4/B4_E7A_SCORE_SCALE_MECHANISM_REPORT_V1.md` |
| `docs/B4_E7B_CROSS_STREAM_OFFSET_PLAN_V1.md` | `docs/experiments/b4/B4_E7B_CROSS_STREAM_OFFSET_PLAN_V1.md` |
| `docs/B4_E7B_CROSS_STREAM_OFFSET_REPORT_V1.md` | `docs/experiments/b4/B4_E7B_CROSS_STREAM_OFFSET_REPORT_V1.md` |
| `docs/B4_E7_PERSONALIZATION_AUDIT_V1.md` | `docs/experiments/b4/B4_E7_PERSONALIZATION_AUDIT_V1.md` |
| `docs/B4_E8A_MEMORY_MECHANISM_PLAN_V1.md` | `docs/experiments/b4/B4_E8A_MEMORY_MECHANISM_PLAN_V1.md` |
| `docs/B4_E8A_MEMORY_MECHANISM_REPORT_V1.md` | `docs/experiments/b4/B4_E8A_MEMORY_MECHANISM_REPORT_V1.md` |
| `docs/B4_E8B_INCREMENTAL_INFORMATION_PLAN_V1.md` | `docs/experiments/b4/B4_E8B_INCREMENTAL_INFORMATION_PLAN_V1.md` |
| `docs/B4_E8B_INCREMENTAL_INFORMATION_REPORT_V1.md` | `docs/experiments/b4/B4_E8B_INCREMENTAL_INFORMATION_REPORT_V1.md` |
| `docs/B4_E9_LEAD_POLARITY_AUDIT_PLAN_V1.md` | `docs/experiments/b4/B4_E9_LEAD_POLARITY_AUDIT_PLAN_V1.md` |
| `docs/B4_E9_LEAD_POLARITY_AUDIT_REPORT_V1.md` | `docs/experiments/b4/B4_E9_LEAD_POLARITY_AUDIT_REPORT_V1.md` |
| `docs/B4_GLOBAL_ENCODER_SELECTION_V1.md` | `docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md` |
| `docs/B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md` | `docs/experiments/b4/B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md` |
| `docs/B4_PROTOCOL_V1.md` | `docs/experiments/b4/B4_PROTOCOL_V1.md` |
| `docs/B4_RESOURCE_BENCHMARK_V1.md` | `docs/experiments/b4/B4_RESOURCE_BENCHMARK_V1.md` |
| `docs/B4_TEST_AUTHORIZATION_V1.md` | `docs/experiments/b4/B4_TEST_AUTHORIZATION_V1.md` |
| `docs/B4_TEST_DEFERRAL_DECISION_V1.md` | `docs/experiments/b4/B4_TEST_DEFERRAL_DECISION_V1.md` |
| `docs/B4_VALIDATION_CHALLENGE_PROTOCOL_V1.md` | `docs/experiments/b4/B4_VALIDATION_CHALLENGE_PROTOCOL_V1.md` |
| `docs/BASELINE_PROTOCOL_V1.md` | `docs/contracts/BASELINE_PROTOCOL_V1.md` |
| `docs/BENCHMARK_PROTOCOL_V1.md` | `docs/contracts/BENCHMARK_PROTOCOL_V1.md` |
| `docs/COMMIT_PIN_TRANSLATION_V1.md` | `docs/provenance/COMMIT_PIN_TRANSLATION_V1.md` |
| `docs/CROSS_DATASET_PROVENANCE.md` | `docs/provenance/CROSS_DATASET_PROVENANCE.md` |
| `docs/CURRENT_STATE.md` | `docs/control-plane/CURRENT_STATE.md` |
| `docs/DATASET_CONTRACT.md` | `docs/contracts/DATASET_CONTRACT.md` |
| `docs/DATA_SPLIT_POLICY.md` | `docs/contracts/DATA_SPLIT_POLICY.md` |
| `docs/DEMO_SCENARIO.md` | `docs/explanation/DEMO_SCENARIO.md` |
| `docs/EVIDENCE_MAP.md` | `docs/control-plane/EVIDENCE_MAP.md` |
| `docs/EXPERIMENT_CATALOGUE.md` | `docs/control-plane/EXPERIMENT_CATALOGUE.md` |
| `docs/EXPERIMENT_CONTRACT.md` | `docs/contracts/EXPERIMENT_CONTRACT.md` |
| `docs/EXPLANATION_EVALUATION_PROTOCOL.md` | `docs/explanation/EXPLANATION_EVALUATION_PROTOCOL.md` |
| `docs/EXPLANATION_EVALUATION_REPORT_V1.md` | `docs/explanation/EXPLANATION_EVALUATION_REPORT_V1.md` |
| `docs/EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md` | `docs/external-validation/EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md` |
| `docs/EXTERNAL_VALIDATION_STRATEGY_V1.md` | `docs/external-validation/EXTERNAL_VALIDATION_STRATEGY_V1.md` |
| `docs/IMPLEMENTATION_PLAN.md` | `docs/control-plane/IMPLEMENTATION_PLAN.md` |
| `docs/IMPROVEMENT_ROADMAP_V1.md` | `docs/control-plane/IMPROVEMENT_ROADMAP_V1.md` |
| `docs/LITERATURE_SEARCH_V1.json` | `docs/literature/LITERATURE_SEARCH_V1.json` |
| `docs/LITERATURE_SEARCH_V2.json` | `docs/literature/LITERATURE_SEARCH_V2.json` |
| `docs/LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md` | `docs/explanation/LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md` |
| `docs/M1_ATTEMPT2_VALIDATION_ADMISSIBILITY_CENSUS.md` | `docs/experiments/m1/M1_ATTEMPT2_VALIDATION_ADMISSIBILITY_CENSUS.md` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V1.md` | `docs/experiments/m1/M1_DUAL_MEMORY_PROTOCOL_V1.md` |
| `docs/M1_DUAL_MEMORY_PROTOCOL_V2.md` | `docs/experiments/m1/M1_DUAL_MEMORY_PROTOCOL_V2.md` |
| `docs/M1_MEMORY_RETENTION_DECISION_V1.md` | `docs/experiments/m1/M1_MEMORY_RETENTION_DECISION_V1.md` |
| `docs/M1_PHYSICAL_OBSERVATION_DECISION_V1.md` | `docs/experiments/m1/M1_PHYSICAL_OBSERVATION_DECISION_V1.md` |
| `docs/M1_STAGE1_ATTEMPT1_FAILURE.md` | `docs/experiments/m1/M1_STAGE1_ATTEMPT1_FAILURE.md` |
| `docs/M1_STAGE1_ATTEMPT2_FAILURE.md` | `docs/experiments/m1/M1_STAGE1_ATTEMPT2_FAILURE.md` |
| `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` | `docs/experiments/m2/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md` |
| `docs/M2_DEVELOPMENT_EXECUTION_PROTOCOL_V1.md` | `docs/experiments/m2/M2_DEVELOPMENT_EXECUTION_PROTOCOL_V1.md` |
| `docs/M2_GATE_DERIVATION_RECEIPT_V1.json` | `docs/experiments/m2/M2_GATE_DERIVATION_RECEIPT_V1.json` |
| `docs/M2_TRAIN_ONLY_RECEIPT_CANONICALIZATION_V1.md` | `docs/experiments/m2/M2_TRAIN_ONLY_RECEIPT_CANONICALIZATION_V1.md` |
| `docs/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | `docs/experiments/m2/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` |
| `docs/METRICS_PROTOCOL.md` | `docs/contracts/METRICS_PROTOCOL.md` |
| `docs/P1_PHYSIOLOGY_FUSION_PROTOCOL_V1.md` | `docs/experiments/p1/P1_PHYSIOLOGY_FUSION_PROTOCOL_V1.md` |
| `docs/P1_PHYSIOLOGY_RETENTION_DECISION_V1.md` | `docs/experiments/p1/P1_PHYSIOLOGY_RETENTION_DECISION_V1.md` |
| `docs/PHASE3B1_CLASSICAL_BASELINE_RESULTS.md` | `docs/baselines/PHASE3B1_CLASSICAL_BASELINE_RESULTS.md` |
| `docs/PROVENANCE_INCIDENT_V1.md` | `docs/provenance/PROVENANCE_INCIDENT_V1.md` |
| `docs/QWEN_EVALUATION_RUN.md` | `docs/explanation/QWEN_EVALUATION_RUN.md` |
| `docs/REPO_AUDIT.md` | `docs/control-plane/REPO_AUDIT.md` |
| `docs/RESEARCH_SCOPE.md` | `docs/control-plane/RESEARCH_SCOPE.md` |
| `docs/SIGNAL_PROCESSING_CONTRACT.md` | `docs/contracts/SIGNAL_PROCESSING_CONTRACT.md` |
| `docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_AMENDMENT_V1_1.md` | `docs/experiments/t2/T2_ARM_COMPARISON_ANALYSIS_PLAN_AMENDMENT_V1_1.md` |
| `docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md` | `docs/experiments/t2/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md` |
| `docs/T2_ARM_COMPARISON_REPORT_V1.md` | `docs/experiments/t2/T2_ARM_COMPARISON_REPORT_V1.md` |
| `docs/T2_CANONICAL_TRAINING_EXECUTION_SPEC_V1.md` | `docs/experiments/t2/T2_CANONICAL_TRAINING_EXECUTION_SPEC_V1.md` |
| `docs/T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md` | `docs/experiments/t2/T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md` |
| `docs/T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md` | `docs/experiments/t2/T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md` |
| `docs/T2_TRAIN_ARTIFACT_REVIEW_AND_OUTER_ACTIVATION_V1.md` | `docs/experiments/t2/T2_TRAIN_ARTIFACT_REVIEW_AND_OUTER_ACTIVATION_V1.md` |
| `docs/U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md` | `docs/experiments/u1/U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md` |
| `docs/U1_CALIBRATION_RELIABILITY_REPORT_V1.md` | `docs/experiments/u1/U1_CALIBRATION_RELIABILITY_REPORT_V1.md` |
| `docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` | `docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` |
| `docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md` | `docs/experiments/u1/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md` |
| `docs/W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1.md` | `docs/experiments/w1/W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1.md` |
| `docs/W1_WINDOW_COMPARATOR_REPORT_V1.md` | `docs/experiments/w1/W1_WINDOW_COMPARATOR_REPORT_V1.md` |

## Directories hoisted out of `docs/`

| old path | current path |
|---|---|
| `docs/handbook/` (briefly), originally `docs/` | `handbook/` |
| `docs/CARDIOSENTIN*_AUDIT/VERIFICATION/REVIEW*.md` | `audits/` |
| `docs/PAPER_*`, `docs/LITERATURE_SEARCH_V1.md`, `paper/` | `paper/` |
| `handoffs/` | `handoffs/` (unchanged name, moved and moved back) |

## The seven T1 documents were deliberately not moved

**`docs/T1_*.md` and `docs/t1_episode_reasoning.md` remain flat, on purpose.**

The T1 canonical driver's own source files are frozen by SHA-256 —
`tests/neural/test_t1_*.py` assert that `src/cardiosentinel/neural/t1_*.py` are
byte-identical to recorded digests. Those files construct the document paths.
Repointing them at `docs/experiments/t1/` is a correct path fix and *still* a
byte change, so it fails the freeze. That guard is working as designed: the
driver's source is frozen so that the executed protocol cannot drift.

Amending the digests is possible — `T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md` is
the precedent — but it requires a human authorisation and an amendment document.
**Tidying a directory is not a sufficient reason to spend one.** So T1 stays
flat, and this is the record of why.

Fourteen of the fifteen categories hold. If T1 source has to change for a real
scientific reason, move these seven documents in the same amendment and add
their rows to the table above.

## What was deliberately not rewritten

- **Frozen artifacts under `cardiosentinel-runs/`.** Immutable by construction.
- **`docs/literature/LITERATURE_SEARCH_V2.json`.** Its hashed payload records
  `"supersedes": "docs/LITERATURE_SEARCH_V1.json"`. Correcting that string would
  change `payload_sha256`, which is the digest that makes it evidence. The
  pointer is stale; **this table is how it resolves.**
- **The session handoffs, ECG3–ECG23.** Verified byte-identical to their
  committed versions. A stale path in a historical handoff is a broken link, not
  a false statement, and this programme records corrections in the current
  control plane rather than editing the record.
- **Superseded handbook versions v1.2, v1.3, v1.4.** Restored verbatim after a
  first pass rewrote paths inside them. Only v1.5 is current and only v1.5 was
  updated.
- **`audits/CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md`.** Superseded by V2;
  left with the paths it was written against.

## Documents that still carry stale internal paths, on purpose

Editing a document's bytes is not free. **38 documents are digest-pinned; nine
of those are pinned by *other documents* rather than by code, so no test fails
when one is edited** — a decision record quoting the digest of the protocol it
decided on, a report quoting the digest of the plan it executed.

Four such documents still name pre-2026-08-28 paths and were left that way:

| document | pinned by |
|---|---|
| `docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md` | `B4_TEST_AUTHORIZATION_V1`, `B4_TEST_DEFERRAL_DECISION_V1`, `T1_EXECUTION_RECOVERY_AMENDMENT_V1_1` |
| `docs/experiments/b4/B4_TEST_DEFERRAL_DECISION_V1.md` | `EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1` |
| `docs/experiments/t2/T2_ARM_COMPARISON_ANALYSIS_PLAN_AMENDMENT_V1_1.md` | `T2_ARM_COMPARISON_REPORT_V1` |
| `docs/external-validation/EXTERNAL_VALIDATION_STRATEGY_V1.md` | `EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1` |

**This table is how their pointers resolve.**

## Checking this table stays true

```
grep -roh 'docs/[A-Za-z0-9_.-]*' cardiosentinel-runs --include=*.json | sort -u
```

Every path that command prints must appear in the first table above. If one does
not, a document moved without being recorded here.
