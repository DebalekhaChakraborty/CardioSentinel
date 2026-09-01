# Document path translation — V3

**Date:** 2026-08-31

Recorded paths are never rewritten. This is a third translation applied after V2,
in the same append-only pattern as
[`DOCUMENT_PATH_TRANSLATION_V1.md`](DOCUMENT_PATH_TRANSLATION_V1.md) and
[`DOCUMENT_PATH_TRANSLATION_V2.md`](DOCUMENT_PATH_TRANSLATION_V2.md). Neither of
those records was edited.

## 1. The handbook is split by research programme

`docs/handbook/` held one flat line of revisions, v1.0 to v1.5, all describing
the completed V1 evidence programme. The journal-extension programme has its own
handbook line, which is not a revision of v1.5 and does not supersede it.

| V2 current path | V3 current path |
|---|---|
| `docs/handbook/CardioSentinel_Research_Execution_Handbook_v1.*` | `docs/handbook/v1/CardioSentinel_Research_Execution_Handbook_v1.*` |

`docs/handbook/v2/` is new. It has no recorded historical path, so it appears in
no translation: nothing resolves *to* it from a V1 or V2 record.

**The split is by programme, not by recency.** `v1/` remains authoritative for
what V1 measured. `v2/` governs prospective journal-extension work and grants no
experimental authorization by existing.

## 2. Retired paths now fail closed

`docs/paper/` was retired — see
[`V1_PUBLICATION_WORKSPACE_RETIREMENT_V1.md`](V1_PUBLICATION_WORKSPACE_RETIREMENT_V1.md).
Resolution requires the target to exist, so a recorded `paper/` path now raises
`UnknownDocumentPathError` rather than returning a path to a file that is no
longer in the tree.

That is the intended behaviour and it is now asserted directly. The previous
assertion — that such a path still resolves — passed only where the gitignored
directory happened to survive on disk, and would have failed on a fresh clone.

## 3. Blueprint authority map

The journal-extension blueprint arrived named as a handbook revision. For a short
window the same 1500-line document was staged at two paths. It was never carried
at both on `master`: the duplicate was resolved before either landed.

| | Before | After |
|---|---|---|
| Canonical blueprint | *(none on `master`)* | `docs/journal-extension/CARDIOSENTINEL_TOP_JOURNAL_RESEARCH_MASTER_BLUEPRINT_V2_1.md` |
| Handbook V2 line | `docs/handbook/v2/…_Handbook_v2.0.md` — full copy | `docs/handbook/v2/…_Handbook_v2.1.md` — **pointer, no independent authority** |
| Handbook V2 `.docx` | `…_Handbook_v2.0.docx` | `…_Handbook_v2.1.docx` — rendered copy, authority disclaimed by the pointer beside it |
| Filename vs header | filename `v2.0`, header `Version 2.1` | both **2.1**; the header was not downgraded |

Content digest of the blueprint, identical at both paths while both existed:
`1b2f715cd1952a01f788d391197e9e6446ac59e33433c0c5ab1fde5701c668de`.

**Nothing was deleted.** The full text remains in the history of
`docs/handbook/v2/CardioSentinel_Research_Execution_Handbook_v2.0.md`.

## 4. What this record does not do

It does not rewrite any recorded path, alter any digest, or change what any
historical document says. The ten handbook files moved byte-identical; their
recorded SHA-256 values are unchanged and the migration receipt was repointed,
not re-hashed.
