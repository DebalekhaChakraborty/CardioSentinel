# CardioSentinel Research Execution Handbook, V1.5

**Control-plane document. Not an experiment report and not the manuscript.**

V1.5 exists to give one authoritative view of what this programme has spent,
established, refused and left open, so that a future session cannot resurrect a
rejected hypothesis, misstate partition authority, or confuse exploratory
evidence with confirmatory evidence.

**It summarizes and links. It does not duplicate the reports, and it creates no
new scientific conclusion.** Where this document and a frozen `_V1` report
disagree, **the report wins** and this document is wrong and must be corrected.

**Supersedes** `CardioSentinel_Research_Execution_Handbook_v1.4.md` for
control-plane purposes. V1.4's §-numbered narrative history is **not** repeated
here and remains the authority for phase history, choreography and governance
mechanics.

---

## 1. Programme charter and research thesis

**Thesis.** An Intelligent Physical System for myocardial-ischemia monitoring
should be judged as a *system* — representation, physiology fusion, memory,
contamination-safe personalization, calibration, episode reasoning and an edge
runtime — rather than as a single classifier score.

**Corpus.** LTSTDB. One dataset, permanently. External corroboration was
declined in writing on 2026-08-24 (`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md`,
§2.4): **no second cohort will corroborate any result in this programme.**

**Standing epistemic posture, unchanged since v1.2:**

- **Development evidence only**, except the single consumed sealed test.
- **Never claim medical or diagnostic performance.**
- **Do not change code in response to a scientific result.**
- **Absence of a lock is evidence** (v1.4 §41.2).
- **Prefer a recorded negative to an unrecorded positive.**

---

## 2. RQ1–RQ7 status

Carried forward from v1.4 §24. **Nothing in E11, E12a or E12d moved any RQ.**

| RQ | Question | Status |
|---|---|---|
| **RQ1** | Does patient-specific memory reduce false alarms without sacrificing sensitivity? | **Open** — no no-memory arm at episode level |
| **RQ2** | Can continual personalization be made contamination-safe? | **Partial** — M2-G retained on development evidence; no episode-level contamination-stress comparison |
| **RQ3** | Can uncertainty reduce cloud dependence without unsafe local decisions? | **Answered — negatively.** Router at `c_star = 0.90` evaluated and **rejected**, `Retained: false` |
| **RQ4** | Does longitudinal/episode reasoning improve monitoring quality? | **Supported (bounded).** W1 difference 0.1921, 95% paired interval [0.0505, 0.3455], excludes zero |
| **RQ5** | Can the selected model operate efficiently on edge hardware? | **Open** — laptop replay simulation only; **no edge-hardware measurement exists** |
| **RQ6** | Does foundation-model knowledge improve the compact student? | **Not started** — Phase 4B |
| **RQ7** | Can confounder-aware supervision reduce false ST alarms? | **Not started** — Phase 6B |

**Two answered, one partial, four open.** RQ3's answer is a rejection.
**RQ4's "(bounded)" may never be dropped when quoting it** — the bound comes off
only if a well-tuned memoryless rule gets its own operating point and still
loses. **The B4 representation branch (E1–E12d) answered no RQ.**

---

## 3. Dataset / partition authority map

| Partition | Subjects | Authority | Status |
|---|---|---|---|
| **TRAIN** | **56** (12 zero-positive, **44 evaluable**) | development | **The only partition any future experiment may use.** E11's prospective 3-fold split lives inside it |
| **VALIDATION (historical)** | **12** (9 with positives) | development | **SPENT for confirmatory purposes.** Used for hypothesis generation across E1–E10. **Must not be used as fresh confirmation** |
| **TEST (sealed)** | — | confirmatory | **CONSUMED 2026-08-25.** `repeat_attempt_permitted: false`. Four sealed artifacts immutable. **Never open them** |
| **E11 B0 outer-held-out geometry population** | **44 evaluable subjects / 79 evaluable streams** | development | **CONSUMED 2026-08-28 for future confirmatory geometry claims** (E13a). May be described; **may not be quoted as fresh held-out confirmation of any geometry hypothesis** |

**The E11 prospective split**, frozen and reused by E12d:

```
split digest  ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3
56 subjects · 3 outer folds 19/19/18 · 44 evaluable · 132 streams
```

| fold | held-out rows | prevalence | inner-train | inner-val | inner-val prevalence |
|---|---|---|---|---|---|
| 0 | 149,042 | 0.2935 | 195,043 | 30,367 | 0.0300 |
| 1 | 118,628 | 0.2601 | 225,626 | 30,198 | 0.0246 |
| 2 | 106,782 | 0.1781 | 243,449 | 24,221 | 0.0251 |

**Inner-validation prevalence runs 8.4×–12.1× below inner-train.** Preregistered,
retained deliberately, **never asserted harmless**.

**Structural enforcement.** `E11FoldAuthority` exposes exactly four
argument-free accessors — `inner_train_rows`, `inner_validation_rows`,
`outer_train_rows`, `outer_held_out_rows`. `E11Partition` has **no member** for
TEST or historical VALIDATION and is not a `str` subclass. Subjects are admitted
by **whitelist** against the authorized population. **TEST is unreachable because
nothing can express it**, not because code declines it.

**No held-out estimate is obtainable within LTSTDB, permanently.**

---

## 4. Sealed-test and one-shot budget status

**All fifteen one-shot budgets are spent.** The B4/neural sealed test was the
fifteenth and last, consumed 2026-08-25 00:17:57Z–00:43:22Z.

**There is no budget left to protect and none left to spend.** The governance
machinery no longer guards an unspent access; it guards the **record** of
accesses already taken. Every `*_AUTHORIZED` flag sitting `True` on disk is a
**spent token, not a live permission.**

**Every training run now requires a fresh, explicit human authorization.**
E11 ATTEMPT 1/2, E12d ATTEMPT 1/2 each required one and each got one.

**NO AUTOMATIC RETRY.** Never add `--force`, `--retry`, `--reset`,
`--overwrite` or `--fresh-seed`. Re-execution after a failure is a **new
attempt requiring new authorization** (§A8 policy).

---

## 5. Environment / reproducibility authority

| | |
|---|---|
| **Scientific interpreter** | `/home/AI_POC/venvs/tactics/bin/python` — 335 packages, Python 3.12.6 |
| Application interpreter | `venvs/debalekha` — **never use for science** |
| **Never** | install, upgrade or downgrade anything in `tactics` |

**Determinism surface.** `B4BTransformerCNN` contains dropout, so the **global
RNG stream is load-bearing during training**. The registered construction order
is binding:

```
initialize_determinism() -> model -> optimizer -> loss -> train loader -> inner-validation loader
```

**A DataLoader with `generator=None` draws its worker `base_seed` from the
global RNG once, at first iteration.** With `persistent_workers=True` that draw
happens **once per loader**, so sharing a loader across fits silently deletes a
draw. This destroyed E12d ATTEMPT 1 (§7). `FitScopedLoaderCache` now makes it
structurally impossible and `tests/neural/test_e12d_loader_scoping.py` pins it.

**Known traps, all hit at least once:**

1. **`NaN * 0 == NaN`** — masking by multiplication does not exclude a row. Killed E11 ATTEMPT 1. Use index selection.
2. **B4 arrays are lexicographic, not chronological — 0 of 132 streams are in time order.** `start_sample` is recoverable from the stable id. The M1 cache *is* chronological.
3. **`grep -r` here is ugrep and skips gitignored paths** — the evidence trees are gitignored.
4. **The Bash cwd resets to `/home/AI_POC`.**
5. **AUPRC is bounded below by prevalence.** Never compare across sets of differing prevalence.
6. **Print the denominator every time** — subject-macro is over 9 of 12 on validation, 44 of 56 on train.
7. **A tool-call timeout can SIGTERM a background job.** Launch with `setsid nohup`, no timeout-linked sleep. Killed E11 ATTEMPT 0.
8. **`/tmp` scratchpads are per-session and not durable.**

---

## 6. Experiment ledger E1–E12d

**Every entry below is a *mechanism* finding. None is generalization evidence.**

| Exp | Question | Outcome |
|---|---|---|
| **E1** | Is information absent from the B4 embedding, or present but unused? | **Unresolvable at n=12.** All 5 contrasts include zero; one score set, two metrics, opposite verdicts |
| **E2 / E2b** | Do B4-A/B/C candidates separate? | **No.** All paired intervals include zero. The epoch bootstrap was an invalid instrument |
| **E3** | Is the operating point a prior artifact? | **Yes for calibration, no for ranking.** Brier 0.0656→0.0421, NLL 0.2274→0.1654, AUPRC/AUROC by **exactly 0.0** |
| **E6a** | Would more subjects resolve anything? | **Cannot tell.** Width-scaling exponent ≈ **−0.15**, not −0.5. The `1/√n` projection was **withdrawn** |
| **E7a** | Static subject-wise score normalization? | **Refuted in direction.** Perfect normalization (ECDF) is the *worst* arm |
| **E7b** | Static stream-wise normalization? | **Refuted.** Stream variation is discriminative quality, not offset |
| **E8a** | Does M1 memory identify unreliable windows/streams? | **Windows yes, streams no.** Memory measures **atypicality** |
| **E8b** | Does M1 add information beyond the B4 score? | **Yes, survives conditioning.** `d_long` concordance 0.836 → **0.712** stratified. **C0/C1 probe proposed, NOT executed** |
| **E9** | Lead / polarity / label semantics? | **Channel-specific but polarity-agnostic.** Elevation and depression collapse into one class |
| **E10** | Is the class direction stable on unseen subjects? | **TRAIN LOSO cosine min +0.971, 0/79 negative.** The 3 validation failures are the 3 lowest cosines, 3 smallest ‖delta‖, 3 lowest centroid separations. **The head is faithful; the representation fails** |
| **E11** | Does a morphology auxiliary objective (λ=0.1) improve unseen-stream direction stability? | **CATEGORY C — mechanism NOT ESTABLISHED.** All three primary geometry intervals include zero |
| **E12a** | Was selection stable, and was the auxiliary objective mature at selection? | **DECISION C — no further conclusion.** Selection demonstrably weak; auxiliary maturity **unobservable** |
| **E12b/c** | Instrumentation and end-to-end observability | **Implementation only.** No science. Runner declared observability-ready |
| **E12d** | Was the auxiliary objective still evolving after selection? | **DECISION D — no further conclusion.** Replication gate **PASSED**; auxiliary had **not plateaued**; **no coherent B1-specific geometry continuation** |
| **E13a** | Are held-out geometry failures temporally reproducible, and are reversal / weak magnitude distinct? | **DECISION D — no coherent mechanism established.** Within-stream direction is highly stable (median `cos_within` **+0.9935**, sign agreement **56/57**); **one of two eligible negative streams reproduces, the other does not**. Population now **consumed** for confirmatory geometry |

**Authoritative reports:** `B4_E10_…REPORT_V1.md`,
`B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_REPORT_V1.md`,
`B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1.md`,
`B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_REPORT_V1.md`.

---

## 7. Failed-attempt / quarantine ledger

**Quarantined evidence must never enter a scientific calculation.**

| Attempt | Classification | Interpretable | Cause |
|---|---|---|---|
| **E11 ATTEMPT 0** | launch failure | **NO** | Tool-call timeout SIGTERM'd the job. No scientific outcome |
| **E11 ATTEMPT 1** | apparatus failure | **NO** | `NaN * 0 == NaN` in the auxiliary mask. Fold 0 B0 completed and its values are **QUARANTINED** — used only as ATTEMPT 2's bit-for-bit reproduction gate. `B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md` |
| **E12d ATTEMPT 1** | harness / RNG-replication failure | **NO** | Inner-validation DataLoader shared across each fold's B0/B1 fits, deleting one global RNG draw per fold. **All three B0 fits reproduced E11 bit-identically; all three B1 fits diverged from epoch 2.** Receipt never passed `DATA_BOUND`. `E12D_ATTEMPT_1_CLASSIFICATION.md` |

**E12d ATTEMPT 1's B1 trajectories must never enter E12d results. ATTEMPT 2 is
the only scientific E12d execution.**

**Pattern worth naming:** all three failures were **harness defects that the
governance machinery caught before interpretation**, not scientific
disappointments. Each was caught by a gate that existed because an earlier
failure taught the programme to build it.

---

## 8. Established findings

Findings that survive their own uncertainty and may be stated without hedging
beyond the boundaries attached to them.

1. **RQ3 is answered negatively.** The uncertainty router was built, evaluated against a prespecified gate, and **rejected**.
2. **RQ4 is supported, bounded.** W1 difference 0.1921, interval [0.0505, 0.3455]. **"(bounded)" is not optional.**
3. **The B4 class direction is highly coherent on training streams and occasionally reverses on unseen ones.** E10: TRAIN LOSO cosine min **+0.971**, **0/79 negative**. E11 replicated this prospectively on **44 evaluable subjects / 79 evaluable streams**: B0 median cosine **+0.9777** with **3/79 negative**.
4. **The frozen head is faithful.** E10 established the failure is representational, not in the classifier head.
5. **The representation is not subject-dominated.** Class separation exceeds between-subject centroid dispersion by **26×** on TRAIN and **12×** on VALIDATION (E10; registered prediction 5 refuted).
6. **Prior correction moves calibration and not ranking.** Brier and NLL improve; AUPRC and AUROC move by **exactly 0.0** (E3).
7. **The morphology auxiliary objective at λ = 0.1 does not establish improved unseen-stream direction stability.** E11 Category C: all three primary intervals include zero.
8. **That objective had not plateaued when selection stopped it.** E12d: continued post-selection decrease in **all three folds**, `F_aux` = **+0.6208 / +0.2556 / +0.5378**, all post-selection trajectories monotone (`V == F`).
9. **E12d reproduced E11's phase-1 computation exactly** — six fits AUPRC bit-identical, selected epochs **1,1,1,2,4,1**, counts **5,5,5,6,8,5**, B0 `train_loss` bit-identical.
10. **The selection instrument is weak.** Four of six E11 margins fall below E2's documented **+0.032** argmax bias; fold 1 B1's margin is **+0.00029213**; AUPRC and loss epoch ordering disagree in **6/6** fits.

---

## 9. Suggestive-but-unresolved findings

**These may be described. They may not be built upon as if established.**

1. **M1 memory adds information beyond the B4 score** (E8b, `d_long` concordance 0.712 stratified, broad across 7/9 subjects) — but the **C0/C1 incremental probe was proposed and never executed**.
2. **Subject-macro AUPRC nominally separated B1 from B0** in E11: **+0.0258, 95% CI [+0.0002, +0.0562]**, 29/44 subjects. **Secondary, fragile — the lower bound is two ten-thousandths from zero — and unsupported by the primary mechanism.** It is **not** E11's headline.
3. **All three E11 primary geometry point estimates moved in the predicted direction** (+0.0030 cosine, +0.1217 ‖delta‖, −0.0127 negative fraction) while **all three intervals include zero**. Directional agreement is not establishment.
4. **Representation geometry continues to evolve after AUPRC selection in most fits** — 5 of 6 selected epochs precede the largest observed geometry movement (E12d). **This is not evidence that later geometry is better.**
5. **AUROC and AUPRC peak at different epochs in every E12d fit.** Observed, recorded, and **not** used to propose an alternative selection metric.
6. **B1's fold-2 TRAIN consensus contains one negative-cosine stream** (`s20471:1`, cos −0.4625, **12 positive windows**). An observed secondary diagnostic, outside every registered endpoint.

---

## 10. Rejected / closed hypotheses

**Do not resurrect these. Each was tested and closed on recorded evidence.**

| Hypothesis | Status | Authority |
|---|---|---|
| Uncertainty routing reduces cloud dependence safely | **REJECTED** at `c_star = 0.90`, `Retained: false` | RQ3 / U1 |
| Static subject-wise score normalization helps | **REFUTED IN DIRECTION** — ECDF is the worst arm | E7a |
| Static stream-wise normalization helps | **REFUTED** — stream variation is discriminative quality | E7b |
| The representation is subject-dominated | **REFUTED** — 26× / 12× separation ratio | E10 |
| The B4 head is the failure surface | **REFUTED** — the head is faithful | E10 |
| Memory identifies unreliable *streams* | **REFUTED** — windows yes, streams no | E8a |
| Prior correction improves ranking | **REFUTED** — AUPRC/AUROC move by exactly 0.0 | E3 |
| Polarity predicts held-out failure | **REFUTED** — target is polarity-agnostic | E9 |
| SQI predicts held-out failure | **REFUTED** | E9 |
| The `1/√n` subject-scaling projection | **WITHDRAWN** — measured exponent ≈ −0.15 | E6a |
| Epoch-bootstrap as an uncertainty instrument | **INVALID** — bootstrapping an argmax pins to the max | E2 |
| "Class-direction collapse" as a categorical endpoint | **DELETED before execution** — no defensible TRAIN-only threshold | E11 amendment A4 |
| Remaining-descent fraction `R(x)` as a diagnostic | **WITHDRAWN before execution** — degenerate at s=1, and 4/6 fits select epoch 1 | E12d amendment §7.0 |
| External corroboration via EDB | **DECLINED IN WRITING** — no second cohort, permanently | Route A decision |

**Not authorized and repeatedly declined for the B4 branch:** λ sweeps,
alternative morphology targets, a second auxiliary head, direct
class-direction losses, subject-adversarial objectives, lead embeddings,
polarity normalization, larger heads, architecture search, and any augmentation
chosen from an outcome.

---

## 11. Explicit non-claims

**The programme does not claim, and must not be cited as claiming:**

1. **Any medical or diagnostic performance.** Development evidence on a research corpus.
2. **Any generalization beyond LTSTDB.** One corpus, permanently; external corroboration declined.
3. **That morphology-aware representation learning does not work.** E11's null is scoped to *one target, one λ = 0.1, one architecture, one seed per arm per fold*.
4. **That any epoch other than the selected one would perform better.** E12d observed **no** outer outcome.
5. **That later representation geometry is better.** Continued evolution is not improvement.
6. **That B1 and B0 differ beyond single-seed training variance.** E11 A3 registers that V1 cannot separate them.
7. **Any inferential claim from three folds**, or from 44 subjects where the interval is wide.
8. **That the sealed test answered a research question.** It characterises the selected encoder on held-out subjects and moved no RQ.
9. **Any edge-hardware performance.** A laptop replay simulation is not an edge measurement.
10. **Anything derived from quarantined attempts** (§7).

---

## 12. Agentic / Qwen governance findings

**Every agent is grounded on the evidence graph and none is autonomous.**

```
agents/  evidence · graph · context · research · architecture · evaluation
         claims.py · explain.py · providers.py · cli.py
```

- **The claim guard is executable, not advisory.** `claims.py` encodes the publication boundary as **18 Appendix A patterns**; a violation **falls back to deterministic prose rather than publishing the claim**.
- **The evidence graph is closed** — 35 nodes / 39 edges per alert, closed node kinds and edge relations. Agents may not invent a node kind.
- **The open-weight Qwen provider is opt-in and local, and the generative arm HAS been exercised — once.** `EXPLANATION_EVALUATION_REPORT_V1.md` reports **n = 1 context**, Qwen3-1.7B and Qwen3-4B-Instruct-2507: **evidence fidelity 1.000, 0 claim violations, completeness 1.000, latency 63.4014 s**. **The runtime refused that generation** — it asserted a `G1`–`G6` range passed while **G4 and G5 were blocked**, and the inversion **reproduced on two independent runs**. **This is a demonstrated failure mode, not a failure rate.** The separate manual run contract `QWEN_EVALUATION_RUN.md` remains **NOT EXECUTED**.
- **The Architecture Selection Agent manages lifecycle, not recommendation.** It does not choose a model.
- **The research assistant's current-state topic is `sealed_test_consumed`** — it reports attempt 1 `COMPLETE`, repeat prohibited, and routes stale-premise questions about an "unopened" test to the consumed record. `research.py` still repeats U1/T2 `source_lock: unopened` values; **those are correct historical attestations about those runs, not claims about today's repository.**

**Governance finding worth preserving:** the agentic layer's value here has been
**refusal**, not generation. Its measurable contribution is the claims it
declined to emit.

---

## 13. IPS component status

| Component | Evidence | Status |
|---|---|---|
| **B4-B** neural encoder | `phase3b2-architecture-v1` | **COMPLETE · SELECTED** over B4-A/B4-C · **sealed test CONSUMED 2026-08-25** |
| **P1-B** physiology fusion | `phase4-p1-physiology-v1` | **COMPLETE · RETAINED**, FPR caveat recorded |
| **M1L** long-timescale memory | `phase5-m1-dual-memory-v2` | **COMPLETE · RETAINED** |
| **M2-G** contamination-safe gate | `phase6-m2-development-v1` | **COMPLETE · RETAINED** |
| **U1** calibration | `phase7-u1-development-v1` | **COMPLETE** · Platt **RETAINED**, router **REJECTED** |
| **T2** longitudinal comparison | `phase8-t2-development-v1` | **COMPLETE** · S4D selected; **contrast interval spans zero** |
| **T1** episode reasoning | `phase9-t1-*` | **COMPLETE** · canonical attempt **CONSUMED**, failed post-claim at stage 24; continuation measured and reported |
| **W1** window comparator | derived, no run directory | **COMPLETE · RQ4 supported (bounded)** |
| **IPS runtime** | `edge/`, 1,692 lines | **COMPLETE** · laptop replay simulation, **not edge hardware** |

**Not started:** E1 edge hardware (RQ5), Phase 4B (RQ6), Phase 6B (RQ7).
**Declined:** EDB external validation.

**Still unanswered and not an RQ:** what the S4D architecture contributed. T2's
interval spans zero and `s4d_temporal_evidence_s_t` feeds both W1 arms.

---

## 14. Artifact / receipt / report index

**Plans and reports (`docs/`)** — the authoritative scientific record:

```
B4_E10_REPRESENTATION_GEOMETRY_{PLAN,REPORT}_V1.md
B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_{PLAN,REPORT}_V1.md
B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md
B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1.md
B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_{PLAN,REPORT}_V1.md
B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md · IMPROVEMENT_ROADMAP_V1.md
EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md · CURRENT_STATE.md
```

**Run roots (`cardiosentinel-runs/`, gitignored):**

```
b4-e11-morphology-aware-v1/
  E11_ATTEMPT_2/                        manifest digest 5d357209…f49359 (17 files)
  E12D_PHASE1_REPLICATION/              ATTEMPT 1 — QUARANTINED
  E12D_PHASE1_REPLICATION_ATTEMPT_2/    the scientific E12d execution
```

**Key digests:**

| Item | Digest |
|---|---|
| E11 split assignment | `ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3` |
| E11 ATTEMPT 2 artifact manifest | `5d357209005bf1571e3a740219dd89f6cd770ea62ee00b17c6c9806985f49359` |
| E12d execution plan | `109c42a14daaf202e604994b40e4f349285783ff846d72a512088a4fe290c924` |
| E12d data binding | `b5eba39843631530681768975d94b8dd6c6d2c78ea13fa02945c7447f461c3d6` |

**Instrumentation (`src/cardiosentinel/neural/`):** `e11_authority`,
`e11_data_binding`, `e11_instrumentation`, `e11_checkpoints`,
`e11_geometry_trajectory`, `e11_outer_geometry`, `e11_run_state`,
`e11_future_runner`, `e12d_orchestrator`. Test suite: **3,075 passing**.

---

## 15. Paper claim matrix

**Drafted, verified by file presence:** **§5.6**
(`PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`), **§9** (`PAPER_S9_DISCUSSION_DRAFT.md`,
`PAPER_S9_DISCUSSION_SKELETON.md`), and **§4 / §4.6**
(`PAPER_S4_EVIDENCE_FRAMEWORK_DRAFT.md`, 2026-08-28).

**§2 Related Work is now drafted** (`PAPER_S2_RELATED_WORK_DRAFT.md`,
2026-08-28) from a **targeted five-query search, not a systematic review** — a
qualification the draft carries into its own gap statement. One citation is
**VERIFIED** (the LTSTDB reference, fetched from PhysioNet); the rest are
**SEARCH-RETURNED and must be fetched and confirmed before submission**.
It carries the §6.3 condition of `B4_TEST_AUTHORIZATION_V1.md`: **§2 must not be
shaped by the sealed-test result**, and §2.0 records how that is honoured.

| Claim | Supportable? | Required qualifier |
|---|---|---|
| System-level IPS design for ischemia monitoring | **Yes** | Development evidence; simulation, not edge hardware |
| Episode reasoning improves monitoring quality | **Yes** | **"(bounded)"** — operating point chosen with the thing under test in the loop |
| Uncertainty routing rejected on prespecified gate | **Yes** | A negative result, reported as one |
| Class direction coherent on train, occasionally reversed on unseen streams | **Yes** | E10 + E11 prospective replication, 44 subjects / 79 streams |
| The head is faithful; failure is representational | **Yes** | Development evidence |
| Morphology auxiliary objective improves generalization | **NO** | E11 Category C — must be reported as **not established** |
| Any epoch/threshold would have done better | **NO** | Never evaluated |
| Edge deployment performance | **NO** | No edge-hardware measurement exists |
| External generalization | **NO** | Declined, permanently |
| Diagnostic/clinical performance | **NO — prohibited** | Standing constraint |

**The binding gap is the manuscript, not model capability.**

---

## 16. Current frontier and open questions

**Nothing is currently authorized. No experiment is designed or pending except
`E13a`, which is preregistered and NOT authorized.**

**The open scientific question, stated exactly:** E12a asked whether E11's null
came from a **weak objective** or a **weak delivery mechanism**. E12d showed the
objective was still learning when delivery stopped — but **could not show that
this distinguishes B1 from B0**. **That question remains open.**

**Live branches, none authorized:**

1. **E13a — COMPLETE, Decision D.** The B4 held-out geometry population is now **consumed for confirmatory purposes**; this branch cannot be advanced further on this corpus without a partition the programme does not have.
2. **E8b's C0/C1 incremental probe** — proposed in E8b, never executed.
3. **The manuscript §4 / §4.6** — needs no authorization and no compute, and every source is on disk.

**What this programme is good at, and the standing danger:** producing correct,
well-recorded negative results and the governance to protect them. **Twelve
mechanism findings, a consumed sealed test, two completed prospective
experiments — and still no §4.** Every remaining scientific question needs
either a new authorization or data this programme does not have. **The
manuscript needs neither.**
