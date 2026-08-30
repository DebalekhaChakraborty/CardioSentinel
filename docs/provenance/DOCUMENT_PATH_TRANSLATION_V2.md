# Document path translation, V2

**2026-08-29. The publication, handbook and handoff trees moved under
`docs/`.** This is a path-only migration. It does not supersede or rewrite
`DOCUMENT_PATH_TRANSLATION_V1.md`, which remains the historical record of the
2026-08-28 reorganisation.

| V1 current path | V2 current path |
|---|---|
| `paper/...` | `docs/paper/...` |
| `handbook/...` | `docs/handbook/...` |
| `handoffs/...` | `docs/handoffs/...` |

## Transitive resolution

A path recorded before V1 is resolved in two explicit steps:

```text
historical recorded path
  -> DOCUMENT_PATH_TRANSLATION_V1 current path
  -> DOCUMENT_PATH_TRANSLATION_V2 current path
```

Examples:

| Historical recorded path | V1 current path | V2 current path |
|---|---|---|
| `docs/PAPER_S2_RELATED_WORK_DRAFT.md` | `paper/PAPER_S2_RELATED_WORK_DRAFT.md` | `docs/paper/PAPER_S2_RELATED_WORK_DRAFT.md` |
| `docs/handbook/CardioSentinel_Research_Execution_Handbook_v1.5.md` | `handbook/CardioSentinel_Research_Execution_Handbook_v1.5.md` | `docs/handbook/CardioSentinel_Research_Execution_Handbook_v1.5.md` |
| `handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md` | `handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md` | `docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md` |

Resolution is explicit. Unknown paths fail; no basename search or directory
guessing is permitted.

## Recorded path versus opened path

An immutable artifact, frozen report, historical audit or handoff continues to
record the path that was true when it was created. Its bytes are not rewritten.
Code that needs the file now keeps the recorded path unchanged and resolves a
separate current path through V1 and then V2.

The machine-readable move receipt is
`docs/provenance/DOCUMENT_HIERARCHY_MIGRATION_V2_RECEIPT.tsv`. It records 68
filesystem files: 64 tracked files and four ignored owner working drafts. The
move itself changed zero bytes. The four ignored drafts remain ignored at their
new location and have an independent byte-identical safety copy under
`/tmp/cardiosentinel_migration_v2_drafts.r4e5M7/` for this migration session.

## One receipt row was reclassified, 2026-08-30

`docs/handoffs/README.md` was recorded as `content_frozen: Y`, role
`HISTORICAL_HANDOFF`, and
`test_frozen_and_historical_moved_files_retain_content_identity` enforced its
byte size and digest.

**That was a directory-rule artifact, not a judgement.** `_policy()` in
`scripts/provenance/document_hierarchy_inventory.py` classified everything under
`handoffs/` as historical, and the index was swept in with the sessions it
indexes. **It is the one file in that tree whose purpose is to change**: a new
session writes a handoff, and the index has to name it. Frozen, it could not,
and it sat claiming *"Latest: ECG 23"* while ECG 24 and ECG 25 existed.

Session ECG 25 edited it, the test caught the edit, and the edit was reverted
rather than forced. The row is now `content_frozen: N`, role
`LIVE_HANDOFF_INDEX`, and `_policy()` carries the same exception so a regenerated
receipt agrees with this one.

**The migration-time `byte_size` and `sha256` are left as recorded.** They state
what the file was when it moved, which remains true; the flag beside them states
that it is no longer required to stay that way. Nothing else in the receipt
changed, and no other row's classification was revisited.

## Frozen exceptions

- The seven `docs/T1_*.md` / `docs/t1_episode_reasoning.md` files remain flat.
- Immutable artifact-recorded paths are not edited.
- Historical handoffs and all handbook versions retain their bytes.
- The final manuscript remains content-frozen and is opened from its V2 path.

The complete pre-move coupling classification is recorded in
`docs/provenance/DOCUMENT_PATH_COUPLING_INVENTORY_V2.md`.
