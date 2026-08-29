# Provenance Incident V1 — commit identifier migration

> **Append-only record.** Filed under the same convention as
> `M1_STAGE1_ATTEMPT1_FAILURE.md` and
> `M2_DEVELOPMENT_ATTEMPT1_FAILURE_AND_RECOVERY_DECISION_V1.md`: the programme
> records what went wrong as a first-class artifact rather than repairing it
> silently.

| | |
|---|---|
| Date | 2026-08-24 |
| Class | provenance reference resolution, non-scientific |
| Scientific artifacts mutated | **none** |
| Resolution | `COMMIT_PIN_TRANSLATION_V1.md`, append-only |
| Status | contained; translation table published |

---

## 1. Incident

The repository history was rewritten to remove 49 `Co-Authored-By` trailers from
commit messages. The rewrite was authorized, executed once, and force-pushed to
`origin/master`.

It changed **commit identifiers**. 268 commit SHAs from `ea27846` (2026-08-07)
forward were replaced.

The repository records scientific provenance by citing commit SHAs. Those
citations were not inventoried before the rewrite, and the rewrite invalidated
their **direct resolution** from `origin/master`. This was a provenance
reference-resolution failure, not scientific corruption: the cited artifacts,
their contents, and their recorded results remained intact.

## 2. Impact

**No change to:**

- code behaviour — the affected values are string constants; nothing resolves a
  commit at runtime, and the test suite is unaffected;
- any scientific result, metric, threshold, checkpoint or digest;
- any file's content — every tree is byte-identical, `git diff ceb339b 0fc999e`
  is empty;
- the sealed B4 test, which remained unopened throughout.

**Affected:**

| | |
|---|---|
| Tracked files carrying a dangling reference | **71** |
| Dangling SHA tokens | **92** |
| Distinct unresolvable commits | **69** |
| Frozen `_V1` records among them | 24 |
| Committed experiment locks among them | 3 |
| Runtime constants in `src/` and `tests/` | 18 files |

The loss is precisely one property: **a third party can no longer follow a pin
from a frozen record to the commit it names.** That property is the
repository's stated contribution, which is why a defect that changes no result
is nonetheless recorded here rather than absorbed.

## 3. Detection

Not detected by the rewrite, which reported success on its own terms: content
identity was verified, commit counts matched, and the contributors objective was
met. Those checks were sound and all passed. None of them asked whether anything
*referred to* the identifiers being replaced.

The dangling references were raised by a second session reviewing the change
afterwards, and confirmed by re-scan.

Two measurement errors occurred during that confirmation and are recorded
because both were checks that passed for the wrong reason:

1. **`git cat-file -t` was used as a reachability test.** It reports objects that
   the local `refs/original` backup keeps alive, so pins appeared to resolve when
   they resolved only locally. Corrected by testing `merge-base --is-ancestor`
   against `origin/master`. The first count was wrong by two orders of magnitude.
2. **The initial scan covered markdown only**, reporting ~50 affected files. A
   full scan of all 445 tracked files found **71**, including 16 source and test
   files and 3 committed locks — the load-bearing cases.

A related false positive was raised and withdrawn in the same review:
`experiment_lock_sha256` was reported as unverifiable after failing to reproduce
under raw-byte and canonical hashing. The registered values were correct; the
hashing input was wrong. See §7 of `COMMIT_PIN_TRANSLATION_V1.md` — the
convention is self-referential and was undocumented, with no verifier in `src/`.

## 4. Resolution

An append-only translation table, `COMMIT_PIN_TRANSLATION_V1.md`, carrying 326
exact mappings in both directions, the derivation method, and an impact index.

In-place correction was considered and is **impossible** for the artifacts that
matter. Experiment locks are sealed by a self-referential digest: correcting a
`git_sha` field changes the lock's own digest, and B4-B's digest is registered in
28 files including three downstream protocol documents and five downstream
experiment locks. 16 affected `docs/` records are likewise sealed by reference,
one of them in 20 places. The translation layer is the only repair that restores
resolution without falsifying a registration.

Pre-rewrite history is preserved in `refs/original`, `refs/local-backup`, and a
verified `--all` bundle. Recovery refs must not be deleted and `git gc
--prune=now` must not be run.

## 5. Prevention

Any future history rewrite in this repository requires, **before** execution:

1. **Provenance pin inventory** — scan all tracked files, not documentation
   alone, for tokens resolving to commits. Test reachability from the remote
   default branch, never object existence.
2. **Frozen artifact dependency scan** — identify artifacts whose digests are
   registered elsewhere, and self-referential digests that cannot absorb an edit.
3. **SHA migration review** — a written statement of what will be invalidated and
   how it will be translated, produced before the rewrite rather than after.
4. **Mapping capture** — retain the rewrite's old→new map at the moment of
   rewrite. Reconstructing it afterwards is possible only because trees were
   unchanged; a rewrite that alters content would not permit it.

## 6. Assessment

The rewrite was authorized with its principal cost stated: SHA churn across 268
commits. The cost that was not stated is the one that materialised — that those
SHAs were load-bearing inside frozen artifacts. The inventory in §5.1 would have
surfaced it in minutes and was not run.

The programme's governance held where it mattered. No scientific artifact was
mutated, no frozen record was edited under pressure to make the problem
disappear, and the sealed test remained closed while the repair was designed. The
failure was detected before an irreversible decision was taken on top of it.
