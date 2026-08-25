# Research Scope

## Objective

CardioSentinel investigates continuous detection of transient ischemic ST
episodes in ambulatory ECG. Detection research is not clinical diagnosis: this
repository must not recommend treatment, declare a patient condition, or claim
clinical effectiveness without appropriate external evidence.

The intended physical-to-digital-to-physical loop is ECG acquisition or
real-time replay, edge signal processing, patient-adaptive inference,
uncertainty estimation, local decision or cloud escalation, temporal episode
reasoning, and evidence-grounded alert generation. An alert is a research output
for evaluation, not a diagnosis.

## In scope

- Reproducible ingestion of appropriately licensed ECG datasets and annotations.
- Subject-independent representation learning, patient-specific baseline memory,
  physiology-guided ST-T features, calibrated uncertainty, temporal episode
  reasoning, and edge/hardware benchmarking.
- Evaluation against ischemic and non-ischemic ST-event confounders.

## Out of scope

- Clinical diagnosis, treatment recommendations, a medical-device claim, or
  patient-facing decision support.
- An LLM, dashboard, API, cloud deployment, or model training in Phase 0.

## Research hypotheses and limitations

The research hypotheses are that subject-independent learning can be improved by
patient-specific baseline memory; morphology-aware fusion can improve robustness;
calibrated uncertainty can make routing safer; and temporal reasoning can reduce
isolated-window false alerts. These are hypotheses, not established results.

Current state: EDB and LTSTDB are integrated with validated annotation labels,
and models exist across every layer above (classical, neural, physiology,
memory, calibration, and longitudinal temporal); see `docs/CURRENT_STATE.md`
for the experiment-by-experiment ladder. The B4-B neural sealed evaluation was
consumed once on 2026-08-25: attempt 1 completed, repeat is prohibited, and the
registered result is available through
`docs/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md`. All fifteen one-shot budgets are
now spent. None of this is clinical validation or evidence of generalization:
the neural result is one uncorroborated evaluation on twelve test subjects from
one dataset, and no edge-hardware target has been selected.
