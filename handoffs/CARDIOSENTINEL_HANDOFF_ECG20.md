# CardioSentinel — handoff to session "ECG 20"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG20.md in the repo and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/CardioSentinel` |

`tactics` holds 335 packages, `installed_packages_sha256 = b0fd6eaa…`,
Python 3.12.6. **Verify with `neural.provenance.dependency_environment()`.**
Never install, upgrade or downgrade anything in it — **a single `pip install`
voids that digest and the reproducibility claim it supports.**

**Shell state:** the Bash working directory silently resets. Always `cd`
explicitly. **Never `git add -A`.**

**Three or four sessions share this one checkout, and the user works in it
directly.** HEAD moves under you. Run `git status` immediately before anything
that assumes a branch or a clean tree, and never clean up untracked files you did
not create — the user harvests other sessions' drafts and commits them.

---

## 1. THE HEADLINE — the explanation layer is finished and measured

ECG 19 handed over a repository whose documents were true and whose budgets were
all spent. This session built and exercised the **open-weight explanation layer**.

```
master   6be26f98f7b3ef78479416fc5525666ba2f855e6
open PRs none
tests    3405 collected
env      335 packages, b0fd6eaa…  (unchanged — nothing was installed)
disk     11 GB free   ** see §6 **
```

| PR | What |
|---|---|
| **#121** | `LocalQwenProvider` — Apache-2.0, ungated, opt-in, adds no dependency |
| **#123** | fail-closed identity and cache; the numeric claim guard; categorical alignment |
| **#124** | **Arm B exercised** — the first real-model report, and a correction to a finding of mine |
| **#125** | a false positive that made the deterministic fallback fail its own gate |

**Arm B is exercised. Defect 2 is closed.** `docs/EXPLANATION_EVALUATION_REPORT_V1.md`.

---

## 2. What the Qwen layer actually is

**Four gates, in order, on every generated explanation:**

```
generation -> claims.audit()          lexical, 18 Appendix A patterns
           -> numeric claim guard     number + optional unit vs the evidence
           -> categorical alignment    gate status and lifecycle states
           -> served, or DETERMINISTIC fallback with the reason recorded
```

**Each gate exists because the previous ones passed a real failure.** That
sequence is the finding, and it is §5.6 material.

| | |
|---|---|
| Models run | `Qwen3-1.7B` @ `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` · `Qwen3-4B-Instruct-2507` @ `cdbee75f17c01a7cc42f958dc650907174af0554` |
| Weights | `HF_HOME=/home/debalekha_chakraborty/.cache/hf-bench`, **outside every repo** |
| Enable | `CARDIOSENTINEL_LLM_PROVIDER=local` + `_MODEL` + `_REVISION` (a full 40-char SHA; anything shorter is refused) |
| Result | 1.7B **refused** — asserted `G1`–`G6` passed while G4, G5 were blocked. 4B **served** — stated it correctly |

**Two models, one context. That is not a scaling law** and the report does not
offer it as one.

---

## 3. Four things about this layer that are easy to get wrong

- **The harness does not run the gates.** `evaluate_arms` calls
  `provider.generate()` directly. Its table measures **raw model output**, not
  what a user receives. Correct for an evaluation — gating first would only ever
  measure the template — but reading that table as "what ships" is wrong.
- **The registered metric and the governance guard are separate on purpose.**
  `evidence_fidelity` extracts `\d+\.\d{2,}` and is registered in
  `EXPLANATION_EVALUATION_PROTOCOL.md` §3.1. **Do not widen it to make a gate
  work.** The guard is allowed to be stricter; the metric is not allowed to move.
- **Qwen3 is a hybrid reasoning model.** Without `enable_thinking=False` it emits
  `<think>…</think>`, and a truncated trace scored fidelity 1.000, 0 violations,
  and would have been shown to a user. `_strip_reasoning` returns empty on an
  unclosed block so truncation falls back.
- **Lifecycle matching is case-SENSITIVE, deliberately.** `NORMAL` is a state and
  *normal* is an adjective, and `safety.reasons` says *"did not look normal
  enough to learn from"*. Case-insensitive matching made the **deterministic
  renderer fail its own gate**. Do not "fix" this back.

---

## 4. Open items for ECG 20, in priority order

1. **§2 Related Work, and the literature search it depends on.** Top of the list
   for four sessions. `PAPER_OUTLINE_V2.md` §2 says the gap statement must be
   written **after** the search, not to fit the contribution, and §2.5 —
   grounded generation and guardrails — has no source in this repository at all.
   **A fabricated citation is the same class of error the whole apparatus exists
   to prevent.**
2. **Draft §5.6 and §9.5.** They have more material than they did a day ago —
   see §5 below. §5.6 is short and is the best evidence in the paper that the
   guards are load-bearing.
3. **Not recommended: a third model, more contexts, or a fifth gate.** See §7.

---

## 5. What this session added to the manuscript, and where

**§5.6 — the boundaries the guards caught.** It was five findings; the
explanation layer adds four more, each found by a failure the previous gates
passed:

| # | Found by | Passed by |
|---|---|---|
| 6 | a truncated `<think>` trace scoring as a valid explanation | fidelity, claim guard, completeness |
| 7 | `54.6%` — a probability restated as a percentage | claim guard, and the registered metric, which cannot see one decimal place |
| 8 | `"passed … G1 through G6"` while G4 and G5 were blocked | claim guard, numeric guard, fidelity, completeness |
| 9 | the categorical validator flagging the word *normal* | **its own regression test**, whose fixture licensed `NORMAL` |

**§9.5 — the pattern, and it is the most repeatable finding of the programme.**
Six times in one session a check passed or failed **for a reason unrelated to
what it claimed to verify**: a stale generator digest nothing asserted; a
reachability test using `cat-file`, which finds objects kept alive by
`refs/original`; a pin scan that read only markdown while `grep -r` silently
skipped the gitignored evidence tree; a package-count assertion that tested
which host it ran on; a provider test that shadowed the libraries it meant to
exercise; and a fixture that certified a validator bug as correct.

**Every instance is documented in-repo**, not in a chat log.

---

## 6. Standing constraints — verbatim, still in force

- **All fifteen one-shot budgets are spent.** `TEST_ATTEMPT.json` **now exists**
  and that is correct. Consumed attempt directories and the four sealed-test
  artifacts are **immutable**. Every `*_AUTHORIZED` flag on disk is a spent
  token, not a live permission.
- **NO AUTOMATIC RETRY. No M2 / U1 / T2 rerun. No T1 fold retry.**
- Never install/upgrade/downgrade packages, especially in `tactics`.
- Never add `--force` / `--retry` / `--reset` / `--overwrite` / `--fresh-seed`.
- Do not change code in response to scientific results.
- Patient identity selects a namespace and a calibrator; **never** a feature.
- **Disk is at 11 GB free.** The two Qwen snapshots are 12 GB in
  `~/.cache/hf-bench`. They are outside every repo and safe to delete; the
  evidence trees on the same filesystem are not.

---

## 7. The danger this handoff names

**The governance layer generates its own work, and every piece of it is
defensible.**

Watch the shape of this session. Arm B found a categorical failure, which
justified a fourth gate. The fourth gate had a bug, which justified a fix. The
fix revealed that the failure is model-dependent, which invites a third model.
A third model would find something, which would justify a fifth gate.

**That loop is real, productive, and infinite.** Each step was correct. Each step
was measurable. Each step produced something true that was not there before. And
none of it is §2.

ECG 16 was warned against building one more agent and built none, then wrote 569
lines of outline instead. ECG 18 was handed one job, did it, and fixed five more
real things. ECG 19 named that pattern and it recurred here in a new costume.

**There is now very little in this repository that is incorrect, and still no
manuscript.** The next session's honest test is whether a file exists at the end
of it that a stranger could read — not whether one more true thing was recorded.
