# T2 Arm Comparison Analysis Plan — Amendment V1.1

## 0. Nature of this document

**This amendment was written after the measured values were read.** That is
stated first because it is the only fact that determines how everything below
should be weighted.

`docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md`
(`84adf43b885d6dd3ecef3b678d1a2b89fc6e94f48ffdf8d2f0dc2bb0a7eba973`) is **not
edited**. It remains byte-identical to the document that was approved and merged
before the first read, and `docs/T2_ARM_COMPARISON_REPORT_V1.md` continues to
cite that digest. A pre-registration that can be edited after the values are
visible is not a pre-registration, and the audit trail is worth more than the
tidiness of a single file.

**What this amendment does is expand what may be reported. It restricts
nothing, changes no estimand, and authorizes no new computation.**

| | |
|---|---|
| Written | 2026-08-22, **after** the first read |
| Amends | `T2_ARM_COMPARISON_ANALYSIS_PLAN_V1` §3 and §5.3 |
| Changes the primary estimand | **No** |
| Changes the derived analysis | **No** |
| Authorizes a new computation | **No** |
| Authorizes a rerun, refit or threshold change | **No** |
| Opens TEST | **No** |
| Net effect on reporting | **Strictly more is reported** |

---

## 1. The defect this amendment repairs

V1 contained an **unreconciled internal conflict**, and the first execution
resolved it silently. Both halves are on the record:

> **§5.3** — *"Reported per arm, verbatim, with `is_selection_input: false`
> stated alongside. Challenge subsets and cold-start strata are descriptive."*

> **§3** — *"Not allowed: any claim of unbiased absolute S4D performance on this
> validation set."*

Cold-start strata **contain per-arm absolute AUPRC**. So §5.3 required reporting
values that §3 constrained, and V1 never said how to hold both.

The generator resolved it by **dropping the values**: it printed each stratum's
`row_count` and omitted the entire `metrics` block — 17 keys × 3 strata × 2 arms.
The same instinct suppressed both arms' pooled and subject-macro AUPRC entirely.

**Silent omission was the wrong resolution, on two counts.**

1. **It is unregistered selective reporting.** A conflict resolved invisibly at
   execution time is precisely the failure pre-registration exists to prevent.
   The decision was never reviewed because it was never stated.
2. **It removed the scale.** The primary contrast is
   `pooled_auprc_difference = 0.093215`, with a paired interval of
   `[-0.015229, 0.148951]`. Without an absolute anchor a reader cannot tell
   whether that is the gap between 0.10 and 0.007 or between 0.50 and 0.41.
   Those are different scientific situations and the report could not
   distinguish them.

V1 §3's own instruction was never a prohibition on reporting. It reads:

> *"Report the contrast; do not present the selected arm's absolute value **as an
> unbiased estimate**."*

That permits the value with correct framing. The execution was **stricter than
the plan required**, and over-restriction is a deviation from a plan just as
under-restriction is.

---

## 2. Amendment to §5.3 — cold-start strata

Cold-start strata are reported **in full**, both arms, every stratum, including
the `metrics` block.

**Registered wording, to appear with the values:**

> Cold-start strata are reported as descriptive stratification summaries. They
> do not constitute independent performance estimates and are not used to
> support absolute model superiority claims.

No subgroup claim is made. No stratum is compared across arms as a finding. The
strata are not aggregated into, and are not presented as support for, the §2
contrast.

---

## 3. Amendment to §3 — arm-level absolute AUPRC

Both arms' **pooled primary AUPRC** and **subject-macro AUPRC** are reported,
labelled descriptive.

**Registered wording, to appear with the values:**

> Absolute arm-level values are descriptive because the selected arm was chosen
> using the same criterion. They are reported to give the primary contrast a
> scale, not as unbiased estimates of either arm's performance.

The V1 §3 asymmetry is unchanged and still governs interpretation:

| | |
|---|---|
| **The paired contrast is unbiased** | Both arms were evaluated on identical rows under a rule fixed in advance |
| **The selected arm's absolute figure is not** | It was chosen for having the higher value **on this very set**; the bias attaches to the maximum, not to the contrast |

Every prohibited phrasing in V1 §3 remains prohibited. *"S4D achieved superior
AUPRC"* and *"S4D was found to outperform GRU"* are still forbidden, and
reporting the number does not license the sentence.

### 3.1 Scope of what is added

**Added:** pooled primary AUPRC and subject-macro AUPRC, both arms — the two
quantities the two registered differences are computed from.

**Not added:** the remaining pooled metrics (`auroc`, `balanced_accuracy`, `f1`,
`mcc`, `npv`, `ppv`, `sensitivity`, `specificity`) and the remaining
subject-macro metrics. They exist in the artifact and are **not** reported,
because no registered estimand is computed from them and adding them after the
values are visible would be scope creep of exactly the kind §1 objects to.

That boundary is stated here so it is a decision rather than an accident — which
is the whole complaint against the original omission.

---

## 4. What this amendment does not change

- The primary estimand: `selection_decision.pooled_auprc_difference`, verbatim.
- The DERIVED ANALYSIS: same seed 2026, same 1000 replicates, same subject unit,
  same rows, no refit, no threshold change, no reselection. **The bootstrap is
  not re-run with different settings and its result is unchanged.**
- The claim scope, the resolution caveat, and the prohibition on p-values and
  significance language.
- §6 exclusions, §7 calibration wording, §8 validation firewall.
- The sealed-test state. TEST remains unopened.

No number that appeared in the first execution changes. The report gains values;
it revises none.

---

## 5. Provenance

The report records that it was produced under V1 **as amended by this
document**, cites both digests, and states plainly that the amendment postdates
the first read. A reader who wants the un-amended reporting boundary can
reconstruct it exactly: it is this report minus the two blocks named in §2 and
§3.

---

## 6. Standing

This amendment expands reporting on evidence already read. It does not create a
precedent for amending a plan to change an estimand, add a computation, or
select an analysis after seeing results. Any of those would require a new
pre-registration, not an amendment.
