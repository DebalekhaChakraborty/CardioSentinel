# CardioSentinel — handoff to session "ECG 18"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG18.md in the repo and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use here) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/CardioSentinel` |
| Master at handoff | `61d9009`, clean, 0 open PRs |

Python `3.12.6`, torch `2.13.0+cpu`, numpy `2.3.2`. Never install, upgrade or
downgrade anything in `tactics`.

**Shell state:** the Bash working directory silently resets. Always `cd`
explicitly. Never `git add -A` anywhere near `/home/AI_POC`.

**You share the checkout.** A second Claude session and the user both work in
this directory. Run `git status` before any command that assumes a state, stage
explicit paths only, and check `git worktree list` — parallel worktrees were
used and removed in ECG 17; do not recreate them without saying so.

---

## 1. THE HEADLINE — the sealed test is CONSUMED

**The B4/neural one-shot budget was spent on 2026-08-25 at 00:17:57Z and
completed at 00:43:22Z.** It was the last unspent budget in the programme.
There are now none.

Every document that says the sealed test is *unopened*, *unspent*, or *the last
irreversible budget* is **now false**. That is the single largest job waiting
for you — see §4.

```
attempt_status           COMPLETE
attempt_sequence         1
repeat_attempt_permitted false
experiment_id            B4B_cnn_transformer_v1
architecture             B4BTransformerCNN
duration                 1524.2 s
scored_row_count         463,035
test_audit_sha256        79447d4da551d88f3c97389953c98e8edd3be2a682930cbcdde25525d7efb905
```

### The registered result, exactly as produced

**Primary — pooled-window AUPRC `0.0935334`.** Positive prevalence `0.0460529`
(20,899 positive / 432,905 negative / 453,804 primary windows / 12 subjects).

| Secondary, pooled | |
|---|---|
| AUROC | 0.7332374 |
| F1 | 0.0687550 |
| Sensitivity | 0.0705775 |
| Specificity | 0.9525716 |
| PPV | 0.0670241 |
| NPV | 0.9550159 |
| Balanced accuracy | 0.5115746 |
| MCC | 0.0225878 |

Confusion at the frozen threshold `0.8329097628593445`:
TP 1,475 · FP 20,532 · FN 19,424 · TN 412,373.

**Subject-macro figures are means over EIGHT of twelve subjects**, not twelve.
Four test subjects are single-class, and `METRICS_PROTOCOL.md` excludes them
from discrimination metrics rather than assigning 0.0 or 1.0.

| | value | contributing |
|---|---|---|
| AUPRC | 0.354901 | **8 / 12** |
| AUROC | 0.780837 | **8 / 12** |
| Balanced accuracy | 0.563647 | **8 / 12** |
| MCC | 0.231071 | **8 / 12** |
| Sensitivity | 0.169043 | **8 / 12** |
| F1 | 0.142821 | 12 / 12 |
| NPV | 0.972640 | 12 / 12 |
| PPV | 0.332849 | 12 / 12 |
| Specificity | 0.947705 | 12 / 12 |

**Never quote a subject-macro number without its denominator.** This is the
§9.2 denominator finding recurring in the final evaluation, and it was
pre-registered precisely because it had already happened once in T2.

**Bootstrap: 1,000 subject replicates, seed 2026, 1000/1000 successful, 0
undefined** for every metric.

| | 95% interval |
|---|---|
| AUPRC | [0.033058, 0.239284] |
| AUROC | [0.653182, 0.836523] |
| Balanced accuracy | [0.481415, 0.650244] |
| F1 | [0.027598, 0.222080] |
| **MCC** | **[-0.033876, 0.221346]** — includes zero |
| NPV | [0.912590, 0.993000] |
| PPV | [0.019556, 0.415725] |
| Sensitivity | [0.029482, 0.334282] |
| Specificity | [0.896129, 0.994691] |

**Challenge strata at the frozen threshold** — registered quantitative
secondary: rate-related FP fraction `0.2292818` (1,162/5,068, 4 subjects);
axis-shift FP fraction `0.0389143` (119/3,058, 8 subjects). **Exploratory,
descriptive, never bootstrapped, never headlined:** conduction-change 8/10
windows, 1 subject.

Score semantics: **uncalibrated sigmoid model score; not calibrated
probability.**

Artifacts: `TEST_ATTEMPT.json`, `TEST_METRICS.json`, `TEST_PREDICTIONS.npz`,
`TEST_AUDIT.json` in
`cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/`.
**They are immutable. Do not regenerate, amend or "fix" any of them.**

---

## 2. How it was authorized — the chain, in order

1. **`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md`** — Route A (EDB
   `overlap_clean` secondary evaluation) **declined** 2026-08-24, in writing,
   with reasons. No EDB data was accessed. §2.4 records what the decline costs:
   no second cohort will corroborate any result, **permanently for this paper**.
2. **`B4_TEST_AUTHORIZATION_V1.md`** — signed by the researcher in their own
   hand. §6.3 waives §2 Related Work with a **binding condition**: §2, when
   written, must not be shaped by the sealed-test result. §6.4 is the
   pre-registered reporting commitment, frozen before access.
3. Execution once, under `B4_PROTOCOL_V1`, through the bound B4-B path.

`B4_TEST_DEFERRAL_DECISION_V1.md` is **superseded** and should be read as
history, not as policy.

---

## 3. The near-miss you must know about

**The sealed evaluator targeted the wrong model, and it was caught with the
authorization already signed.**

`sealed_test.py` binds to `B4_raw_compact_cnn_v1` (B4-A) through module
constants in `experiment.py`. Phase 3B-2 **selected B4-B and rejected B4-A**.
Each file was correct about itself; nothing compared them. Running the obvious
entry point would have spent the budget characterising the rejected
architecture — and would have looked clean doing it, because all three B4 locks
carry `status: locked_for_one_shot_test` with `test: null`, so no downstream
check would have objected.

It was found by reading the entry point before calling it, not by any test.

**What now exists because of it:**

- `neural/b4b_sealed_test.py` — `SelectedArchitectureBinding` makes "the model
  the authorization names" and "the model the evaluator loads" one comparable
  object. `verify_selection_identity` proves selection record, lock, checkpoint
  bytes, threshold receipt and model class describe one model, **before** the
  attempt is claimed. `preflight_audit_schema` proves the audit payload is
  assemblable before any test access. `validate_audit_payload` refuses to write
  an audit missing any field the reporting commitment needs.
- `sealed_test.refuse_rejected_candidate()` — the legacy path now refuses a
  rejected candidate **by name**, and fails closed if the selection record is
  unreadable.
- The failure path catches `BaseException`, not `OSError`: a recording fault
  attaches as a note and **the original exception is re-raised**, never masked.

---

## 4. Open items for ECG 18, in priority order

### 4.1 Make the documents true again — highest priority

These now contradict reality:

| File | claims |
|---|---|
| `docs/CardioSentinel_Research_Execution_Handbook_v1.4.md` | 11 hits — §43 chain state, §51 ledger, §0.x summaries |
| `docs/CURRENT_STATE.md` | 1 — "unopened — the last irreversible budget" |
| `docs/PAPER_OUTLINE_V2.md` | 2 |
| `reproducibility/README.md` | 1 — "No sealed test access" |
| `docs/B4_TEST_DEFERRAL_DECISION_V1.md` | 2 — **frozen; do NOT edit.** Superseded, not wrong-when-written |

§43's table must move B4/neural from **UNOPENED** to **CONSUMED**, and *"TEST is
sealed"* becomes false without qualification rather than half true.

**`git stash list` holds `stash@{0}`** — a `CURRENT_STATE` refresh pinned to
`1018001`, stale even before the run. Regenerate wholesale against current
master rather than popping it.

### 4.2 Paper §7 Results

The outline says §7 is *"unchanged from V1, and that is the point."* **That is
no longer true** — there is now a sealed-test row. Add it with its boundary
inline, per `PAPER_S9_DISCUSSION_SKELETON.md` §9.8: the number goes in §7, one
sentence goes in §9.1, **and no thesis in §9 moves.** A discussion revised in
light of the result is post-hoc reasoning whatever it says.

### 4.3 §2 Related Work

Still unwritten, still blocks §9.3, and now carries the §6.3 condition: it must
not be shaped by the result. The literature search has not started.

### 4.4 Drafts already in the repo, unreviewed

`PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`, `PAPER_S9_DISCUSSION_SKELETON.md`,
`PAPER_S9_DISCUSSION_DRAFT.md` (merged in #105). §9.3 is deliberately stubbed.
§9.7 is a new subsection on the provenance incident, accepted but unwritten.

### 4.5 RQ5 / edge

Still open. A laptop replay is not an edge measurement.

---

## 5. The provenance incident — read before following any commit pin

A history rewrite on 2026-08-24 stripped co-author trailers and changed **268
commit identifiers**. File contents did not change; every tree is identical.
**69 commits cited across 71 tracked files stopped resolving.**

- `COMMIT_PIN_TRANSLATION_V1.md` — 326 exact mappings, both directions,
  derivation stated so a third party can re-derive it.
- `PROVENANCE_INCIDENT_V1.md` — the dated chronology.

**Experiment locks cannot be corrected in place.** `experiment_lock_sha256` is
self-referential — the SHA-256 of the lock with that field removed,
`sort_keys=True`, `separators=(",", ":")`. Editing any field changes the lock's
own digest, and B4-B's is registered in **28 files** including three downstream
protocol documents and five other experiments' locks. Translate; never edit.
`neural.integrity.verify_experiment_lock()` implements the check.

**Do not run `git gc --prune=now`.** `refs/original/*`,
`refs/local-backup/pre-coauthor-rewrite` and
`~/cardiosentinel-recovery/pre-coauthor-rewrite.bundle` hold the pre-rewrite
history.

---

## 6. Standing constraints — amended where the run changed them

- **The sealed test is consumed. There is no second attempt, and no budget
  remains to protect.** What remains to protect is the *record* of it: the four
  artifacts are immutable.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- **Do not change any number, threshold or claim in light of the result.** Not
  a thesis, not a hedge, not an emphasis.
- No M2 / U1 / T2 rerun. No T1 fold retry. No second continuation. The
  `*_AUTHORIZED` flags on disk are spent tokens, not live permissions.
- Consumed attempt and continuation directories are immutable.
- Never install/upgrade/downgrade packages, especially in `tactics`.
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- Keep scratch files **outside the repo**.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; **never** a
  predictive feature.
- Labels never determine memory-stream membership, ordering or update
  eligibility.

---

## 7. Lessons from ECG 17

- **A merge can silently drop a commit.** #108 merged at `fd473bd`, one commit
  before the safety work; master then lacked the audit pre-flight and still had
  `except OSError: pass`. It was caught only because the module on master was
  diffed against the reviewed branch head. **Verify what landed, not that a
  merge happened.**
- **Two files each correct about themselves can disagree.** The evaluator/
  authorization mismatch in §3 is the canonical instance. Nothing compared them
  because nothing was responsible for comparing them.
- **A check can pass for a reason unrelated to what it claims to verify.** Three
  times in one day: `git cat-file -t` counted objects a local backup kept alive;
  a markdown-only scan missed the load-bearing source and lock files; a lock
  digest was reported corrupt because the hashing input was wrong, not the
  value. All three were withdrawn after re-measurement.
- **Git author identity does not distinguish sessions.** Every commit carries
  the user's configured identity. Attribution must come from session records,
  never from the author field.
- **Pin ordering, not just behaviour.** Several tests assert *source order* —
  identity gate before attempt claim, pre-flight before claim — because a
  behavioural test passes whether the gate sits above or below the claim, and
  only one of those refuses before writing a receipt.

---

## 8. Facts that are easy to get wrong

- The selected encoder is **B4-B** `B4B_cnn_transformer_v1` /
  `B4BTransformerCNN`. B4-A `B4_raw_compact_cnn_v1` was **rejected** and is
  retained only as the efficient-CNN reference.
- Subject-macro discrimination metrics on the sealed test are over **8 of 12**
  subjects.
- The threshold `0.8329097628593445` came from **validation**,
  `test_informed: false`, and was never recomputed.
- Invocation paths, if anything is ever re-derived (not re-run):
  `source = cardiosentinel-data/ltstdb/1.0.0` (not `…/ltstdb`),
  `feature_root = cardiosentinel-features/ltstdb-baseline-v1`,
  `run_root = cardiosentinel-runs/phase3b2-architecture-v1`.
- `cardiosentinel-runs/`, `cardiosentinel-features/`, `cardiosentinel-data/`
  are gitignored. The B4-B checkpoint and lock are mirrored in
  `reproducibility/demo_bundle/` and **are** tracked.
- The S3 evidence mirror was verified 2026-08-24: 786 objects, Object Lock
  GOVERNANCE until 2027-08-22. `CHECKSUM_MANIFEST.md` is authoritative;
  `reproducibility/README.md` points at it rather than restating it.

---

## 9. Open defects — recorded, not resolved

- **§2 Related Work does not exist**, and the literature search has not
  started. It blocks §9.3 and carries the §6.3 non-contamination condition.
- **§9.7 accepted but unwritten** — the provenance-incident subsection.
- **RQ5 unanswered.** No edge measurement exists.
- **`stash@{0}` is a stale CURRENT_STATE refresh.** Regenerate, do not pop.
- **The handbook's §43/§51 and every "unopened" claim are now false.** §4.1.
