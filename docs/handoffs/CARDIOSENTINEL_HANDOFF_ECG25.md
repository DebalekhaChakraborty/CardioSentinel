# CardioSentinel — handoff to session "ECG 26"

Paste this whole file as the first message of the new chat, or say:
"Read docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG25.md in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/CardioSentinel` |
| Branch | `chore/post-merge-living-state`, **PR #132 open** |
| GitHub | `DebalekhaChakraborty/CardioSentinel`, `master` at `1bdc1b7` |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **The Bash working directory silently resets** — put
`cd` in the same command as the work. **Never `git add -A`.**

### The one environment trap that will waste your morning

**The directory was renamed** from `Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal`
to `CardioSentinel`, and the frozen venv's editable install still points at the
old name:

```
.../site-packages/__editable__.cardiosentinel-0.1.0.pth
  -> /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal/src
```

Without a symlink at the old path, `import cardiosentinel` fails outright and
**nine governance tests fail as `DID NOT RAISE`** — the sealed-test
claim-exclusivity, source-order and T1 capability-gate proofs, which resolve
their own source through `inspect.getsource`. **They look like disabled safety
guards and are not.**

```bash
ln -s /home/AI_POC/tactics/CardioSentinel \
      /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
```

**Do not repair this with `pip install -e .`** — that risks the 335-package
digest the code itself asserts, to fix a filename. Full write-up: defect 2b in
`docs/control-plane/CURRENT_STATE.md`.

---

## 1. STATE — green, one PR open

```
ruff check .     All checks passed
pytest tests     3578 passed, 1 skipped, 0 failed   (~19 min)
markdown links   174 files, 0 broken
git status       clean apart from this handoff and reproducibility/demo-ui/
```

**PR #132 is open** on `chore/post-merge-living-state`. #128–#131 are merged.

Nothing is half-finished. Start new work freely.

---

## 2. WHAT THIS SESSION DID

**Closed the T1 blocker (PR #129).** Four `src/cardiosentinel/neural/t1_*.py`
files had been repointed at `docs/experiments/t1/` and were failing their
SHA-256 freeze. Reverted them, moved the seven T1 documents back to flat
`docs/`, and recorded *why* in `docs/README.md` and the translation table.
**The seven `docs/T1_*.md` files must stay flat.** 18 E501 errors fixed by
explicit wrapping through an AST parse gate.

**Runtime trust-boundary hardening and the document-hierarchy V2 migration**
(PRs #130, #131, owner-authored) — `paper/`, `handbook/`, `handoffs/` now live
under `docs/`, backed by a coupling inventory, a byte receipt and two test
modules.

**Research-artifact presentation cleanup (PR #131).** The README no longer opens
with *"If you arrived here from the manuscript"* and no longer navigates by
paper section number. Evidence links were re-keyed into a controlled design
lineage. Two substantive corrections went in with it: the sealed-test number now
carries its comparator (**B4-B 0.0935 against B3's 0.1683** on the same held-out
partition — *"the raw-waveform representation did not match handcrafted ST
features"*), and the physical task is stated as the scope document states it.

**Living-state refresh (PR #132, open).** `EVIDENCE_MAP.md` still claimed
*"Fourteen of fifteen budgets are spent. Only the B4 / neural sealed test
remains"* — both halves false since 2026-08-25. Corrected. A speculative W1
half-sentence was removed from the README.

**Evidence mirror verified.** All three S3 prefixes checked by content on
2026-08-29: exact object counts and byte totals, 0 delete markers, 0 overwrites,
both recorded manifest digests matching, **24/24 sampled objects re-hashed**.
`snapshot-2026-08-28-4c59ff1` is no longer attested only by its own upload.
§8.0 carries the dated record; defect 1 has now been opened and closed three
times in one week, and the entry says so.

---

## 3. NEW — the demo dashboard, and what it found

`reproducibility/demo-ui/` is a **presentation layer over the existing runtime.**
It adds no inference, no threshold, no state machine. The browser implements no
second detector.

```bash
# generate (deterministic only)
python reproducibility/demo-ui/export_snapshot.py

# generate, and also exercise the guarded generative path
python reproducibility/demo-ui/export_snapshot.py --with-local-models \
  --hf-cache /home/debalekha_chakraborty/.cache/hf-bench/hub

# serve, from the repository root
python -m http.server 8081 --bind 0.0.0.0
#   -> http://localhost:8081/reproducibility/demo-ui/
```

`demo_snapshot.json` is **derived and gitignored**. The exporter checks the
generated replay against the contracted scenario and **writes nothing on a
mismatch** — record, subject, 479 observations, one alert `EVT-s20201-0000`,
00:17:05→00:27:45, 640 s, 129 windows, peak p_t 0.545613, peak s_t 0.953344,
max d_long 1.411607, opening gate `G1 G2 G3 PASS / G4 G5 BLOCK / G6 PASS`,
0 admitted memory updates.

### The guarded-generation finding reproduced live

`--with-local-models` runs each locally cached model through the **same**
`PatientExplanationAgent` the runtime uses. On 2026-08-30, on this machine:

| model | outcome | |
|---|---|---|
| `Qwen/Qwen3-1.7B` @ `70d244cc` | **REFUSED** → deterministic fallback | *"the range asserts G4, G5 as passed, which the evidence does not record"* · 57.0 s |
| `Qwen/Qwen3-4B-Instruct-2507` @ `cdbee75f` | **SERVED**, 0 violations | 139.2 s |

**That is the recorded failure mode reproducing independently**, not a replay of
the frozen figure. Both revisions match `QWEN_EVALUATION_RUN.md` exactly.

**The runtime does not retain the refused generation** — only the reason it was
refused. The dashboard therefore shows what was *delivered* and why, and never
reconstructs what was rejected. Do not add that reconstruction.

**One context, one run per model. No failure rate and no scaling law is
claimed**, and the UI says so on both surfaces.

---

## 4. TRAPS

1. **Never `ruff format`.** The repo is ruff-*checked*. A format pass reflowed
   128 unrelated files and lengthened frozen constant tables.
2. **Never edit a frozen document's content to fix a path.** **38 documents are
   digest-pinned — and only 29 of those are pinned by code.** The other nine are
   pinned *by other documents*, so **no test fails when one is edited.** Before
   editing any document, hash it and search the whole tree, including
   `cardiosentinel-runs/*.json`, for that digest.
3. **T1 sources are SHA-frozen**, and so are some baseline sources. Check before
   editing anything under `src/cardiosentinel/neural/t1_*`.
4. **A provenance generator is a document's content.** `scripts/provenance/gen_*.py`
   emit path strings *into* reports that must regenerate byte-for-byte. Where a
   constant is both emitted and opened it is split in two — see `AMENDMENT` and
   `AMENDMENT_PATH` in `gen_t2_arm_comparison_report.py`.
5. **The full suite takes ~19 minutes.** Run it in the background; do not poll
   with short sleeps.
6. **`M1_STAGE1_ATTEMPT1_FAILURE.md` records the SHA-256 of the empty string.**
   A naive "is this file's digest quoted anywhere?" check reports a false pin for
   every file it cannot read.
7. **Adding a handoff changes a census.**
   `tests/reproducibility/test_document_hierarchy_v2.py` asserted a fixed count
   of tracked handoffs; it now checks that every *receipt-listed* handoff is
   still tracked, which is what it always meant. The index,
   `docs/handoffs/README.md`, was `content_frozen: Y` and is now
   `LIVE_HANDOFF_INDEX` — see §6. **The handoffs themselves remain frozen.**
8. **Canvas sizing, if you touch the demo UI.** `mkLayer` reads `data-h`, never
   the `height` attribute — it *writes* that attribute as `height × dpr`, so
   reading it back made the ECG canvas double on every rebuild until it filled
   the viewport. CSS `max-height` now caps every canvas as a second line of
   defence.

---

## 5. THE SCIENCE IS UNCHANGED

**All fifteen one-shot budgets are spent.** The B4 neural sealed test, the last
of them, was consumed on 2026-08-25. Nothing further can be measured without a
new human authorization, a re-scoring run, or data this project does not have.

RQ4 **Supported (bounded)** — the parenthesis is part of the claim. RQ3 is a
**negative finding** reported as a result. RQ1, RQ2 (partial), RQ5, RQ6 and RQ7
are open, and every one needs a run.

Nothing in this session recomputed, re-scored or re-selected anything. No frozen
artifact, attempt receipt, threshold or experiment identity was touched.

---

## 6. WHAT IS OPEN

1. **Merge PR #132.** It carries the living-state refresh, the Evidence Map
   correction, the demo dashboard and this handoff.
2. **The symlink in §0 is untracked infrastructure.** A fresh clone or another
   machine will see the nine failing governance tests until it exists. Deciding
   between renaming the directory back and a controlled reinstall is still open.
3. **The demo UI has never been reviewed at 1920×1080 by anyone who could see
   it.** Structure, data binding and HTTP delivery are verified; layout and
   legibility are not. Open it before recording.
4. **`docs/paper/drafts/` is single-copy** — gitignored, not in S3. One disk
   failure loses it.
5. **The evidence mirror will go stale again.** Defect 1 has been opened and
   closed three times in one week; re-verify with a date attached rather than
   inheriting 2026-08-29.
6. ~~**The handoff index cannot name ECG 24 or ECG 25.**~~ **Resolved
   2026-08-30, on the owner's decision.** The V2 receipt had classified
   `docs/handoffs/README.md` as `content_frozen: Y`, role `HISTORICAL_HANDOFF`,
   and a test enforced its byte size — so the index sat claiming *"Latest:
   ECG 23"* while ECG 24 and ECG 25 existed. This session edited it, the test
   caught the edit, and the edit was reverted rather than forced.

   The classification was a **directory-rule artifact**: `_policy()` in
   `scripts/provenance/document_hierarchy_inventory.py` marked everything under
   `handoffs/` historical, and the index was swept in with the sessions it
   indexes — freezing the one file in that tree whose purpose is to change. The
   row is now `content_frozen: N`, role `LIVE_HANDOFF_INDEX`; `_policy()` carries
   the same exception, and it still agrees with all 68 receipt rows. The
   migration-time `byte_size` and `sha256` are left as recorded, because they
   state what the file was when it moved and that remains true. Reasoning is in
   `docs/provenance/DOCUMENT_PATH_TRANSLATION_V2.md`. **The 23 handoffs
   themselves are untouched and still frozen.**
