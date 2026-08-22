# W1 Window-Only Comparator — Report, V1

**Step 3 of `docs/W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1.md`: the first read of comparator values.** Produced
under the §6 authorization to re-open the T1 held-out labels, to the
reporting shape fixed in §4 and §5 of that plan before any comparator
value existed. The plan was not modified.

**RQ4 — *does longitudinal/episode reasoning improve monitoring quality?* —
was recorded unanswered because the T1 measurement was one-armed.** This is
the second arm.

---

## 1. Provenance and firewall

| | |
|---|---|
| Analysis executed at commit | `f998bf5e0797d076215873aae72300b59f007b6f` |
| Preserved state evidence | `t1_oof_state_evidence.npz` |
| Digest, verified before any row was read | `72f13a8b29eafdd99801bb64dbf8b61f19717f3d7af777d74f21c9709dd28232` |
| Rows in the consumed trace | 492,904 |
| State machine invoked | `false` |
| Run directory created or written | `false` |
| Threshold generated, swept or altered | `false` |
| Model refitted or re-scored | `false` |
| TEST accessed | `false` |

Labels were opened one fold at a time through the §16 authority, under the
selection already promoted for that fold, and were used only to score
states and flags that were computed before any label was read.

---

## 2. Primary result — plan §4.1

Subject-macro mean `episode_f1`, **Arm T1 − Arm W**. Positive favours the
episode state machine.

| | |
|---|---|
| Arm T1 subject-macro `episode_f1` | **0.2524** |
| Arm W subject-macro `episode_f1` | **0.0603** |
| **Difference, Arm T1 − Arm W** | **0.1921** |
| **95% paired subject-bootstrap interval** | **[0.0505, 0.3455]** |
| Successful replicates | 1,000 |
| Undefined replicates | 0 |
| Seed | 2,026 |

### 2.1 Arm T1 reproduces its published value

Arm T1's subject-macro mean is 0.2524, against the
0.2524 published in `T1_DESCRIPTIVE_REPORT_V1.md`.
Plan §4.1 made this a stopping condition: had it not reproduced, the
comparator would be scoring different rows and the analysis would have
stopped rather than reported a second number.

### 2.2 Claim scope

The interval describes **between-subject variation in the paired contrast,
conditional on the fitted upstream models and frozen thresholds.** It is
not a confidence interval for a population parameter and it is not a
hypothesis test. **No p-value and no significance language appears
anywhere.** It is also an *unconditional* resample: no selection event is
conditioned on, because no selection was made here.

Twelve subjects. The interval is coarse by construction and its tails are
governed by a handful of subjects, exactly as plan §4.2 registered before
execution.

---

## 3. Per-subject evidence — plan §4.3

Reported separately and never aggregated into §2. Plan §5 registered that
**the per-subject table is the only thing that distinguishes genuine
equivalence from two real effects cancelling**, which is why it is here.

| Fold | Subject | Ref. ep. | T1 runs | T1 matched | T1 `episode_f1` | W runs | W matched | W `episode_f1` |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `ltstdb:s2004` | 38 | 10 | 9 | 0.3750 | 89 | 12 | 0.1890 |
| 1 | `ltstdb:s2005` | 0 | 7 | 0 | 0.0000 | 363 | 0 | 0.0000 |
| 2 | `ltstdb:s2019` | 6 | 0 | 0 | 0.0000 | 0 | 0 | 0.0000 |
| 3 | `ltstdb:s2020` | 0 | 8 | 0 | 0.0000 | 395 | 0 | 0.0000 |
| 4 | `ltstdb:s2023` | 0 | 1 | 0 | 0.0000 | 120 | 0 | 0.0000 |
| 5 | `ltstdb:s2031` | 18 | 11 | 9 | 0.6207 | 120 | 4 | 0.0580 |
| 6 | `ltstdb:s2057` | 5 | 5 | 4 | 0.8000 | 100 | 5 | 0.0952 |
| 7 | `ltstdb:s2058` | 3 | 0 | 0 | 0.0000 | 0 | 0 | 0.0000 |
| 8 | `ltstdb:s2059` | 47 | 0 | 0 | 0.0000 | 1 | 1 | 0.0417 |
| 9 | `ltstdb:s3068` | 35 | 9 | 9 | 0.4091 | 115 | 10 | 0.1333 |
| 10 | `ltstdb:s3072` | 1 | 1 | 0 | 0.0000 | 1 | 0 | 0.0000 |
| 11 | `ltstdb:s3073` | 10 | 7 | 7 | 0.8235 | 58 | 7 | 0.2059 |

### 3.1 Dominance — one registered limb holds, the other does not

Plan §5 asserted that Arm W *"must produce at least as many alert rows as
Arm T1 ... and therefore weakly more predicted runs."* Both limbs are
checked here. **The run limb holds. The alert-row limb is false.**

| Fold | Subject | T1 runs | W runs | W ≥ T1 runs | T1 alert rows | W alert rows | W ≥ T1 rows |
|---|---|---:|---:|---|---:|---:|---|
| 0 | `ltstdb:s2004` | 10 | 89 | `true` | 2,143 | 520 | `false` |
| 1 | `ltstdb:s2005` | 7 | 363 | `true` | 7,103 | 2,317 | `false` |
| 2 | `ltstdb:s2019` | 0 | 0 | `true` | 0 | 0 | `true` |
| 3 | `ltstdb:s2020` | 8 | 395 | `true` | 4,926 | 1,165 | `false` |
| 4 | `ltstdb:s2023` | 1 | 120 | `true` | 904 | 410 | `false` |
| 5 | `ltstdb:s2031` | 11 | 120 | `true` | 3,463 | 139 | `false` |
| 6 | `ltstdb:s2057` | 5 | 100 | `true` | 1,701 | 209 | `false` |
| 7 | `ltstdb:s2058` | 0 | 0 | `true` | 0 | 0 | `true` |
| 8 | `ltstdb:s2059` | 0 | 1 | `true` | 0 | 1 | `true` |
| 9 | `ltstdb:s3068` | 9 | 115 | `true` | 4,029 | 541 | `false` |
| 10 | `ltstdb:s3072` | 1 | 1 | `true` | 17 | 4 | `false` |
| 11 | `ltstdb:s3073` | 7 | 58 | `true` | 2,181 | 712 | `false` |

Run dominance holds for every fold: `true`. Alert-row dominance: `false`.

**Why the alert-row limb was wrong.** Once Arm T1 enters `EVENT` it
*stays* there until a release condition fires, so it marks rows on which
the event condition does **not** hold. Arm W marks only rows where the
condition holds. The state machine therefore produces **more alert rows in
fewer, longer runs**, and the memoryless rule produces fewer rows in many
short ones. The plan reasoned about confirmation and overlooked hysteresis.

The predictions in §4 rest on the **run** limb, which holds, so they are
still testable. The error is recorded rather than quietly dropped.

---

## 4. Registered predictions — plan §5

Recorded before any comparator value existed. Reported as written.

| Group | Subjects | Registered prediction |
|---|---|---|
| **A — episode-free** | `ltstdb:s2005`, `ltstdb:s2020`, `ltstdb:s2023` | worse or unchanged at zero |
| **B — missed** | `ltstdb:s2019`, `ltstdb:s2058`, `ltstdb:s2059`, `ltstdb:s3072` | may improve |

| Group | Subject | Ref. ep. | Arm T1 `episode_f1` | Arm W `episode_f1` | Direction |
|---|---|---:|---:|---:|---|
| A | `ltstdb:s2005` | 0 | 0.0000 | 0.0000 | equal |
| A | `ltstdb:s2020` | 0 | 0.0000 | 0.0000 | equal |
| A | `ltstdb:s2023` | 0 | 0.0000 | 0.0000 | equal |
| B | `ltstdb:s2019` | 6 | 0.0000 | 0.0000 | equal |
| B | `ltstdb:s2058` | 3 | 0.0000 | 0.0000 | equal |
| B | `ltstdb:s2059` | 47 | 0.0000 | 0.0417 | W higher |
| B | `ltstdb:s3072` | 1 | 0.0000 | 0.0000 | equal |

### 4.1 The aggregate prediction was wrong

**Plan §5 registered that a near-zero difference was the expected outcome,
and that it would be uninformative rather than reassuring.** The observed
difference is 0.1921 with a 95% paired interval
of [0.0505, 0.3455], which
**excludes zero**. The registered expectation is refuted, and plan §5
binds this report to say so rather than reconcile it.

**Why it was wrong.** The §5 reasoning considered only the seven
zero-scoring subjects, whose two failure modes do push in opposite
directions — and among them the prediction held: Group A is unchanged at
zero, and one Group B subject improved. But it never considered the five
subjects that actually score. For those, Arm W's flood of predicted runs
inflates the `episode_f1` denominator `predicted + reference` without
matching proportionally more episodes, and the score collapses. The
aggregate is driven by the subjects the prediction ignored.

That is a defect in the pre-registered reasoning, not in the measurement.
It is recorded here because a prediction that is only checked when it
succeeds is not a prediction.

---

## 5. The operating-point asymmetry — the limitation that bounds this result

**Both arms run at thresholds that were selected with the state machine in
the loop.** The promoted per-fold policy id is
`qw0.9_qe0.99_FAST`: it binds the quantile levels
`q_watch = 0.9` and `q_event = 0.99` **together with** the `FAST`
persistence profile, whose `event_confirm_windows = 2` is a state-machine
parameter. The operating point and the confirmation requirement were
chosen jointly.

Arm W is therefore evaluated at an operating point tuned for a rule it
does not implement. A memoryless rule at a `q_event` of 0.99 fires on
roughly the top percentile of rows with nothing to suppress isolated
firings, which is exactly the flood of short runs observed in §3.
**A memoryless rule given its own operating point would very likely score
better than Arm W does here.**

This is not a defect that can be repaired inside this analysis. Plan §7
excludes any threshold sweep for either arm, correctly — sweeping would be
threshold generation, and a comparator handed its own tuned operating
point while the incumbent keeps its frozen one would be uninterpretable in
the other direction. Both framings have a thumb on the scale; this one's
thumb is named.

**What the result therefore supports:** at the operating point this
programme actually selected and froze, the episode state machine agrees
with reference episodes substantially better than the memoryless rule does
at that same point.

**What it does not support:** that episode reasoning beats window-level
alerting *in general*, or that a well-tuned memoryless alerting rule would
lose. Neither claim is testable from this evidence, and the second would
need a threshold search nobody has authorized.

Plan §9 registered the mirror-image risk — that a null result would be
misread as *"the state machine is useless"*. The non-null result carries
the same hazard facing the other way, and it is named here for the same
reason.

---

## 5. What this does and does not answer

**Answers.** Whether the T1 episode state machine changes episode-level
agreement relative to a memoryless window rule, on identical rows, under
identical frozen thresholds, with every upstream component shared.

**Does not answer.** Whether the *T2 S4D temporal score* contributes
anything: `s4d_temporal_evidence_s_t` is an input to **both** arms, so this
ablation holds it fixed. That is a separate missing arm and a separate
experiment, and it would require re-scoring rather than a derived analysis.

**Also does not evaluate** the encoder, physiology fusion, memory or
calibration — each is common to both arms by construction — nor TEST
performance, generalisation beyond LTSTDB, clinical utility, or deployment
latency.

**Neither arm is characterised as better or worse in monitoring terms.**
Ranking them needs an alerting-cost model this programme does not have.
The numbers are reported and left unranked.
