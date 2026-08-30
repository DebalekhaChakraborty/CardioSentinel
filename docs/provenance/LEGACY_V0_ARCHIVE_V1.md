# Legacy V0 Archive Receipt V1

**Recorded:** 2026-08-30

**Disposition:** archived outside the active `master` tree

**Scope:** the 2020 college prototype formerly stored at `legacy/v0/`

## 1. Archive identity

The final `master` snapshot containing `legacy/v0/` was merge commit
`b51c25843efab6bdbf6d6ed4caa7dfc46a5a690e` (merge of PR #132). Before the
directory was removed from the active tree, that exact commit was published as:

- protected branch `legacy` (`refs/heads/legacy`);
- annotated tag `archive/legacy-v0-tree` (tag object
  `b72b8c6b773d491ac3807a79ab42097573bb29ca`, targeting the commit above).

At archive creation, the `legacy` branch was locked, administrator enforcement
was enabled, and force-pushes and deletion were disabled. The immutable,
commit-pinned archive is browsable at
[`b51c258/legacy/v0`](https://github.com/DebalekhaChakraborty/CardioSentinel/tree/b51c25843efab6bdbf6d6ed4caa7dfc46a5a690e/legacy/v0).

The Git identities at both archive refs are:

| Object | Git object ID |
|---|---|
| Commit | `b51c25843efab6bdbf6d6ed4caa7dfc46a5a690e` |
| `legacy/` tree | `4894eb0b644f8d6740af05d573bf28cd078eb5ee` |
| `legacy/v0/` tree | `3e4936137d1bb102011ee3a81cd5d36e668fbd6d` |

The older annotated tag `legacy/v0` remains unchanged. It targets original
2020 commit `1c0451e270febe0e20b899c4593e2e0eb1605302`, where the prototype files
were still at repository root. It does not replace the branch and tag above,
which preserve the final `legacy/v0/` layout.

## 2. Content receipt

The archive contains 13 files totalling 1,279,540 bytes. These SHA-256 values
were computed from the clean pre-removal tree:

| Archived path | Bytes | SHA-256 |
|---|---:|---|
| `legacy/v0/Dataset/data 1.csv` | 7,222 | `7ef24b5cec5c923c9bbcb455de9e2362f9f184ed6967532a9c452d44222a33ce` |
| `legacy/v0/Dataset/data 2.csv` | 6,316 | `f45673910f80b129d6fc838166cb16bcd7b83c77c61a0a03d359742283a32139` |
| `legacy/v0/Dataset/data 3.csv` | 4,101 | `c83364681e8fdaffe1c550e152132172e98ee2e369420a9a5d0018bd754e2ffb` |
| `legacy/v0/README.md` | 744 | `9907f12c9c13af448c946d2a7a262911969e28a28454be9995b6d46a7530b45c` |
| `legacy/v0/REPORT.pdf` | 1,001,552 | `220064f9ffb9321be2d6e690ad230739c1b07f4f98425bc7d122da2ab27507f9` |
| `legacy/v0/Results/1/graph.png` | 51,590 | `4cad565cd31cc6f7a0da3e076ddd4fc9625ec3fa9ed393de67ed5fab7863e8b9` |
| `legacy/v0/Results/1/output.png` | 43,776 | `6bca7ce121c8af15805299986652a1da8044fcf08f72e02a02321e95ae2b15f8` |
| `legacy/v0/Results/2/graph.png` | 45,126 | `b83f01a653e63f29eed4f935deeab45d7bb46ee84aa04f38fdb5eea20c909db8` |
| `legacy/v0/Results/2/output.png` | 25,602 | `752b7c1c1cc826d41b597dbe24be838532dc796cf3bb7d805f72ddf405f6ec50` |
| `legacy/v0/Results/3/graph.png` | 57,045 | `f3b929b3400f03a78c49f7aaa08ba4a28da6e8421c3407b076877c7bf441b647` |
| `legacy/v0/Results/3/output.png` | 31,838 | `5e845715c61ba5b336eac9a251385bcaa82c92319529ec8ec242191f6ea01ca0` |
| `legacy/v0/SOURCE CODE.py` | 4,413 | `8dfa31eb69ec18dc72df6cf45d2d2183f487e9f1923c5f68ef5967e2e9e8dcef` |
| `legacy/v0/User Manual.txt` | 215 | `54b496b3b04ce2c76436822943fb110fdf0d1fac200ca91e7d74e92ee0b2801a` |

No archived file was edited as part of the removal. The archive branch and tag
were created before the deletion commit, and both resolved to the tree IDs
above.

## 3. Interpretation boundary

This is historical material, not part of the modern CardioSentinel pipeline.
The fixed-threshold program was never validated for clinical use, and its
outputs are not clinical evidence. The sample CSVs lack verified provenance,
licensing, patient, lead, unit, sampling and annotation metadata and must not be
used for experiments.

Moving the directory off `master` is an organisational and traceability action.
It does not remove the objects from Git history, reduce clone history, establish
rights to the archived material, or make it private. Any legal, privacy or
history-remediation decision remains a separate data-governance task.

## 4. Verification

After fetching the archive branch, its identities can be checked without
checking it out:

```bash
git fetch origin refs/heads/legacy:refs/remotes/origin/legacy
git rev-parse refs/remotes/origin/legacy
git rev-parse refs/remotes/origin/legacy:legacy/v0
git ls-tree -r -l refs/remotes/origin/legacy -- legacy/v0
```

The first two object checks must return the commit and `legacy/v0/` tree IDs in
§1. Individual file contents can be read with `git show` and compared with the
SHA-256 table in §2.

## 5. Active-tree removal verification

The removal branch was verified after the archive-warning contract test was
repointed from the removed README to this receipt:

- the active `legacy/` path was absent;
- the locked archive still contained all 13 files and resolved
  `legacy/v0/` to `3e4936137d1bb102011ee3a81cd5d36e668fbd6d`;
- the Markdown link scan covered 177 files and 49 local links with zero broken
  targets;
- `python -m ruff check .` passed;
- the document-hierarchy and path-translation gates passed, 13 tests;
- the complete suite passed: **3,578 passed, 1 skipped, 0 failed**, with 15
  existing Python 3.12 fork warnings, in 1,124.22 seconds (18:44).

The definitive suite ran from the isolated removal worktree. The repository's
existing ignored evidence roots were exposed to that process as read-only bind
mounts in a private mount namespace, so evidence-bearing tests ran while the
source evidence and the concurrently edited primary checkout remained
unchanged. No scientific artifact was generated, rescored or rewritten.
