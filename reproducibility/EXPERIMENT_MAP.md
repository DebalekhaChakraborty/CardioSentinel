# Experiment map — claim to artifact to test

Which published claim rests on which artifact, which lock froze it, and what
re-verifies it. **Demo tier re-verifies none of these**; it reproduces the
system's behaviour, not its scientific claims.

| Claim | Artifact | Lock | Re-verified by |
|---|---|---|---|
| T1 subject-macro `episode_f1` 0.2524, 95% [0.0826, 0.4415] | `phase9-t1-continuation-v1` | `T1_EXPERIMENT_LOCK.json` | `docs/T1_DESCRIPTIVE_REPORT_V1.md` + `gen_t1_descriptive_report.py` |
| T2 difference 0.093215, 95% [-0.015229, 0.148951] | `phase8-t2-development-v1/t2-v1-outer-validation` | `T2_OUTER_VALIDATION_EXPERIMENT_LOCK.json` | `gen_t2_arm_comparison_report.py` |
| W1 difference 0.1921, 95% [0.0505, 0.3455] | T1 held-out re-read | — | `gen_w1_window_comparator_report.py` |
| U1 router **rejected**, ratio 6.4536 vs limit 3.0 | `phase7-u1-development-v1` | `U1_EXPERIMENT_LOCK.json` | `docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` |
| U1 calibration retained, NLL 0.143708 vs 0.231705 | same | same | `gen_u1_reliability_report.py` |
| B4-B selected, 309,809 params | `phase3b2-architecture-v1` | `EXPERIMENT_LOCK.json` | `docs/B4_GLOBAL_ENCODER_SELECTION_V1.md` |
| B4-B sealed evaluation consumed once, pooled AUPRC 0.0935334 | `phase3b2-architecture-v1/B4B_cnn_transformer_v1/TEST_*` | `TEST_ATTEMPT.json`, attempt 1 `COMPLETE`, repeat prohibited | `docs/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` + immutable `TEST_AUDIT.json` |
| Live representation == frozen corpus (6 ULP) | full feature corpus | — | `tests/edge/test_representation_matches_frozen_cache.py` |
| M2 order preserved by `step()` extraction | corpus rows | — | `tests/neural/test_m2_step_matches_replay.py` |

## What the demo tier does **not** re-verify

The representation-equality and M2-order tests need the 16 GB feature corpus and
**skip on a fresh checkout**, naming the missing trees. That skip is deliberate:
this repository has been bitten by tests that passed in CI because evidence was
gitignored and failed on every machine that held it.

## One-shot budgets

**15 tracked, 15 spent.** The B4 neural sealed evaluation was consumed once on
2026-08-25: attempt 1 is `COMPLETE` and `repeat_attempt_permitted` is `false`.
No path in this package touches or reproduces its test artifacts; the demo tier
continues to use development artifacts and a validation record only. Handbook
§51 is the canonical ledger, and
`docs/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` is the bounded account of the
registered result.
