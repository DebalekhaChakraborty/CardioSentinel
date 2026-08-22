# External Validation Strategy, V1

**This document identifies and audits. It authorizes no acquisition, no
download, no evaluation and no protocol change.** Its purpose is to establish
whether an independent external cohort exists for this system *before* any data
reaches disk, which `CROSS_DATASET_PROVENANCE.md` requires and which is not
recoverable once violated.

**The headline finding is negative and should be read first.** There is no
drop-in independent external cohort for this task in the public record. The
milestone is blocked by data availability, not by effort. §5 says what follows
from that.

---

## 0. Why this precedes the sealed test

`docs/CardioSentinel_Research_Execution_Handbook_v1.2.md` §43 argues that
opening the B4/neural sealed test before external validation *"spends the final
firewall on a result no cohort can corroborate."* The evidence since then
strengthens the argument rather than weakening it:

- **T2** (`T2_ARM_COMPARISON_REPORT_V1.md`) — the selected arm's contrast against
  its comparator has a paired subject-bootstrap interval that **includes zero**.
- **W1** (`W1_WINDOW_COMPARATOR_REPORT_V1.md`) — episode reasoning does beat a
  memoryless rule, but only *at the operating point selected for the state
  machine*, and the report says so.
- **§24** — no research question was affirmatively answered before W1, and W1's
  answer is bounded by an operating-point asymmetry.

Every one of those results lives on **one cohort of 12 validation subjects**. A
sealed-test number would live there too.

---

## 1. What a candidate cohort must satisfy

Derived from the frozen contracts, not negotiable without a protocol version
change.

| Requirement | Value | Source |
|---|---|---|
| Sampling frequency | nominal **250 Hz**, header authoritative | `DATASET_CONTRACT.md` |
| Channels | **2–3** signals | `DATASET_CONTRACT.md` |
| Window / stride | **10 s / 5 s** causal | `evaluation/protocol.py` |
| Sample coordinate | `SAMPLES_PER_SECOND = 250.0` | `t1_continuation_measurement` |
| Recording structure | **long continuous ambulatory streams** | T1 accumulates state over hours; T2 carries state across windows |
| Labels | **ST-episode onset/offset annotations** in a WFDB vocabulary | `t1_protocol.group_reference_episodes` needs episode boundaries, not per-beat classes |
| Feature schema | 146 features → 64 | `t2_protocol.T2_SHARED_SCAFFOLD` |

**The label requirement is the binding one.** This system's endpoint is
episode-level alerting. A cohort with beat labels, rhythm labels, or diagnostic
class labels cannot produce reference episodes, and inventing episodes from
another label type would be a new labelling protocol — which destroys the
independence the cohort was wanted for.

---

## 2. Candidate identification

Enumerated from PhysioNet's own topic indices and release pages, 2026-08-22.
**No data was downloaded.**

### 2.1 The universe is small

PhysioNet's [`st-segment` topic index](https://physionet.org/content/?topic=st-segment)
returns essentially one ambulatory ST-episode database: **Long Term ST Database**
— the training cohort. The [European ST-T Database](https://physionet.org/content/edb/1.0.0/)
is the only other annotated ST-episode resource, and it is already pinned in
`DATASET_CONTRACT.md` and already audited as partially contaminated.

That is the whole realistic universe. It is not an oversight in the search; it
reflects how rare expert episode-level ST annotation is.

### 2.2 The three tiers

| Tier | Cohort | Verdict |
|---|---|---|
| 1 | **EDB `overlap_clean`** (75 records) | available, adapted, audited — but **not independent** and structurally shifted (§3) |
| 2 | **STAFF III** (104 patients) | gold-standard ischemia timing, **incompatible on five axes** (§4) |
| 3 | anything else public | **none identified** |

---

## 3. Tier 1 — EDB, and why it is secondary rather than external

### 3.1 Contamination status: already audited, already enforced

`CROSS_DATASET_PROVENANCE.md` establishes from official LTSTDB headers that ten
LTSTDB recordings are Pisa-collection originals that EDB excerpts, with all ten
pairs verified individually. The conservative exclusion is **fifteen** EDB
records — the ten verified pairs plus same-EDB-subject grouping:

```
e0103 e0104 e0105 e0113 e0123 e0124 e0125 e0126 e0127
e0129 e0133 e0162 e0163 e0603 e0604
```

This is implemented, not merely documented: `evaluation/provenance.py` exposes a
typed registry with the confidence vocabulary `verified` /
`collection-level-risk` / `unknown`, and
`validate_edb_secondary_evaluation_policy` **rejects the `full` cohort** for
secondary evaluation when training includes LTSTDB. Demographic similarity can
never promote a record to `verified`.

**Nothing here needs redoing.** The contamination check the milestone calls for
was already done, correctly, and is enforced in code.

### 3.2 Why it still is not external validation

The provenance document says so itself:

> *Neither cohort may be called fully independent external validation because
> independence of every remaining subject has not been proven.*

The exclusion addresses *known* overlap. It does not establish that the
remaining 75 records are independent of LTSTDB — only that no documented
correspondence links them.

### 3.3 The structural shift nobody has costed — and T2 already measured it

**EDB records are ~2-hour excerpts. LTSTDB records are ~24-hour recordings.**
For a system that carries state across windows, that is not a cosmetic
difference, and this programme has already quantified how much it matters.

From `T2_OUTER_VALIDATION_RESULT.json`, now published in
`T2_ARM_COMPARISON_REPORT_V1.md` §6:

| Cold-start stratum | Rows | Share | AUPRC |
|---|---:|---:|---:|
| `0_5_minutes` | 1,798 | 0.4% | **0.0015** |
| `5_60_minutes` | 19,637 | 4.1% | 0.5440 |
| `over_60_minutes` | 452,462 | **95.5%** | 0.3840 |

**On the validation cohort, 95.5% of rows sit past the first hour**, because the
records are 24 hours long. On 2-hour excerpts roughly half of every record would
fall inside the first hour instead — an order-of-magnitude change in stratum
composition, and the first-five-minutes stratum scores **0.0015**.

This is a structural estimate from record durations, not a measured result on
EDB, and it is stated as such. But it means an EDB evaluation would be scored
largely in the regime where the model is weakest, and a poor number would be
**uninterpretable**: it could not be separated into "does not generalise" versus
"was evaluated mostly during warm-up."

**Any EDB evaluation must therefore be stratified by cold-start bin and
pre-registered as such, or it will produce a number nobody can read.**

---

## 4. Tier 2 — STAFF III, and the five axes it fails

[STAFF III](https://physionet.org/content/staffiii/1.0.0/): 104 patients, 152
coronary occlusions, ischemia induced by prolonged balloon inflation during
PTCA, with all inflation/deflation instants manually annotated.

Its label is the strongest in the field — **ischemia onset is known by
construction**, not by expert ST reading. That is exactly what this system's
labels lack. It is also, on every other axis, the wrong shape:

| Axis | Required | STAFF III | Consequence |
|---|---|---|---|
| Sampling | 250 Hz | **1000 Hz** | 4× decimation — a `SIGNAL_PROCESSING_CONTRACT` change |
| Leads | 2–3 | **standard 12-lead** | lead-selection protocol; the frozen feature schema assumes the LTSTDB montage |
| Duration | ~24 h continuous | **~5 min baseline + ~4 min occlusion + ~5 min recovery** | no long-horizon state; T1 hysteresis and T2 carry are untested at this scale |
| Annotation | ST-episode onset/offset | **balloon inflation/deflation instants only** | a new label-derivation protocol, which is a new labelling decision |
| Mechanism | spontaneous transient ischemia | **induced total occlusion** | a different physiological event |

**What STAFF III could answer, if reframed:** does the detector respond to
*induced* ischemia onset with a known time reference? That is a **mechanism
sensitivity check**, and it would be a genuine contribution. It is **not**
external validation of the ambulatory monitoring task, and presenting it as such
would be a category error.

Each of the five axes is a frozen-contract change. Together they are a new phase,
not a validation run.

---

## 5. What follows

### 5.1 The honest position

**No public cohort supports independent external validation of this system as
specified.** Three routes exist and each costs something real:

| Route | Cost | What it buys |
|---|---|---|
| **A. EDB `overlap_clean`, stratified** | low — adapter exists, audit done, no new contract | a *secondary* cohort result, explicitly not independent, interpretable only if pre-registered with cold-start stratification |
| **B. STAFF III as a mechanism check** | high — five contract changes | a different and defensible claim: response to known ischemia onset |
| **C. New acquisition / clinical partnership** | highest | the only route to genuine independence |
| **D. Report the absence** | none | an honest limitation, and a contribution in an auditable-methodology paper |

### 5.2 Recommendation

**Do A and D. Do not do B yet. Do not open the sealed test.**

Route A is cheap and the machinery already exists, provided it is pre-registered
as a *secondary, stratified* evaluation and never described as external. Route D
costs nothing and is the more valuable of the two for the paper: a documented
audit showing that the field lacks an independent ST-episode cohort is a real
finding about the field, not an excuse about this project.

Route B is a good experiment wearing the wrong label. It should be proposed on
its own terms, as a mechanism check, in its own protocol — not folded into an
external-validation milestone to make the milestone look complete.

### 5.3 What must be true before any acquisition

Binding, from `CROSS_DATASET_PROVENANCE.md`:

1. The provenance audit is completed **from release documentation and headers,
   before waveforms are downloaded.** For EDB this is already done.
2. Any new correspondence enters the typed registry through a reviewed update,
   and changing a frozen evaluation cohort requires a **new benchmark protocol
   version**.
3. Confidence stays `verified` / `collection-level-risk` / `unknown`. Demographic
   similarity never promotes a record.
4. The evaluation is pre-registered before any value is read — the discipline
   T1, T2 and W1 all followed.

### 5.4 Explicitly not decided here

This document does **not** authorize downloading EDB, evaluating on it, changing
any contract, or acquiring STAFF III. §5.2 is a recommendation for a human
decision, and the decision has not been made.
