# Implementation Plan

Future changes must be independently reviewable and must follow the experiment
contract. See `docs/control-plane/CURRENT_STATE.md` for the current experiment ladder,
selected models, and open work; this file tracks which plan items have been
addressed, not day-to-day status.

1. **Dataset ingestion and annotation validation:** implementation and
   annotation-semantic validation complete. Versioned EDB and LTSTDB contracts,
   strict WFDB metadata inspection, annotation preservation, manifest
   generation, leakage validation, remote header/annotation validation, and
   synthetic tests are available.
2. **Signal-processing pipeline:** causal implementation and bounded waveform
   integration validation complete. Includes physical-unit loading, raw and
   optional stateful SOS profiles, causal windows, descriptive quality metrics,
   response audits, and provenance.
3. **Reproducible baselines:** Phase 3A benchmark protocol, frozen subject split,
   leakage-safe window targets, sampling policy, and metrics protocol complete.
   Phase 3B-1 implements frozen waveform-only signal and R-aligned morphology
   schemas, resumable external feature materialization, B0--B3 global classical
   baselines, validation-only threshold locks, and sealed-test reporting. Full
   results are complete: each frozen B0--B3 baseline received one sealed-test
   evaluation (`PHASE3B1_CLASSICAL_BASELINE_RESULTS.md`). The B4 neural
   baseline that follows it is also complete on validation: compact CNN,
   CNN-Transformer, and CNN-SSM candidates were trained and compared, and
   B4-B (CNN-Transformer) is the selected official model
   (`B4_GLOBAL_ENCODER_SELECTION_V1.md`).
4. **Patient-adaptive memory:** contamination-safe short- and long-term baseline
   mechanisms. Complete: short-memory, dual-memory, and long-memory variants
   (M1S/M1D/M1L) were implemented and evaluated; M1L is the selected variant
   (`M1_MEMORY_RETENTION_DECISION_V1.md`), after two earlier attempts failed
   and were documented rather than silently retried.
5. **Physiology-guided model:** justified fusion of ECG representations and ST-T
   morphology. Complete: a plain neural head (P1A) and a physiology-fusion
   model (P1B) were compared, and P1-B is selected
   (`P1_PHYSIOLOGY_RETENTION_DECISION_V1.md`).
6. **Uncertainty calibration:** held-out calibration, reliability metrics, and
   abstention/routing controls. Partial, and the outcome is a **split**
   retention (`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` §2): Platt
   calibration on the recovered logit is retained and frozen, together with the
   subject-disjoint OOF calibrated probabilities and the final all-VALIDATION
   calibrator. The symmetric window-level selective router at `c_star = 0.90`
   is **not** retained, and neither `u_star_dev` nor `u_star_deploy` is retained
   as a routing threshold. The abstention/routing half of this item was
   evaluated and rejected, not delivered.
7. **Temporal episode reasoning:** event construction, onset-delay, and
   false-alarm-per-hour evaluation. Partial: the longitudinal half (causal S4D
   vs. a GRU baseline) is complete, trained, and one-shot outer-validated
   (`T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md`). The episodic/alerting
   state-machine half (internally "T1") has been **executed and measured**. The
   canonical attempt ran 2026-08-21 at `c538181`, failed post-claim at stage 24
   and is consumed; the single authorized measurement continuation ran
   2026-08-22 at `61704aa` and completed. The result is reported in
   `T1_DESCRIPTIVE_REPORT_V1.md`: registered primary subject-macro mean
   `episode_f1` of 0.2524, 95% subject-bootstrap interval [0.0826, 0.4415],
   with seven of twelve subjects scoring zero across two incomparable failure
   modes (`T1_POST_HOC_ANALYSIS_V1.md`). No further T1 execution is authorized.
   The false-alarm-per-hour and temporal-IoU evaluation named in this item's
   scope was **never computed** and may not be reported.

   The longitudinal half was subsequently analysed
   (`T2_ARM_COMPARISON_REPORT_V1.md`, as amended by
   `T2_ARM_COMPARISON_ANALYSIS_PLAN_AMENDMENT_V1_1.md`): the predefined rule
   selected the causal S4D arm on the observed validation contrast, that
   contrast **is** the selection criterion, and its paired subject-bootstrap
   interval includes zero. No superiority claim follows.

   The episodic half was given the comparator it lacked
   (`W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1.md` →
   `W1_WINDOW_COMPARATOR_REPORT_V1.md`): a memoryless window-only rule, on
   identical rows under identical frozen thresholds, scores materially lower
   than the state machine, with a paired interval excluding zero. **This is the
   programme's first affirmatively answered research question (RQ4), and it is
   bounded** — both arms ran at an operating point selected with the state
   machine in the loop, so it does not establish that episode reasoning beats
   window-level alerting in general.
8. **Edge/cloud routing:** confidence-aware policy evaluated without clinical
   claims. **Not delivered.** The window-level policy was evaluated under item 6
   and rejected — see item 6 for what that decision does and does not retain.
   §11 of that decision defers final edge/cloud routing to be reconsidered
   prospectively after temporal reasoning, and freezes no future routing
   algorithm. The evaluation is a completed negative result; the item is not
   complete.
9. **Edge benchmarking:** reproducible latency, energy, and hardware-in-the-loop
   measurements. Partial: B4 latency and parameter-count benchmarking is
   complete on a fixed benchmark host (`B4_RESOURCE_BENCHMARK_V1.md`), and a
   laptop replay runtime now exists in `edge/` running at ~61x real time;
   **neither is an edge-hardware measurement.** No on-device latency, energy or
   thermal figure exists, and RQ5 is open.
10. **Final ablation and external validation:** pre-specified comparisons,
    confounder analysis, and bounded reporting. The first ablation is done —
    see item 7's window-only comparator. External validation is **scoped but
    not performed** (`EXTERNAL_VALIDATION_STRATEGY_V1.md`), and the scoping
    result is itself the finding: **no independent ST-episode cohort exists in
    the public record.** EDB is available only as a *secondary* cohort — 15
    records are excluded for documented LTSTDB overlap, the remaining 75 are
    not proven independent, and its ~2-hour excerpts sit largely in the
    cold-start regime where the model is weakest. STAFF III has gold-standard
    occlusion timing but fails on sampling rate, lead set, recording duration,
    annotation type and ischemia mechanism. No cohort has been acquired and no
    contract has been changed.
