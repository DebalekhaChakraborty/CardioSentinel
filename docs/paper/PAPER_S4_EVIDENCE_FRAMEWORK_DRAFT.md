# §4 — Evidence framework, and §4.6 — The claim boundary as executable code

> **Draft prose for the manuscript.** Not a frozen record: no `_V1`, no digest.
> Sources: `PAPER_OUTLINE_V2.md` §4 and §4.6; handbook §41–§47, §43.2, §53;
> `src/cardiosentinel/agents/claims.py`; `src/cardiosentinel/neural/t1_protocol.py`;
> `docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`.
>
> Written **from code**, with file and symbol references, per the outline's
> instruction. Every count below was read from the source at draft time, not
> recalled.
>
> **What this draft must resist, stated first because it is the risk:** §4 and
> §4.6 are the most flattering material in the paper and they are about
> machinery, not results. **Every claim here is a claim about process. They
> license nothing in §7.**

---

## 4. Evidence framework

A monitoring system that learns from patients is easy to evaluate badly. The
usual failure is not a wrong number; it is a number whose provenance nobody can
reconstruct, produced by a pipeline that could have seen what it should not
have, reported after the fact by an author who already knew what the result was.

We built CardioSentinel so that each of those failures is prevented by
something that runs, rather than by something a reader is asked to trust. This
section describes that machinery. It is the paper's contribution.

### 4.1 Leakage controls as executable constraints

The episode state machine may read exactly **nine** row inputs. The list is a
frozen tuple, `T1_ALLOWED_ROW_INPUTS` in `neural/t1_protocol.py`, and a
companion tuple `T1_FORBIDDEN_TRANSITION_INPUTS` names **fifteen** inputs a
transition may never touch. A name outside the allow list raises before any
value is read.

The interesting half is not the deny list. It is that **`stable_id` is *in* the
allow list, and the transition never reads it.**

Both halves have to be stated together or the design is misread. `stable_id` is
admitted because the row must be identifiable — evidence has to be traceable to
a window, and an artifact that cannot name its rows cannot be audited. It is
never consulted in a transition because identity must not influence a decision.
A deny list alone would have forced identity out of the record entirely and
made the provenance claim unverifiable; an allow list alone would have said
nothing about use. **The constraint is that the identifier is present and
unused, and only code can carry that distinction** — no prose convention
survives a refactor.

### 4.2 One-shot access semantics

Several evaluations in this programme could be performed exactly once. A
held-out partition scored twice is no longer held out, and no amount of
reporting discipline repairs it afterwards.

We treat such an access as a **budget**. **All fifteen budgets in this programme
are spent.** The fifteenth — the neural sealed test — was consumed on
2026-08-25.

A spent budget leaves an `*_AUTHORIZED` flag sitting `True` on disk, and the
temptation is to read that flag as a live permission. It is not: **it is a
receipt for an access already taken.** The persistence claim is therefore not
carried by the flag but by the **re-run guard** — the code path that refuses a
second execution against a consumed record, and that would refuse it even if
every flag were flipped by hand.

**How the fifteenth budget was consumed is this section's best material, and it
is not a success story.** The authorization was signed against a *named
architecture*. The evaluator that ran was bound to an architecture the selection
protocol had **rejected**. The mismatch was caught by **reading the entry
point** — not by a test, not by a guard, and not by the authorization document,
which was correct and which the evaluator did not contradict in any way a
machine could see. Handbook §43.2 records it.

We report this because the honest reading of our own framework is that it is
**partial**. It catches what it was built to catch. The thing it did not catch
was found by a person reading code before pressing the button, and a framework
that cannot admit that is advertising rather than describing.

### 4.3 Pre-registration at execution time

Pre-registration in this programme is enforced by **ordering in version
control**, not by intention.

The plan is merged first, as its own change. The generator runs second. The
report is opened third, as a separate change. Because each step is a commit, the
sequence is checkable after the fact by anyone with the repository: a report
whose plan postdates it is visible, and no assertion by an author is required.

This is weaker than a public registry and stronger than a claim of good faith.
It cannot stop a plan from being written to fit a result the author already
suspects. It does stop a plan from being *edited* once the result is in — which
is the failure we could actually prevent.

Two amendments in this programme postdate the reads they concern. Both say so in
their own first paragraph.

### 4.4 Negative capability

Most testing establishes what a system does. Some of the claims a monitoring
programme needs are about what a run **did not do**: it did not open the sealed
partition, did not read a label, did not train a model.

Promoted artifacts therefore carry **zero-capability counters** — recorded
counts of operations the run was structurally incapable of performing, asserted
to be zero at promotion time. The measurement that produced our primary episode
result consumed a persisted trace and **ran no model**, and four such counters
attest to it, with the sealed test still unopened at the time it ran.

**Proving absence is a different and stronger claim than testing presence**, and
it is the one an evaluation of a learning system on patient data most needs.
The pattern generalises past this system: the strongest form of the guarantee is
that the capability does not exist on the path, so the counter is zero because
nothing could have incremented it.

### 4.5 Digest-bound provenance

Every promoted artifact is bound by SHA-256 to the run that produced it, the
environment lock it ran under, the generator that wrote it, and the immutable
run directory it lives in. Split assignments carry their own digest — the
prospective three-fold split used in §5 is
`ce037309cc…206c3` — and a run refuses to start if the digest it recomputes
does not match the one it was authorized against.

The value is compositional rather than cryptographic. Any single digest proves
little; the chain proves that a reported number, the artifact behind it, the
code that produced it and the environment it ran in are the same objects a
reader can fetch. When one link was broken in this programme, the break was
visible as a mismatch rather than as a wrong result.

---

## 4.6 The claim boundary as executable code

Appendix A lists **twenty-five** forbidden claims. Through an earlier revision
it was a document a human was expected to remember. **Eighteen of them are now
word-anchored regular expressions** in `agents/claims.py`, and `enforce()`
raises rather than returning prose that breaks one.

```
Evidence -> Context (four closed sections) -> Generator -> Claim guard -> Output
                                                              |
                                                 fails -> deterministic fallback
```

Three properties must be stated together. Any two without the third would
mislead.

**First, it is lexical, not semantic.** It catches *outperforms*,
*deployment-ready*, *early detection*, *generalizes to*, *statistically
significant*, *externally validated*, *false alarms per hour*, *conformal
prediction*. It **cannot** catch a novel sentence that means the same thing in
words it does not hold. **It reduces the rate at which overclaims reach output;
it does not make overclaiming impossible, and no sentence in this paper may
imply otherwise.**

**Second, word anchoring is not optional.** A substring test for *"proved"*
matches *"improved"* and *"Provenance"*. That specific bug has bitten this
repository roughly ten times, which is why every one of the eighteen patterns is
anchored at word boundaries rather than written as a substring.

**Third, it cannot be run as a gate over human-authored prose, and that is not a
defect.** Running `find_violations` across the handbook sections that describe
this architecture reports **twelve violations, every one of them a quotation** —
the document that defines a boundary must state the boundary. The exemption is
therefore a caller-declared `quoting=` argument rather than a global suppression
list, because a document-wide exemption would silence the guard exactly where
prose is most likely to overclaim.

### 4.6.1 The evidence graph is the substrate, and the boundary is structural

Each alert is represented as a graph of **35 nodes and 39 edges**. Node kinds
and edge relations are **closed vocabularies**: adding a relation such as
`"probably_caused"` raises rather than being accepted as a new edge type.

The boundary lives in the graph rather than after it. Each *"does not
establish"* is a `constraint` node joined by a `bounded_by` edge, so a model
reading the graph encounters the limitation **as evidence**, structurally
indistinguishable in kind from the measurement it bounds — not as trailing prose
it may summarise away. The temporal evidence value `s_t` carries
`is_calibrated_probability: false` in its own node, so the corresponding
Appendix A claim cannot be inferred from the substrate even by a generator that
never reads a disclaimer.

### 4.6.2 Grounding by curation, not by retrieval

The research assistant answers from **six curated evidence objects**, verified in
continuous integration against the merged reports. It never reads a `_V1`
document at runtime, never embeds one, never searches, and **refuses** a question
that is uncovered or ambiguous.

The uncertainty-router rejection is the case that shows why. A plausible
free-text summary would say *"utility gain insufficient"*. The frozen record says
something different and more specific: the **calibration-agreement guard
passed**, at `0.006683691656635168` against a frozen tolerance of `0.02`, and
what failed was the **asymmetric-abstention guard** — an escalation ratio of
`6.453604523726777` against a limit of `3.0` fixed in advance.

**Raw document access lets a model paraphrase that badly. Invented placeholders
get it wrong outright.** Curation is the only one of the three that fails
closed: an object that does not exist produces a refusal, not a plausible
sentence.

### 4.6.3 What the guard does not establish

It does not establish that the explanations are **correct**.

They are **grounded**: every value in an explanation traces to a frozen
artifact, and a value with no such trace does not appear. Grounded is a
different and weaker property than clinically meaningful, and the distance
between them is not something this machinery measures. §8 reports a generation
that was fluent, scored **1.000** evidence fidelity with **zero** claim
violations, and was nonetheless **refused at runtime** for asserting a gate
state the evidence contradicted. That case is the clearest available statement
of the limit: the guard bounds what may be *said*, not what is *true*.

---

## Draft notes — not manuscript prose

**Verified at draft time** (2026-08-28), read from source rather than recalled:
`FORBIDDEN_CLAIMS` **18** entries, all with a non-empty anchored pattern;
`APPROVED_DISCLAIMERS` **6**; `T1_ALLOWED_ROW_INPUTS` **9**, containing
`stable_id`; `T1_FORBIDDEN_TRANSITION_INPUTS` **15**; router guard values from
`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` lines 143–155.

**Appendix A holds twenty-five forbidden claims; eighteen are machine-checked.**
The gap between 25 and 18 is real and must not be smoothed over in revision —
seven remain human-enforced.

**The guard fires on this draft, and every hit is a quotation.** Running
`claims.find_violations` over this file reports **8 violations**, and all eight
are the eight forbidden phrases enumerated in §4.6's first property — lines
150–152, the paragraph that lists what the guard catches. No other line in the
draft matches.

This is the §4.6 third-property claim reproducing on the section that states it,
and it is worth keeping as evidence rather than editing away: the handbook
reports **twelve violations, every one a quotation**, over the sections that
describe this architecture; this draft independently produced **eight, every one
a quotation**, over the section that defines the boundary. It is also the
empirical case for the caller-declared `quoting=` argument — a document-wide
exemption would have silenced the guard across the whole draft, including the
parts where it should still bite.

**Open before submission:** file/symbol citations should be rendered in the
paper's citation style; the twelve-violation figure should be re-run against the
final handbook text, since it is a property of that prose and will change if the
prose does.
