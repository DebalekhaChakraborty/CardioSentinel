# B4 · E7a Non-Causal Score-Scale Mechanism Probe — Report, V1

Executed under `B4_E7A_SCORE_SCALE_MECHANISM_PLAN_V1.md`, whose §2 interpretation
boundaries govern every sentence below. **Development validation only. No
retraining, no sealed artifact, no threshold optimization, no oracle selected.**

**Headline: the hypothesis is refuted in direction, not merely unsupported.**
Static subject-wise score normalization does not narrow the pooling gap — it
**widens** it, and degrades pooled discrimination substantially. On this cohort
**between-subject score scale carries information; it is not purely nuisance.**

---

## 1. Correctness gate — PASSED exactly

Boundary 3 required that subject-wise monotone transforms leave within-subject
ranking numerically unchanged.

| Arm | max abs Δ per-subject AUROC | max abs Δ per-subject AUPRC |
|---|---|---|
| **P1** (subject z) | **0.00e+00** | **0.00e+00** |
| **P2** (subject ECDF) | **0.00e+00** | **0.00e+00** |

**Exactly zero, not merely within tolerance**, across all 9 contributing
subjects. Subject-macro AUPRC is therefore identical to R0's `0.400636` for both
arms **by construction** — a fact with consequences, see §4.

**The stream-level secondary arms legitimately fail this gate** (`Δ` up to
`7.4e-02` AUROC, `2.9e-01` AUPRC) and that is correct behaviour, not an error:
a per-stream transform is monotone *within a stream*, and nine of twelve
subjects own two or more streams, so subject-level ranking is not preserved. The
registered assertion applies to P1 and P2 only.

---

## 2. Results

**Rows 473,897 · subjects 12 · streams 30 · contributing subjects 9/12.**
Zero-positive subjects: `s2005`, `s2020`, `s2023`. No subject or stream had
`σ = 0`, so no arm needed the flat-sigma fallback.

| Arm | pooled AUPRC | macro AUPRC | gap AUPRC | pooled AUROC | macro AUROC | gap AUROC |
|---|---|---|---|---|---|---|
| **R0** raw | **0.380535** | 0.400636 | **+0.020101** | **0.892762** | 0.841039 | −0.051723 |
| **P1** subject z | 0.304227 | 0.400636 | +0.096410 | 0.824621 | 0.841039 | +0.016419 |
| **P2** subject ECDF | **0.237319** | 0.400636 | **+0.163317** | 0.855715 | 0.841039 | −0.014676 |
| *P1 stream* | 0.333518 | **0.416023** | +0.082506 | 0.820225 | 0.827903 | +0.007678 |
| *P2 stream* | 0.244524 | 0.392025 | +0.147501 | 0.854677 | 0.834444 | −0.020233 |

R0 reproduces E1 exactly (`0.380535` / `0.400636`).

**Dispersion and interleaving.**

| Arm | SD of per-subject median | SD of per-subject IQR | interleaving SD | interleaving range |
|---|---|---|---|---|
| **R0** | 0.01354 | 0.22593 | 0.11085 | 0.3782 |
| **P1** | **0.17328** | **0.58363** | **0.12018** | 0.4149 |
| **P2** | **0.00000** | **0.00000** | **0.00000** | 0.0000 |

**Paired subject bootstrap**, 1,000 replicates, seed 2026:

| Contrast | median | 95% interval | includes zero |
|---|---|---|---|
| P1 − R0 | −0.047224 | [−0.279441, +0.128696] | yes |
| P2 − R0 | −0.114316 | [−0.355172, +0.030896] | yes |

**Both intervals include zero and both are wide** — E6a's ceiling, restated: 12
subjects cannot resolve contrasts of this size. The point estimates are
unambiguously negative; the intervals do not certify them.

---

## 3. Why normalization hurts — the mechanism

**P2 equalises everything and is the worst arm.** It maps every subject onto a
uniform `(0,1)` distribution, achieving **perfect** dispersion equalisation and
**perfect** interleaving — `SD = 0.00000` on every measure. Pooled AUPRC falls
from `0.380535` to `0.237319`. **The most complete removal of between-subject
scale produces the largest loss.**

The mechanism is visible in the per-subject rank positions under R0:

| subject | prevalence | R0 mean global percentile rank |
|---|---|---|
| s2004 | 0.19784 | 0.5741 |
| s3068 | 0.19545 | 0.4979 |
| s2059 | 0.03808 | 0.6609 |
| **s2005** | **0.00000** | **0.6060** |
| **s2020** | **0.00000** | 0.3716 |
| **s2023** | **0.00000** | **0.2827** |

**Three of twelve subjects carry no positive window at all**, and they occupy
~19% of the rows. Under R0 two of the three sit **low** in the global ordering
(`0.372`, `0.283`), so their windows are largely kept out of the global top.

**Per-subject normalization destroys that.** Every subject is forced onto the
same scale, so a zero-positive subject's own highest windows are promoted to the
global top alongside a high-burden subject's true positives. **Normalization
guarantees that roughly a fifth of the top-ranked windows are certainly
negative.** Pooled AUPRC collapses accordingly.

**Note also that the offsets are not simply prevalence.** `s2059` (prevalence
0.038) has the highest mean rank at `0.661`, above both high-burden subjects,
and `s2005` sits at `0.606` with **zero** positives. So the between-subject
level is a mixture of signal and nuisance — **but removing all of it is worse
than keeping all of it.**

**A finding about P1 specifically.** Z-scoring equalises mean and SD by
construction, yet **median dispersion rose from 0.01354 to 0.17328 and IQR
dispersion from 0.22593 to 0.58363.** The score distributions are strongly
skewed, so matching the first two moments actively *mis*-aligns the quantiles.
**Mean/SD standardisation is the wrong tool for this distribution shape**, and
its interleaving got slightly worse too (`0.11085 → 0.12018`).

---

## 4. The result that matters for deployment

**Subject-macro AUPRC is `0.400636` for R0, P1 and P2 — identical to the last
digit.** This is not an empirical finding; it is forced by monotonicity.

**Therefore static subject-wise score normalization cannot improve
single-patient monitoring at all, by construction.** In deployment one patient
is monitored at a time; the relevant statistic is within-subject, and a monotone
per-subject map cannot move it. The only metric it can move is the pooled one —
and it moves it *down*.

**The one arm that moved subject-macro was the stream-level secondary**:
`P1_stream` raised it from `0.400636` to `0.416023`, because normalizing per
`(record, channel)` removes per-lead and per-record offsets *within* a subject,
which is a genuine within-subject transform. **That gain is +0.0154, was not
bootstrapped, rests on 9 subjects, and should be treated as suggestive only** —
E6a's finding applies with full force.

---

## 5. Registered predictions, reported as written

| # | Prediction | Outcome |
|---|---|---|
| 1 | Per-subject AUROC/AUPRC unchanged to `< 1e-9` | **Confirmed** — exactly `0.00e+00` |
| 2 | Location and scale dispersion fall sharply under **both** arms | **REFUTED for P1** — median and IQR dispersion *rose*. Confirmed for P2 |
| 3 | Interleaving dispersion falls under both arms | **REFUTED for P1** (0.11085 → 0.12018). Confirmed for P2 (→ 0) |
| 4 | Pooled AUPRC moves by less than the gap `0.020101` | **REFUTED** — P1 moved −0.076, P2 −0.143 |
| 5 | P2 changes pooled ranking more than P1 | **Confirmed** |

**Prediction 4 was wrong for an instructive reason.** It bounded the *upside* —
closing the gap can recover at most `0.020101` — and silently assumed the
downside was bounded too. **It is not: a transform can destroy arbitrarily much
information.** The registered prediction reasoned about one tail only.

---

## 6. Interpretation boundaries, applied

- **Boundary 1.** These arms are a ceiling for **static, subject-wise score
  normalization only**. They say nothing about M1L/M2-G representation-space
  personalization, and nothing about time-varying score personalization, which
  is a strictly larger class that can reorder within a stream. **Both remain
  entirely open.**
- **Boundary 2.** Development validation's pooling gap is only `+0.020101`.
  **This result cannot refute the post-hoc sealed cross-subject-scale
  hypothesis**, which concerns a partition E7a is forbidden to touch and which
  is permanently consumed. E7a characterises the mechanism on development data
  and nowhere else.
- **Boundary 4.** **Mechanism evidence.** Not development performance, not
  generalization. Nothing here says anything about detection quality.

---

## 7. Decision — and an ambiguity in the registered rule

**The registered rule is ambiguous for this outcome and that is recorded rather
than resolved by preference.** §5 of the plan says *"if P1/P2 materially alter
pooled ranking, stop after reporting and design the causal approximation
separately."* They **did** materially alter it — by `−0.076` and `−0.143` — but
in the **harmful** direction. The rule was written imagining alteration meant
recoverable signal, and it does not cover a destructive result.

**Reading the intent rather than the letter, the correct branch is the second
one: do not implement a score-normalization personalization mechanism.** The
rationale is not that the effect was too small to matter — it is that:

1. The mechanism it presumes — that between-subject scale is nuisance — is
   **contradicted** on this cohort. Removing scale removes signal.
2. Even a perfect version **cannot help single-patient monitoring**, because
   subject-macro is invariant under any monotone per-subject map (§4).

**A causal approximation of P1 or P2 should not be designed.** It would be a
causal approximation of a transform measured to be harmful.

---

## 8. The next mechanistic question

**Not cross-subject scale. Within-subject, cross-stream offset.**

The only arm that moved the deployment-relevant metric was stream-level
normalization (`0.400636 → 0.416023`), which is a *within*-subject transform:
it removes per-lead and per-record offsets that a subject-level transform cannot
see. Nine of twelve validation subjects own two or more streams, and one owns
six.

**The question worth asking next:** *does per-lead / per-record score offset
within a subject degrade within-subject ranking, and is that offset causally
estimable from early stream history?* It is deployment-shaped — M1 already
resets memory at exactly this boundary — it needs no retraining, and unlike E7a
it targets a metric that a monotone per-subject map cannot reach.

**Two prior caveats bind it before it is proposed.** The `+0.0154` that suggests
it is not bootstrapped and rests on 9 subjects; and **boundary 1's other two
open mechanisms — representation-space and time-varying personalization — remain
untested by anything done so far.**
