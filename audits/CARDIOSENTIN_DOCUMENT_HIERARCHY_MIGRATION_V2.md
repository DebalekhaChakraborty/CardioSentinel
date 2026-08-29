# CardioSentinel controlled document-hierarchy migration V2

**Migration date:** 2026-08-29

**Audit closure date:** 2026-08-29

**Starting commit:** `61cc553473180ce68f33bf9c3002addc74b20340`

**Migration commit:** `c837beed9ce560e3283ca4a5b4ab9d2762e96eef`

**PR #131 merge:** `1bdc1b7b3d0182aae87332375c56062d35dcc143`

**Post-merge living-state commit / PR #132 head:**
`c2c306a9c57345e617fb870f5a6091c742f7bc30`

**Audit content commit:** pending closure update

**Scientific interpreter:** `/home/AI_POC/venvs/tactics/bin/python`

## 1. Outcome and boundary

The path-only migration is complete:

```text
paper/     -> docs/paper/
handbook/  -> docs/handbook/
handoffs/  -> docs/handoffs/
```

The three root directories no longer exist. Their tracked contents are now 31,
10 and 23 files respectively. No experiment, rescore, TEST access, checkpoint
change, runtime refactor, metric change, threshold change, manuscript rewrite
or frozen-result amendment was performed.

The seven T1 documents remain flat under `docs/`. The migration did not create
`docs/experiments/t1/` or edit the digest-frozen T1 source files that construct
their paths.

## 2. Complete moved-file inventory

The authoritative per-file inventory is the machine-readable
`docs/provenance/DOCUMENT_HIERARCHY_MIGRATION_V2_RECEIPT.tsv`. Its 68 rows are
incorporated into this audit by reference and record, for every file, the old
path, new path, byte size, SHA-256, protection class and tracked status.

| Tree | Tracked files | Ignored owner drafts at move time | Receipt rows |
|---|---:|---:|---:|
| `paper/ -> docs/paper/` | 31 | 4 | 35 |
| `handbook/ -> docs/handbook/` | 10 | 0 | 10 |
| `handoffs/ -> docs/handoffs/` | 23 | 0 | 23 |
| **Total** | **64** | **4** | **68** |

The four move-time ignored DOCX drafts were copied byte-identically to
`/tmp/cardiosentinel_migration_v2_drafts.r4e5M7/` before the move. That path is
a session-local safety receipt, not a repository dependency. Additional ignored
drafts created later are outside the historical move receipt and do not alter
the 64 tracked Git moves.

Immediately after the three `git mv` operations, the receipt verifier reported:

```text
checked=68 failures=0
```

Six non-frozen files were then changed solely to repair live path references:

- `docs/paper/PAPER_S2_RELATED_WORK_DRAFT.md`
- `docs/paper/PAPER_S9_DISCUSSION_DRAFT.md`
- `docs/paper/TACTICS_SUBMISSION_ASSET_INVENTORY.md`
- `docs/paper/TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md`
- `docs/paper/figures/README.md`
- `docs/paper/figures/make_f3_f4.py`

The final receipt comparison was therefore 6 permitted live-path byte changes,
0 protected-file changes, 0 handbook changes and 0 handoff changes. The move
itself changed zero bytes.

## 3. Coupling and relative-link audit

The pre-move search covered all tracked text, Python and shell source, tests,
configuration, README and control-plane files, path constructors and the
ignored run-artifact tree. The exhaustive occurrence classification is
`docs/provenance/DOCUMENT_PATH_COUPLING_INVENTORY_V2.md`:

- A — live path consumers: updated;
- B — living documentation: updated where current;
- C — historical records: preserved;
- D — digest-frozen sources: preserved;
- E — immutable artifact-recorded paths: none for these three roots; and
- F — natural-language false positives: no action.

The 46 moved Markdown files contained no local Markdown link targets, so moving
them one directory deeper did not require changing a frozen source. The final
repository-wide live-link scan is covered by
`test_all_live_local_markdown_links_resolve`; the closure rerun scanned 175
non-legacy Markdown files and found 0 broken local links. Historical inline path
strings are not links and resolve through the translation records.

## 4. V1 and V2 translation relationship

`docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md` remains byte-identical at:

```text
fb65a3179607b3c7f5481d6a4f174800a744da605330a26aef9f3d5383d74abe
```

`docs/provenance/DOCUMENT_PATH_TRANSLATION_V2.md` records the three root moves.
Resolution is transitive and explicit:

```text
historical recorded path
  -> V1 current path
  -> V2 current path
```

`scripts/provenance/document_path_translation.py` implements this without
basename searching. Unknown paths fail closed. It returns a separate current
path and never rewrites the immutable recorded path in place.

## 5. Frozen content and scientific identity

| Item | SHA-256 before | SHA-256 after/closure |
|---|---|---|
| Final manuscript candidate | `78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2` | `78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2` |
| Handbook v1.5 Markdown | `78780c4033edfbc8260d6fa280723e0d074e5af841154e81832ebc8a06f9c5fc` | `78780c4033edfbc8260d6fa280723e0d074e5af841154e81832ebc8a06f9c5fc` |
| Handbook v1.5 DOCX | `c78ff9f423470ee75ad0b9867d543c2e5d1317742624d815a4b30e9cb7d70132` | `c78ff9f423470ee75ad0b9867d543c2e5d1317742624d815a4b30e9cb7d70132` |
| Related Work V2 verification | `7273183c97d915571b7e16ee865ee5edac97afed080f0a46d95bf46631aded61` | `7273183c97d915571b7e16ee865ee5edac97afed080f0a46d95bf46631aded61` |
| Literature Search V1 JSON | `166f25f76b3cfd6966b15d8b0e2340deb72cce18c4ae01e2b2e85911e59b90d1` | `166f25f76b3cfd6966b15d8b0e2340deb72cce18c4ae01e2b2e85911e59b90d1` |
| Literature Search V2 JSON | `f9a1b681315a541feef1a6c12c8debaeba447c8349b253124ac0560bc948679b` | `f9a1b681315a541feef1a6c12c8debaeba447c8349b253124ac0560bc948679b` |

Every handbook version matched its receipt digest at closure:

| Handbook file | SHA-256 before/after |
|---|---|
| v1.0 DOCX | `669aecc2533e1604bdf0ed8809ec72c6e7129a93e2edb313292745d480674864` |
| v1.1 DOCX | `9a35813abc2a4e31266c5586bf65405a38681e68eb9bfa9722b39dbdee8b9c43` |
| v1.2 DOCX | `af08c216445995fc8cf1d299d0891b9e3b3df3cba4e198311656524a27b99ef9` |
| v1.2 Markdown | `7c7c42a3df43b688f6ab37e5447366374cb5508623b27e5440d87ef169273a32` |
| v1.3 DOCX | `cdc94ece27472ff625389d8b75546e3899a368f9cfcd83567bf6dae299325bf6` |
| v1.3 Markdown | `f06d4babed0a857db26ff629b4e7d4bfb5b171a56b651354f9e8a7f3fe2990ed` |
| v1.4 DOCX | `fe12485d84623560242c7ccd62e28030faccfee1b754b10509c4b2cdcd8759fa` |
| v1.4 Markdown | `f3ab449c5fb532da9b47141d7de9090bdfa32b0c2f16dcaed26f5184e96b594c` |
| v1.5 DOCX | `c78ff9f423470ee75ad0b9867d543c2e5d1317742624d815a4b30e9cb7d70132` |
| v1.5 Markdown | `78780c4033edfbc8260d6fa280723e0d074e5af841154e81832ebc8a06f9c5fc` |

All 23 files moved from `handoffs/` matched their receipt sizes and hashes. No
historical handoff byte was rewritten.

## 6. Provenance-generator checks

- `render_handbook_docx.py` regenerated v1.2 to `/tmp`; all 18 ZIP parts were
  byte-identical to the tracked DOCX.
- `make_f1_f2_f5.py` ran from a scratch copy. Its F1/F2/F5 PNGs were
  byte-identical to the tracked previews. Scratch PDF containers had different
  byte hashes, while the tracked frozen PDFs remained untouched and continued
  to match the move receipt.
- `make_f3_f4.py` was compiled but deliberately not executed: it opens held-out
  E11 artifacts, which the path-only authorization explicitly forbade. Its live
  repository/output path construction was covered by source review and tests.
- No scientific report generator, rescore or experiment was run.

## 7. Verification

All commands used `/home/AI_POC/venvs/tactics/bin/python` where Python was
required.

| Gate | Closure result |
|---|---|
| Translation/path/link focused tests | 35 passed in 0.21 s |
| Literature citation extraction | 22 passed |
| Reproducibility suite | 49 passed in 36.20 s |
| Edge suite | 53 passed in 51.19 s |
| Agent suite | 193 passed in 6.85 s |
| Citation verifier at the V2 manuscript path | 108 keys, 87 unique works, 0 unresolved |
| Manuscript claim guard | 17 expected contextual/negated lexical matches, 0 unqualified overclaims |
| `ruff check .` | all checks passed |
| `git diff --check` | clean |
| Full `pytest tests -q` outside the sandbox | **3,578 passed, 1 skipped, 0 failed**, 15 warnings, 1,103.55 s (18:23) |

The full collection was 3,579 tests: 13 more than the pre-migration 3,566-test
baseline, exactly the seven translation tests plus six hierarchy/link tests.
The skip count remained one. The 15 warnings are the existing Python 3.12
`fork()` deprecation warnings from `test_e12d_loader_scoping.py`.

## 8. Final migration diff classification

The migration commit `c837bee` contains 78 changed paths:

| Classification | Scope | Result |
|---|---|---:|
| A — pure Git move | 58 byte-identical moved files | 58 |
| B — live path reference | 6 moved live files plus `.gitignore`, root README and two live script/provenance indexes | 10 |
| C — path translation V2 | receipt, coupling inventory, V2 table and two explicit resolver/inventory tools | 5 |
| D — living documentation | `ARCHITECTURE.md`, `CURRENT_STATE.md` | 2 |
| E — tests | two new V2 test files and the citation-path regression update | 3 |
| F — unintended/scientific | none | **0** |

Later PR #131 commits added the identifier mapping and research-artifact
presentation. They did not alter any frozen digest or reverse the hierarchy.
PR #132 then reconciled the living state after merge; it is distinct from the
path migration.

## 9. Final state

The authoritative hierarchy is:

```text
docs/paper/
docs/handbook/
docs/handoffs/
audits/
reproducibility/
```

The repository remains research software, not a medical device. The migration
made no scientific or clinical claim. PR #131 is merged; PR #132 remains open
at audit closure. This audit closure is committed locally for review and is not
pushed or merged automatically.

DOCUMENT HIERARCHY MIGRATION V2 SAFE — READY FOR REVIEW
