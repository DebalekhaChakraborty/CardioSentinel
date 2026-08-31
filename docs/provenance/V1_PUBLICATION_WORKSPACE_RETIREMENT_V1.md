# V1 publication workspace — retirement and translation record

**Date:** 2026-08-31
**Last commit in which `docs/paper/` existed as a tracked directory:**
`3ae0a36956f1ec9ea9ee8dee4d6e26cdf2f88fdc`

`docs/paper/` held the V1 TACTiCS manuscript, its outlines, section drafts,
submission logistics and claim audits. `CONTRIBUTING.md` places publication work
outside this computational research artifact, and `CURRENT_STATE.md` records that
**no scientific value is sourced from** that material. It has been removed from
the active tree and gitignored.

**Git history was not rewritten.** Every file remains reachable at
`3ae0a36` and in every commit before it. This change alters repository
organisation only.

---

## 1. What was retired — 18 files, 583,568 bytes

| File | Bytes | SHA-256 |
|---|---:|---|
| `ABSTRACT_CLAIM_AUDIT_V1.md` | 5,392 | `126a8e413ea1e26a…` |
| `CARDIOSENTIN_TACTICS_MANUSCRIPT_V1.md` | 95,393 | `06d590b5f097bf85…` |
| `CARDIOSENTIN_TACTICS_MANUSCRIPT_V2_BODY_FROZEN.md` | 94,003 | `646d133b78cae5a6…` |
| `CARDIOSENTIN_TACTICS_MANUSCRIPT_V3_FINAL_CANDIDATE.md` | 96,408 | `7b05f0f33efcf720…` |
| `CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md` | 97,906 | `78863bcc659f9ee5…` |
| `LITERATURE_SEARCH_V1.md` | 18,974 | `8111102835cee640…` |
| `MANUSCRIPT_V2_ASSEMBLY_PROVENANCE.md` | 1,605 | `e88f1e010f22bf32…` |
| `PAPER_OUTLINE_V1.md` | 16,345 | `6af16994ba5c2240…` |
| `PAPER_OUTLINE_V2.md` | 37,822 | `01a9ebbebb16c639…` |
| `PAPER_S2_RELATED_WORK_DRAFT.md` | 22,029 | `cfcc47e940a91123…` |
| `PAPER_S4_EVIDENCE_FRAMEWORK_DRAFT.md` | 13,071 | `3429d82e30f2c181…` |
| `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md` | 12,308 | `6ebf0a65bbd38563…` |
| `PAPER_S9_DISCUSSION_DRAFT.md` | 29,303 | `30a18f712526c50b…` |
| `PAPER_S9_DISCUSSION_SKELETON.md` | 14,474 | `886cc0779c5486cb…` |
| `PAPER_TABLES_T1_T4_DRAFT.md` | 16,836 | `80e89a4091295fa3…` |
| `TACTICS_OFFICIAL_INSTRUCTIONS_NEEDED.md` | 3,140 | `d9f2fe6957821a96…` |
| `TACTICS_SUBMISSION_ASSET_INVENTORY.md` | 4,877 | `eaf46a75cb8b9032…` |
| `TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md` | 3,682 | `f5034224d60545cc…` |

Manuscript prose was **not** merged anywhere. The canonical science already lives
in experiment reports, frozen protocols, the handbook, the control plane,
evidence and provenance records, explanation reports and `docs/literature/`.
Copying paragraphs out of the manuscript would have created a second authority
for statements those documents already own — the failure this repository's
provenance discipline exists to prevent.

`LITERATURE_SEARCH_V1.md` was retired from `paper/` specifically because the
canonical literature records are under `docs/literature/`.

## 2. What was preserved and relocated — 13 files, 912,267 bytes

The evidence visualizations are research artifacts, not manuscript drafts: their
own README states that no figure computes a new scientific quantity and that every
plotted value traces to a frozen report or promoted run artifact. Each figure now
sits beside the evidence it depicts.

| Old path (under `docs/paper/`) | New path | SHA-256 |
|---|---|---|
| `figures/F1_ips_architecture.pdf` | `docs/control-plane/figures/F1_ips_architecture.pdf` | `676bf598f6cfc259…` |
| `figures/F1_ips_architecture.png` | `docs/control-plane/figures/F1_ips_architecture.png` | `a8da0ba2e2257778…` |
| `figures/F2_partition_authority.pdf` | `docs/control-plane/figures/F2_partition_authority.pdf` | `b5c2ac07d212f443…` |
| `figures/F2_partition_authority.png` | `docs/control-plane/figures/F2_partition_authority.png` | `5ce9f349cf088288…` |
| `figures/F3_episode_reasoning.pdf` | `docs/experiments/w1/figures/F3_episode_reasoning.pdf` | `7d1a18682f8bbd4e…` |
| `figures/F3_episode_reasoning.png` | `docs/experiments/w1/figures/F3_episode_reasoning.png` | `45ffe5da4fdf8798…` |
| `figures/F4_representation_geometry.pdf` | `docs/experiments/b4/figures/F4_representation_geometry.pdf` | `cdb68f6e47138fe0…` |
| `figures/F4_representation_geometry.png` | `docs/experiments/b4/figures/F4_representation_geometry.png` | `59ac382335ab2766…` |
| `figures/F5_guarded_generation.pdf` | `docs/explanation/figures/F5_guarded_generation.pdf` | `f48ec6e019759ef5…` |
| `figures/F5_guarded_generation.png` | `docs/explanation/figures/F5_guarded_generation.png` | `48a1bd4d5d4c0206…` |
| `figures/README.md` | `docs/provenance/EVIDENCE_FIGURES.md` | `d22ae9dbbe53fd7a…` |
| `figures/make_f1_f2_f5.py` | `scripts/provenance/make_f1_f2_f5.py` | `3eb5a2fcd40152ae…` |
| `figures/make_f3_f4.py` | `scripts/provenance/make_f3_f4.py` | `87b99d42b73f2656…` |

The digests above are the values **at the moment of the move**. The ten figure
files moved byte-identical. The three remaining rows did not: both generators had
their output paths rewritten, and the README was repointed and given a locations
paragraph, so their current digests differ from the recorded ones by design.

The two generators write into more than one scientific area each — F1/F2 to the
control plane and F5 to the explanation layer; F3 to W1 and F4 to B4 — so they
could not travel with a single area. They live with the other provenance
generators in `scripts/provenance/`, with per-figure output paths replacing the
former "write beside the script" behaviour.

## 3. Where the manuscript is preserved

| Copy | Location |
|---|---|
| Local, outside the repository | `../publications/CardioSentinel/historical-v1/` |
| Object store, versioned, no Object Lock | `s3://cardiosentinel-drafts-341181499761/historical-v1/docs-paper/` |

Verified on 2026-08-31 the way §8.0 of `CURRENT_STATE.md` verifies: **18/18
re-hashed after download from S3**, 583,568 bytes, and 18/18 compared against
the repository copy before anything was removed.

The `.docx` drafts under `docs/paper/drafts/` were already gitignored and are
already mirrored to the same bucket.

## 4. What did not change

- No scientific result, metric, threshold or calibration.
- No protocol, authorization, attempt receipt or experiment identity.
- No run artifact, checkpoint, feature or physiological data file.
- No consumed one-shot budget was reopened; all fifteen remain spent.
- No frozen T1 document, and no source under `src/`.
- No git history.

## 5. Consequences recorded rather than hidden

**The migration receipt now marks the retired rows `tracked=N`** and repoints the
13 relocated rows. Two tests were updated to match: the tracked-count
assertion for `docs/paper/` was 31 and is now 0 plus a check that the ten
relocated figures are tracked at their new paths, and content-identity
verification now covers rows the tree still holds, because a retired document
keeps its recorded digest as history but leaves no file to hash.

**Six immutable records still quote digests of retired files** — handoff ECG24
and five audits. They are historical records and are not edited to follow a path.
Their digests remain correct statements about what those files were; the files
are simply no longer in the active tree, and this document is where that is
recorded.
