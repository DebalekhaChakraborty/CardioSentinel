# Abstract-to-body claim audit, V1

**Not manuscript prose.** Every substantive sentence of the abstract in
`CARDIOSENTIN_TACTICS_MANUSCRIPT_V3_FINAL_CANDIDATE.md`, mapped to the body
section that supports it and to the frozen authority behind that section.

**The controlling rule: "stronger than body" must be NO on every row.** Where a
draft sentence was stronger, the abstract was weakened. The body was never
strengthened to accommodate it.

| # | Abstract claim | Body § | Figure / table | Frozen authority | Qualification preserved | Stronger than body |
|--:|---|---|---|---|:--:|:--:|
| 1 | Continuous physiological monitoring is a physical–digital systems problem, not only a classification problem | §1 ¶1 | F1 | framing; no quantity | n/a | **NO** |
| 2 | Signal → causal computation → patient-relative state → irrevocable decision → report to a person | §1 ¶1, §3, §2.7 | F1 | `PAPER_OUTLINE_V2` §3.5; handbook §52/§55 | n/a | **NO** |
| 3 | Two governance questions usually asked separately | §1 ¶3, §2.6 | — | `CARDIOSENTIN_RELATED_WORK_VERIFICATION_V2` §7 | "usually", not "never" | **NO** |
| 4 | CardioSentinel integrates representation, physiology, memory under a contamination-safe gate, calibration, temporal episode reasoning, evidence graph | §3.1–§3.6 | F1, T1 | `T1` component table; each component's retention decision | no component credited with a gain | **NO** |
| 5 | **We couple** the two questions under one provenance/authority model | §1, §4, §8, §10.4 | F2, F5 | `B4_TEST_AUTHORIZATION_V1`; `agents/claims.py`; `agents/graph.py` | "couple", never "introduce the first" | **NO** |
| 6 | Prior work covers each half; **to the best of our targeted review, no prior system spans both under one authority** | §2.6 | — | `..._VERIFICATION_V2` §8, §10 — corrected matrix | qualified review language; both halves conceded as precedented | **NO** |
| 7 | Episode reasoning improves episode-level agreement over a memoryless window rule, on identical rows, **at the promoted operating point** (+0.1921, 95% CI [0.0505, 0.3455], 12 held-out subjects) | §6.2, §1.1 C2 | F3, T2 row 1 | `T1_DESCRIPTIVE_REPORT_V1`, `W1_WINDOW_COMPARATOR_REPORT_V1` | claim-guard-licensed wording verbatim; operating-point clause present | **NO** |
| 8 | **In the single evaluated generative context**, an explanation scoring 1.000 evidence fidelity, 0 claim violations, 1.000 completeness asserted G1–G6 passed while G4 and G5 were blocked | §8.1, §8.2, §1.1 C4 | F5, T2 row 18, T3 | `EXPLANATION_EVALUATION_REPORT_V1` | scope stated; **no rate claimed** | **NO** |
| 9 | A categorical state-alignment gate refused it and the runtime served a deterministic fallback | §8.2, §8.4 | F5 | same | refusal reported as the behaviour, not as a safety guarantee | **NO** |
| 10 | Replay runs at roughly **61× real time in laptop simulation** | §9 | T2 row 16 | handbook §55; 1,079 windows / 89 s | "laptop simulation" present; edge language absent | **NO** |
| 11 | Prespecified gates also **rejected an uncertainty router** and **closed a representation-improvement branch** | §7.2, §5.2, §10.2 | T3, T4 | `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1` (`Retained: false`); E11 Category C, E12d/E13a Decision D | reported as rejection and closure, not as success | **NO** |
| 12 | Evaluation uses **one primary ambulatory corpus with no independent external cohort** | §11 ¶1 | T4 | `EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1`, declined 2026-08-24 | both facts in the abstract, not only §11 | **NO** |
| 13 | A **single-use, encoder-only** sealed evaluation showed **weak, heterogeneous** cross-subject performance | §5.1, §11 | T2 rows 4–6, T4 | `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1`; `TEST_ATTEMPT.json` | qualitative by choice; encoder-only and single-use both stated | **NO** |
| 14 | **This is governed monitoring research, not diagnostic validation** | §1 ¶5, §11, §12 | — | handbook Appendix A; `agents/claims.py` | boundary statement | **NO** |

**Stronger than body: NO on all 14 rows.**

## Decisions taken while drafting, and why

**The sealed AUPRC is not in the abstract.** Row 13 is qualitative. The brief
permits the number with mandatory `encoder-only` and prevalence `0.0460529`
attached; carrying both qualifiers costs more abstract space than the number
buys, and the qualitative form ("weak, heterogeneous") is what the body
actually supports. **The number is not hidden** — §5.1, §11, §12 and Table T2
rows 4–6 all carry it with both qualifiers. Removing it from the abstract
removes an achievement-shaped number, not a disclosure.

**Three quantitative anchors, not four**, per the brief. Rows 7, 8 and 10. Row
11 is deliberately qualitative: it shows the gates can return no without
spending a slot.

**One draft sentence was weakened.** An earlier version read *"no prior system
spans both surfaces under one authority"* without the review qualifier. That is
stronger than §2.6, which says *"to the best of our targeted review"*. The
abstract now carries the qualifier and concedes in the same sentence that prior
work covers each half.

**Row 7's wording is not paraphrased.** Appendix A claim 6 licenses exactly one
improvement claim and specifies its form. The abstract uses that form verbatim
rather than a shorter equivalent, because a shorter equivalent is what the guard
exists to catch.
