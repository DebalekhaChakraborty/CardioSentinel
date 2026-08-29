# CardioSentinel — handoff to session "ECG 16"

Paste this whole file as the first message of the new chat, or say:
"Read /home/AI_POC/CARDIOSENTINEL_HANDOFF_ECG16.md and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use here) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/…-ECG-Signal` (renamed `CardioSentinel-AI`) |

`tactics` holds the frozen 335-package set,
`installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`,
Python `3.12.6`. **Verify with `neural.provenance.dependency_environment()`, not
a pip-freeze hash.** Never install, upgrade or downgrade anything in it.

**Frozen T1 five** — run from `src/cardiosentinel/neural/`, bare filenames, in
this order, `sha256sum` then `md5sum` → `4107286307d147d542ff15e916225315`.

```
t1_protocol.py  t1_execution_spec.py  t1_evidence_store.py
t1_development_run.py  t1_persistence.py
```

**Shell state:** the Bash working directory silently resets. Always `cd`
explicitly. Never `git add -A` anywhere near `/home/AI_POC`.

The remote prints "This repository moved" on every push. Noise.

---

## 1. THE HEADLINE — the project is no longer an ECG model

ECG 15 turned a frozen research pipeline into a working intelligent physical
system. **No experiment was run, no budget opened, no artifact touched.**

```
master        bd361f73a7797819799f567566ba785fe81c0cc7   (merge of #93)
open PRs      #94 only — CI green, awaiting the human's merge
tags          research-freeze-v1.0 · ips-agentic-runtime-v1.0
working tree  clean
tests         3,286 collected
```

The system now senses, decides, explains, and refuses claims its evidence does
not support:

```
ECG replay -> edge runtime -> AlertEvent -> EvidenceGraph
                                              |
              +-------------------------------+------------------+
              |                 |                  |             |
        Evidence Agent   Explanation Agent   Research Asst.  Architecture Agent
              |                 |                  |             |
              +-------------------------------+------------------+
                                              |
                                        Claim guard
                                              |
                                    Demonstration console
```

### What merged in ECG 15

| PR | Subject |
|---|---|
| #82 | Edge representation bridge, proven against the frozen corpus to 6 ULP |
| #83 | Streaming inference session — ECG chunk to alert at ~61× real time |
| #84 | Evidence Agent, and Appendix A as executable code |
| #85 | Evidence graph — provenance traversed, closed vocabularies |
| #86 | Patient Explanation Agent, guarded generation, deterministic fallback |
| #87 | Evidence-Grounded Research Assistant, curated objects, no doc access |
| #88 | Handbook **v1.4** — §52–§56, the IPS architecture and claim governance |
| #89 | Documentation alignment; fixed an RQ5 self-contradiction in v1.4 |
| #90 | Reproducibility: a **committed 1.63 MiB demo bundle** |
| #91 | Recovered usability tests that lost #90's merge race |
| #92 | Architecture Selection Intelligence Agent — lifecycle, not recommendation |
| #93 | IPS demonstration console, terminal, zero new dependency |
| #94 | **OPEN** — Evidence-Constrained Explanation Evaluation framework |

---

## 2. Run it in three commands

The demo bundle is **committed**, so this works from a clone plus one PhysioNet
record (`reproducibility/DATA_ACCESS.md`).

```bash
cardiosentinel edge console s20201 --seconds 2400 \
  --run-root reproducibility/demo_bundle/runs \
  --feature-root reproducibility/demo_bundle/features

cardiosentinel agent research "Why was the selective router rejected?"
cardiosentinel agent architecture "Why was S4D selected?"
```

Expected, and contracted by `docs/DEMO_SCENARIO.md`: 1 alert at `00:17:05`,
640 s, 129 windows, peak p_t `0.545613`, gates `G1 PASS G2 PASS G3 PASS
G4 BLOCK G5 BLOCK G6 PASS`, `0/1079` memory updates admitted.

**`0` admitted is correct.** The contamination gate only admits windows that
look normal and sit outside a 60 s refractory.

---

## 3. The one open PR — decide this first

**#94** — Evidence-Constrained Explanation Evaluation framework. CI green at
`95ccc351fde24bcfabe4dbd4658405dfc64ced3a`.

Ships the deterministic arm measured (fidelity 1.000, 0 violations,
completeness 1.000) and the generative arm **unexercised**, because no API
credentials exist here. The table prints `NOT EXERCISED` in the provider row
rather than hiding it in a footnote. The harness is validated against
deliberately bad stub providers.

---

## 4. Consumed vs available — unchanged since `research-freeze-v1.0`

| One-shot budget | State |
|---|---|
| **B4 / neural sealed test** | **AVAILABLE — the last one.** Zero `TEST_ATTEMPT.json` in the tree |
| Everything else (14 budgets) | **CONSUMED.** Handbook §51 is the ledger |

**Do not open the B4 sealed test.** §43.1 argues it on evidence now, not
caution: the headline T2 contrast spans zero and no cohort exists to corroborate
a test number. The paper is stronger without spending it.

**Nothing in #82–#94 consumed a budget.** Handbook §56 states that explicitly.

---

## 5. Open items for ECG 16, in priority order

1. **Merge #94** if the human approves.
2. **Paper package — `PAPER_OUTLINE_V2.md`.** V1 was written at #81, before the
   runtime and the whole agentic layer. Its §2 Related Work and §9 Discussion
   outlines are sound; the skeleton does not know about §52–§56 or the five
   claim-boundary findings. **Supersede, do not edit** — V1 carries the `_V1`
   convention.
3. **§9 needs a new subsection: the five claim-boundary findings** (see §7).
4. **Related Work still requires an actual literature search.** The outline says
   the gap statement must be written *after* the search, not to fit the
   contribution.
5. **Deferred deliberately:** Edge Benchmark Intelligence Agent. The project
   identity moved; it can only report measurements and must refuse the
   readiness verdict (Appendix A claim 5). Revisit only with real hardware.
6. **Not recommended:** any new ML experiment. The remaining gap is the
   manuscript, not model capability.

---

## 6. Standing constraints — verbatim, still in force

- DO NOT: execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read/open/
  hash a B4 test cache or waveform; inspect B4 test labels; calculate B4 test
  metrics; inspect test predictions.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.**
- **No M2 / U1 / T2 rerun. No T1 fold retry. No second continuation.**
  `T1_CONTINUATION_AUTHORIZED` and `T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED`
  are `True` on disk and are **spent tokens, not live permissions**. The re-run
  guard is the persistence claim, not the flag.
- Consumed attempt and continuation directories are **immutable**.
- Never install/upgrade/downgrade packages, especially in `tactics`.
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- Keep scratch files **outside the repo**.
- Do not change code in response to scientific results.
- Patient identity selects a state namespace and a calibrator; **never** a
  predictive feature.
- Labels never determine memory-stream membership, ordering, or update
  eligibility.
- Do not access sealed TEST.

---

## 7. Hard-won lessons from ECG 15

- **`gh pr view` reports a stale head, and it cost a merge.** #90 merged three
  minutes before its usability-test commit landed; the commit was orphaned and
  the API kept reporting the old head. **Pinned-SHA CI checks do not protect
  against this** — they prove *a* SHA passed, not that the SHA you pushed is on
  the branch. **Before calling a PR ready, verify with
  `git ls-remote origin refs/heads/<branch>` against the pushed SHA.**
- **The claim guard has now caught five components, including itself.** Its own
  disclaimer (#84), the explanation template's closing sentence (#86), the
  research objects' forbidden lists (#87), the console's **wrapped** disclaimer
  (#93), and #94's reporting rules. The fourth is the instructive one: the guard
  accepted unwrapped prose and rejected the *identical wrapped* prose — its
  exemption was defeated by **presentation**. Fixed by making
  `strip_approved_disclaimers` whitespace-insensitive.
- **Never reword around the guard.** Each fix was structural — a registered
  disclaimer, a caller-declared `quoting=`, whitespace normalisation. Rewording
  would teach authors to avoid stating boundaries plainly.
- **Generic keywords collide, twice.** `"selected"` sent a B4 question to T2
  (#87); `"arm"`/`"longitudinal"` made both T2 candidates unreachable (#92).
  Keywords must be discriminative, ties must be **refused**, and #92 added the
  test that asserts no keyword is shared.
- **Write the contract before the implementation.** `DEMO_SCENARIO.md` caught
  two wording divergences within an hour of the console being written.
- **`.gitignore` silently drops staged files.** `*.pt` matched three demo-bundle
  checkpoints; integrity tests passed because the manifest and the missing files
  agreed with each other. **Integrity is not usability** — only execution
  catches that class.
- **Check `ListAgents` and `git worktree list` before starting.** Two peer
  sessions were active during ECG 15.

---

## 8. Facts that are easy to get wrong

- **The IPS layer changed no scientific finding.** §49, §51 and Appendix A are
  identical to v1.3. §56 says so explicitly.
- **A laptop is not edge hardware.** RQ5 is **open**. The permitted phrase is
  *"laptop-based edge simulation using streaming physiological replay"*.
- **Only the twelve validation subjects are replayable.** T1 thresholds are
  leave-one-subject-out; anything else is **refused**, not served another
  subject's thresholds.
- **The demo must use `raw_profile()`.** The frozen corpus is
  `processing_profile: raw`; a band-pass would shift every embedding silently.
- **`s20591` producing zero alerts is a validation signal**, not a failure — it
  reproduces the published result that s2059 has 47 reference episodes and 0
  predicted runs.
- **`s_t` is a bounded sigmoid, never a probability**
  (`score_is_calibrated_probability: false`).
- **RQ4 is "Supported (bounded)", never bare "Supported."**
- **T2's interval includes zero; W1's excludes it.** Different estimands.
- **The claim guard is lexical, not semantic**, and cannot be run as a gate on
  human-authored prose — running it over Handbook §52–§56 reports twelve
  violations, every one a quotation. §53.1 explains this.
- The agents **never** read a `_V1` document at runtime. Curated objects only.
- No generative-model SDK is a project dependency. The environment is frozen.

---

## 9. Open defects — recorded, not resolved

1. **`PAPER_OUTLINE_V1.md` predates the runtime and the agentic layer.**
2. **Handbook §53.2 records four claim-boundary findings; there are five.** The
   fifth (#94's reporting rules) is noted in a parenthetical, not the table.
3. **The S3 evidence mirror is "not verified as of 2026-08-23"** — the AWS
   session expired. `CHECKSUM_MANIFEST.md` correctly scopes it out; nothing
   depends on it. Neither verified nor lost.
4. **The generative explanation path has never run against a real model.**
5. `scripts/provenance/` is ruff-excluded, so lint errors there are invisible to
   CI. Passing explicit paths to ruff bypasses the exclusion and reports ~116.

---

**The danger has shifted again.** ECG 11 was over-engineering. ECG 12 haste.
ECG 13 premature interpretation. ECG 14 merge-race and stale state. **ECG 15 was
the codebase outrunning its documentation** — for a day, `ARCHITECTURE.md` said
the edge layer did not exist while it was running at 61× real time.

What is dangerous now is **stopping short of the manuscript**. The system is
complete and the paper is not. Every remaining item in §5 is writing, not
building, and the temptation will be to build one more agent instead.
