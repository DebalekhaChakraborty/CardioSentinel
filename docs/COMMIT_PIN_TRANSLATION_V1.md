# Commit Pin Translation V1

> **Append-only record.** This document adds a translation layer. It modifies no
> existing artifact, edits no frozen record, and changes no scientific value.

| | |
|---|---|
| Class | provenance repair, append-only |
| Supersedes | nothing |
| Modifies | nothing |
| Mapping entries | **326** (323 master + 3 archive-tag orphans) |
| Mapping confidence | **exact** — see §3 |

---

## 1. Purpose

The repository history was rewritten to strip 49 `Co-Authored-By` trailers from
commit messages. The rewrite changed **commit identifiers** and nothing else:

- every file's content is **byte-identical** before and after;
- every tree object is unchanged — `git diff ceb339b 0fc999e` is empty;
- no scientific result, checkpoint, metric, threshold or digest moved;
- no code behaviour changed, and the test suite is unaffected.

What the rewrite did break is **reference resolution**. The repository records
provenance by citing commit SHAs — in frozen `_V1` records, in protocol
documents, in `Final` constants in `src/`, and inside experiment locks. **69
distinct commits cited across 71 tracked files no longer resolve from
`origin/master`.** A reader following such a pin gets nothing.

This document restores that resolution without touching a single referenced
artifact. **The pin is not corrected in place; it is translated here.**

---

## 2. How to use this translation

Use this table whenever a frozen record cites a commit that no longer resolves
directly from `origin/master`:

```text
Frozen document:
Executed at commit 31c7e415e79b

Lookup:
31c7e415e79b → dcb3913cf0f0

Verification:
git show dcb3913cf0f0
```

The old identifier remains the historical value recorded by the frozen
document. The mapped identifier is the corresponding reachable commit to
inspect; it does not amend or replace the frozen record.

---

## 3. Mapping methodology

Each pre-rewrite commit was matched to its post-rewrite counterpart on the
triple:

| Criterion | Why it is sufficient |
|---|---|
| **Tree SHA** | The rewrite altered only commit messages. Every tree is byte-identical, so the tree hash is an unchanged fingerprint of content. |
| **Author timestamp** | Preserved exactly by the rewrite; committer and author dates are unchanged. |
| **Commit subject** | The stripped trailer lived in the message *body*. No subject line changed. |

Every match is **1:1 in both directions** — no old commit maps to two new ones,
and no new commit is claimed by two old ones. All 323 commits reachable from the
pre-rewrite master matched. The 3 remaining entries are off-master orphan commits
held only by `archive/*` tags, mapped through those tags.

> **This is an exact translation, not a heuristic mapping.**

It is independently re-derivable: recover the pre-rewrite history from the bundle
in §9 and repeat the match. No trust in the party that produced this table is
required.

---

## 4. Translation table — old → new

Chronological. **Cited** marks a commit referenced somewhere in the tracked tree;
those 69 rows are the ones that repair a dangling reference.

| Date | Old SHA | New SHA | Cited | Subject |
|---|---|---|---|---|
| 2020-06-25 | `f7ca017d1082` | `f7ca017d1082` |  | Initial commit |
| 2020-06-25 | `c5c3942da97a` | `c5c3942da97a` |  | Update README.md |
| 2020-06-25 | `c2af2662fe25` | `c2af2662fe25` |  | DATASET/ |
| 2020-06-25 | `e24dcc812d7c` | `e24dcc812d7c` |  | Delete data 1.csv |
| 2020-06-25 | `679c46e7de6e` | `679c46e7de6e` |  | Delete data 2.csv |
| 2020-06-25 | `ef27fee38734` | `ef27fee38734` |  | Delete data 3.xlsx |
| 2020-06-25 | `483f8eefa654` | `483f8eefa654` |  | Dataset/data 1 |
| 2020-06-25 | `3bbff123326b` | `3bbff123326b` |  | Delete data 1.csv |
| 2020-06-25 | `23450db9a12d` | `23450db9a12d` |  | Create data 1 |
| 2020-06-25 | `4891f5171519` | `4891f5171519` |  | Add files via upload |
| 2020-06-25 | `6ea2df11af10` | `6ea2df11af10` |  | Delete data 1 |
| 2020-06-25 | `98d2b0f7e036` | `98d2b0f7e036` |  | Delete data 3.csv |
| 2020-06-25 | `3d6a3f2a0a08` | `3d6a3f2a0a08` |  | Add files via upload |
| 2020-06-25 | `35e803c675b1` | `35e803c675b1` |  | Create x |
| 2020-06-25 | `475d58aa2dd8` | `475d58aa2dd8` |  | Delete x |
| 2020-06-25 | `45b21c733dcf` | `45b21c733dcf` |  | Create x |
| 2020-06-25 | `3111f4e186f2` | `3111f4e186f2` |  | Add files via upload |
| 2020-06-25 | `2383e33ac64d` | `2383e33ac64d` |  | Delete x |
| 2020-06-25 | `ca0c3728a60d` | `ca0c3728a60d` |  | Create x |
| 2020-06-25 | `8d2dd0bf18c7` | `8d2dd0bf18c7` |  | Add files via upload |
| 2020-06-25 | `5f66f6e48b24` | `5f66f6e48b24` |  | Delete x |
| 2020-06-25 | `fc829ee0da8f` | `fc829ee0da8f` |  | Create x |
| 2020-06-25 | `fd8787109b07` | `fd8787109b07` |  | Add files via upload |
| 2020-06-25 | `b63f082d5141` | `b63f082d5141` |  | Delete x |
| 2020-06-25 | `d25abca2ed85` | `d25abca2ed85` |  | Add files via upload |
| 2020-06-27 | `1c0451e270fe` | `1c0451e270fe` |  | Update README.md |
| 2026-08-06 | `a4e71e287e7f` | `a4e71e287e7f` |  | restarting.. |
| 2026-08-06 | `eab171343431` | `eab171343431` |  | Merge pull request #1 from DebalekhaChakraborty/research/cardi… |
| 2026-08-06 | `24acff5210cf` | `24acff5210cf` |  | Phase 1: add PhysioNet ingestion contracts |
| 2026-08-06 | `4d1d738c500c` | `4d1d738c500c` |  | Phase 1: audit PhysioNet annotation semantics |
| 2026-08-06 | `1f803f394947` | `1f803f394947` |  | Merge pull request #2 from DebalekhaChakraborty/research/phase… |
| 2026-08-06 | `2cc8baaa7545` | `2cc8baaa7545` |  | Phase 2: add causal ECG signal pipeline |
| 2026-08-07 | `387f8351ce70` | `387f8351ce70` |  | Phase 2: correct signal quality units and spectral support |
| 2026-08-07 | `f93047a0d167` | `f93047a0d167` |  | Merge pull request #3 from DebalekhaChakraborty/research/phase… |
| 2026-08-07 | `9a1715c325bc` | `9a1715c325bc` |  | Phase 3A: freeze benchmark protocol and subject splits |
| 2026-08-07 | `85cfa2056c69` | `85cfa2056c69` |  | Phase 3A: finalize benchmark challenge balance and mixed-event… |
| 2026-08-07 | `5dea66cc674b` | `5dea66cc674b` |  | Phase 3A: bound sparse conduction challenge claims |
| 2026-08-07 | `0aa30d5b6edb` | `0aa30d5b6edb` |  | Merge pull request #4 from DebalekhaChakraborty/research/phase… |
| 2026-08-07 | `bf5566e18209` | `bf5566e18209` |  | Phase 3B: add reproducible classical ECG baselines |
| 2026-08-07 | `a600c7ee4f82` | `a600c7ee4f82` |  | Phase 3B: harden metric semantics and full-run scalability |
| 2026-08-07 | `5583dca8d400` | `5583dca8d400` |  | Phase 3B: verify pinned PhysioNet waveform source |
| 2026-08-07 | `4b20a284aac9` | `4b20a284aac9` |  | Phase 3B: support verified LTSTDB unit aliases |
| 2026-08-07 | `0f059ad2f2e0` | `0f059ad2f2e0` |  | Phase 3B: add materialization progress monitor |
| 2026-08-07 | `184646218ef1` | `184646218ef1` |  | Phase 3B: ignore external experiment artifacts |
| 2026-08-07 | `301d4bd6ca55` | `301d4bd6ca55` |  | Phase 3B: allow gitignored local experiment storage |
| 2026-08-07 | `9c8ac4697b93` | `9c8ac4697b93` |  | Phase 3B: preserve corpus integrity audit |
| 2026-08-07 | `86b4bdfcba02` | `86b4bdfcba02` |  | Phase 3B: optimize exact validation threshold sweep |
| 2026-08-07 | `4f57ba38d4df` | `4f57ba38d4df` |  | Phase 3B: harden MCC for benchmark-scale counts |
| 2026-08-07 | `87b5d39d9103` | `87b5d39d9103` |  | Phase 3B: close frozen classical baseline evidence |
| 2026-08-07 | `e1479aa8b1b0` | `e1479aa8b1b0` |  | Merge pull request #5 from DebalekhaChakraborty/research/phase… |
| 2026-08-07 | `ad02266bb691` | `ad02266bb691` |  | CI: install ML extras for full test suite |
| 2026-08-07 | `8f488dcd23d9` | `8f488dcd23d9` |  | Merge pull request #6 from DebalekhaChakraborty/chore/ci-insta… |
| 2026-08-07 | `2f5bfbeff630` | `2f5bfbeff630` |  | Phase 3B-2: freeze compact raw-waveform baseline protocol |
| 2026-08-07 | `e964fd131534` | `e964fd131534` |  | Phase 3B-2: implement frozen B4 neural baseline |
| 2026-08-07 | `b19e93d5aa67` | `b19e93d5aa67` |  | Phase 3B-2: harden lossless B4 waveform pipeline |
| 2026-08-07 | `31c7e415e79b` | `dcb3913cf0f0` |  | Merge pull request #7 from DebalekhaChakraborty/research/phase… |
| 2026-08-07 | `ea2784659e08` | `2c931cfa397e` | **yes** | Docs: reflect implemented untrained B4 baseline |
| 2026-08-08 | `f2b9268b6bd2` | `67e0615f6f32` |  | Merge pull request #8 from DebalekhaChakraborty/research/phase… |
| 2026-08-08 | `8455e748cfb0` | `72e1a1cf97ca` |  | Phase 3B-2: implement canonical B4 experiment runner |
| 2026-08-08 | `fc7ac01a2758` | `3171540cf989` |  | Phase 3B-2: harden B4 experiment provenance |
| 2026-08-08 | `21a38ec5c081` | `f341fe37ffc3` | **yes** | Merge pull request #9 from DebalekhaChakraborty/research/phase… |
| 2026-08-08 | `2f379c75503d` | `828e34f318ea` |  | Phase 3B-2: implement one-shot B4 test evaluator |
| 2026-08-08 | `598e6c363b38` | `4a2363dc1be9` |  | Phase 3B-2: harden one-shot test integrity |
| 2026-08-08 | `ab15137fe8ba` | `b01c16315542` |  | Merge pull request #10 from DebalekhaChakraborty/research/phas… |
| 2026-08-08 | `9c9c631dcd7a` | `8ccce22a4641` |  | Phase 3B-2: freeze Transformer and SSM architecture protocol |
| 2026-08-08 | `9ed8fc930740` | `a415074c8a53` |  | Phase 3B-2: harden Transformer and SSM protocol semantics |
| 2026-08-08 | `3d03fa6cce7b` | `c4eb9e2862fb` |  | Merge pull request #11 from DebalekhaChakraborty/research/phas… |
| 2026-08-08 | `b6ccb8e80ee7` | `91bece082be5` |  | Phase 3B-2: implement frozen Transformer and SSM candidates |
| 2026-08-08 | `8cf1cb03ca5d` | `d638e4c770a7` |  | Merge pull request #12 from DebalekhaChakraborty/research/phas… |
| 2026-08-08 | `4b8f087657fe` | `602b17c45ca4` |  | Phase 3B-2: implement candidate experiment runners |
| 2026-08-08 | `2a75a90c5c2a` | `5751417e5b0b` |  | Phase 3B-2: harden official resource benchmark evidence |
| 2026-08-08 | `f1bf641fc54b` | `d6e8c3937c71` |  | Tests: make resource-benchmark tests host-independent |
| 2026-08-08 | `3ce81f41c22b` | `bcba9b00aaea` |  | Phase 3B-2: seal official resource benchmark execution path |
| 2026-08-08 | `4dac065f43e8` | `e3647161727f` |  | Phase 3B-2: atomically claim canonical candidate runs |
| 2026-08-08 | `b27d528c7851` | `8d62f4e7c64b` | **yes** | Merge pull request #13 from DebalekhaChakraborty/research/phas… |
| 2026-08-10 | `917cb1eb34ca` | `019c85120f94` |  | Phase 3B-2: add validation challenge evidence tooling |
| 2026-08-10 | `03647df18219` | `99b13064c2f6` |  | Phase 3B-2: correct challenge evidence to locked-model inferen… |
| 2026-08-10 | `90ad879f5e69` | `d8923caae2bf` |  | Phase 3B-2: final challenge-tooling correction |
| 2026-08-10 | `a185689f43e5` | `586fb06a38a1` |  | Fix validation challenge runtime-gate test isolation |
| 2026-08-10 | `9b5027522c37` | `3a718b379355` |  | Merge pull request #14 from DebalekhaChakraborty/research/phas… |
| 2026-08-10 | `566b955bd660` | `8325aec47ff9` |  | Phase 3B-2: freeze global encoder selection |
| 2026-08-10 | `71c73617e880` | `cdedb270c304` |  | Merge pull request #15 from DebalekhaChakraborty/research/phas… |
| 2026-08-10 | `d6af68d61931` | `74321a88c1f7` |  | Phase 4 groundwork: defer B4 sealed test, expose B4-B encoder … |
| 2026-08-10 | `eb89ed1438f4` | `9c77902b3f43` |  | Phase 4: freeze physiology-fusion experiment |
| 2026-08-10 | `e7ee78ea8d44` | `48b0305a683b` |  | Phase 4 / P1: complete the canonical execution path |
| 2026-08-10 | `fe7b8dc27895` | `fa433ee2313a` |  | Phase 4 / P1: close six execution-integrity blockers |
| 2026-08-10 | `1e6f0da8c83d` | `2d395e1c1e39` |  | Phase 4 / P1: separate primary and challenge populations, add … |
| 2026-08-10 | `0c202795a7a0` | `33002b07dcfb` |  | Phase 4 / P1: bind Stage-1 provenance before digesting and wri… |
| 2026-08-10 | `7e02c22d29bb` | `bc15e4ee7674` | **yes** | Merge pull request #16 from DebalekhaChakraborty/research/phas… |
| 2026-08-10 | `64dcc14dac53` | `baf5260236ff` |  | Phase 5 groundwork: freeze P1 physiology retention decision |
| 2026-08-10 | `a4001dfb3168` | `653c96fe586d` |  | Phase 5 / M1: freeze causal dual-memory protocol and execution… |
| 2026-08-10 | `3fd41927dc7c` | `39fb6cc863b9` |  | Phase 5 / M1: close five canonical execution-integrity blockers |
| 2026-08-10 | `8179091a72d3` | `af0eca0dd9b9` |  | Merge pull request #17 from DebalekhaChakraborty/research/phas… |
| 2026-08-10 | `51b95de59d9c` | `de1c7d1d9f24` |  | M1: correct LTSTDB channel cardinality before scientific execu… |
| 2026-08-10 | `229fb6ecda98` | `b54d4f9f9650` | **yes** | Merge pull request #18 from DebalekhaChakraborty/research/m1-c… |
| 2026-08-11 | `80a1466c7d6c` | `30a840a14473` |  | M1: bounded-memory execution after pre-claim Stage-1 failure |
| 2026-08-11 | `4e1dbd0171a6` | `aa0ede8ebd70` |  | M1: exact waveform-read provenance, full schema-2 revalidation… |
| 2026-08-11 | `f8abf535cdf7` | `5ff66ea1c7a0` | **yes** | Merge pull request #19 from DebalekhaChakraborty/research/m1-b… |
| 2026-08-12 | `60855531ea24` | `8299d43e13a7` |  | M1-v2: define physical observation availability before patient… |
| 2026-08-12 | `16a82deae5da` | `ea9af1d27df7` |  | M1-v2: canonical all-NaN unavailable rows, exact loader sentin… |
| 2026-08-12 | `8260b718ab23` | `5d3a29fd6ee0` | **yes** | Merge pull request #20 from DebalekhaChakraborty/research/m1-v… |
| 2026-08-12 | `80b4b3995983` | `c61bb6e3f8fb` | **yes** | M1 retention freeze (M1L) and prospective M2 contamination-saf… |
| 2026-08-12 | `510eea036da6` | `752148e5ceef` | **yes** | M2-v1: freeze the scientific update policy and derive its TRAI… |
| 2026-08-12 | `27c246247f91` | `23500c3ed15e` | **yes** | Record the prospective runtime-integrity sentinel design |
| 2026-08-12 | `88e793399961` | `8410080c3bdc` |  | M2-v1 gate: read-only TRAIN-only derivation verifier |
| 2026-08-13 | `32b505d27250` | `ea14c4d41a99` |  | M2-v1 gate: extend derivation verifier to full receipt coverage |
| 2026-08-13 | `1aece7f26a51` | `067b75e1cf4d` | **yes** | M2-v1 gate: reproduce receipt fields via recovered historical … |
| 2026-08-13 | `7e5896a48d8f` | `2038104a690f` |  | M2-v1 gate: pin intra-op thread count for deterministic M1L sc… |
| 2026-08-13 | `abfbdc562afb` | `67b5ec8c5492` |  | M2-v1 gate: canonicalize TRAIN-only receipt provenance under t… |
| 2026-08-13 | `e6a2368e2257` | `0462d2bb23ba` |  | Merge pull request #21 from DebalekhaChakraborty/research/m1-r… |
| 2026-08-13 | `82a9cff6a778` | `315fcace71dc` |  | M2-v1: implement the frozen contamination-safe memory update p… |
| 2026-08-13 | `fcb5ebb14ae3` | `7cfe77095e4a` |  | M2-v1: correct evidence semantics from human implementation re… |
| 2026-08-13 | `6e675e8a7ead` | `b79d3553b298` |  | Merge pull request #22 from DebalekhaChakraborty/research/m2-c… |
| 2026-08-13 | `72e6bb3c5516` | `fb07563e0da3` |  | M2-v1: bind canonical scorer and scientific execution harness |
| 2026-08-13 | `0e60c1d3584d` | `5ee1733efce2` |  | M2-v1: make sentinel tests independent of the ambient environm… |
| 2026-08-13 | `cf55d9f4ee6d` | `23d642febb34` |  | M2-v1: enforce the frozen threshold everywhere and key the ann… |
| 2026-08-13 | `251bcb7a74dc` | `7760d012e07e` |  | M2-v1: correct claim-bearing persistence ordering and governan… |
| 2026-08-13 | `6e272ff61598` | `a0344cc8ffd6` |  | M2-v1: make persistence tests independent of the ambient runti… |
| 2026-08-13 | `8e7c773f072f` | `463f6da8be16` |  | M2-v1: frozen-digest claim invariant, one provenance path, ver… |
| 2026-08-13 | `83238686d7aa` | `46e9fe3d34ab` |  | M2-v1: canonical population authority, result contract, per-ar… |
| 2026-08-13 | `e246c84ac7bc` | `53b495144bfe` | **yes** | Merge pull request #23 from DebalekhaChakraborty/research/m2-c… |
| 2026-08-13 | `8268587994f0` | `3f52dfe12362` |  | M2-v1: freeze stress-interval eligibility and build the source… |
| 2026-08-13 | `26fdbdb34500` | `0cec1e271850` |  | M2-v1: activate the canonical development execution route |
| 2026-08-13 | `f7dd23946718` | `c20baa31be1a` |  | M2-v1: make the canonical one-shot route actually executable |
| 2026-08-13 | `3af94bfcb743` | `6316a300f50d` |  | M2-v1: immutable suite identity and a self-proving canonical s… |
| 2026-08-13 | `3c1ba4ce87ad` | `530da77621e5` | **yes** | Merge pull request #24 from DebalekhaChakraborty/research/m2-d… |
| 2026-08-13 | `8de65aca300a` | `48f4aab504ec` |  | M2-v1: recover the canonical development route after the pre-s… |
| 2026-08-14 | `74df6cc3f2cd` | `8e2af81c8e81` |  | M2-v1: prove attempt #1 from artifacts and report real recover… |
| 2026-08-14 | `4d388bf45469` | `e67672648a0a` |  | M2-v1: make failure promotion state authoritative from the act… |
| 2026-08-14 | `d77fbdc37415` | `a178a5b00160` | **yes** | Merge pull request #25 from DebalekhaChakraborty/research/m2-d… |
| 2026-08-14 | `eb025dc24820` | `e77f23712750` | **yes** | M2-v1: preserve source-null SQI semantics and prepare recovery2 |
| 2026-08-14 | `cdc33797c3b7` | `12a7e8972e7e` | **yes** | Merge pull request #26 from DebalekhaChakraborty/research/m2-d… |
| 2026-08-14 | `ea2a3632866e` | `082b2b8c83a0` |  | M2-v1: freeze the human bounded-Pareto retention of M2-G |
| 2026-08-14 | `ba20fc94465a` | `89a9af8294c0` | **yes** | Merge pull request #27 from DebalekhaChakraborty/research/m2-r… |
| 2026-08-14 | `8956f2195e3c` | `6863f5f503e9` |  | U1: freeze the calibration and selective-routing protocol |
| 2026-08-14 | `4cab34f18f45` | `6f7f62455056` |  | U1: separate OOF evidence from the deployable calibrator, and … |
| 2026-08-16 | `32aae59a56ec` | `1e58ac116f0e` | **yes** | U1: make the equal-mass ECE helper actually perform its frozen… |
| 2026-08-16 | `02f1ee41fe36` | `e7e06b31da19` | **yes** | Merge pull request #28 from DebalekhaChakraborty/research/u1-c… |
| 2026-08-17 | `3c4584e53280` | `111bea4467e6` |  | U1: implement the frozen calibration and selective-routing exe… |
| 2026-08-17 | `efdb5a2e9f24` | `80fe6e813bfd` | **yes** | U1: close input and output provenance around the execution har… |
| 2026-08-17 | `233a474aca14` | `7828db772b69` | **yes** | Merge pull request #29 from DebalekhaChakraborty/research/u1-e… |
| 2026-08-17 | `a889f22cd4c7` | `6ad85039f5eb` |  | U1: retain Platt calibration and freeze the window-router reje… |
| 2026-08-17 | `cb34ca08745c` | `44fc30bcc911` |  | U1: state the accepted-sensitivity denominator unambiguously |
| 2026-08-17 | `997df407376e` | `51d1e8a22bee` | **yes** | Merge pull request #30 from DebalekhaChakraborty/research/u1-r… |
| 2026-08-17 | `d39bcf53c102` | `73600ae338db` |  | T2: freeze the causal longitudinal temporal-intelligence proto… |
| 2026-08-18 | `0223a5bf0826` | `6147811b6ce6` |  | T2: close the temporal scientific semantics before implementat… |
| 2026-08-18 | `5a84b382bebb` | `7edebe382b75` |  | T2: bind row identity to the row so replay lineage cannot be a… |
| 2026-08-18 | `c975ce709c2c` | `a089a601b07f` | **yes** | Merge pull request #31 from DebalekhaChakraborty/research/t2-t… |
| 2026-08-18 | `431bd158b740` | `e3beee788797` | **yes** | T2: implement causal GRU/S4D training and execution harness |
| 2026-08-19 | `2620da3eec31` | `01291bc8cfc7` | **yes** | T2: assemble the canonical training route and close its proven… |
| 2026-08-19 | `8eccdd9e0ad5` | `f79a73ce5590` | **yes** | T2: give the assembled-route tests the frozen-runtime seam |
| 2026-08-19 | `62b56c312518` | `0cc4925eeab0` | **yes** | T2: disarm the injected fault instead of undoing every seam |
| 2026-08-19 | `64ff2673ec84` | `d91b7716169b` | **yes** | T2: close the execution-governance and outer-evidence gaps |
| 2026-08-19 | `951503ea6439` | `70dfc24516ea` | **yes** | T2: bind one commit and one device, and narrow the canonical o… |
| 2026-08-19 | `f4759e2a97d1` | `8916668ef849` | **yes** | Merge pull request #32 from DebalekhaChakraborty/research/t2-e… |
| 2026-08-19 | `36497d94097c` | `6a80c07f2152` |  | T2: activate reviewed one-shot outer validation |
| 2026-08-19 | `b0f189a57bea` | `e107082e45c0` | **yes** | Merge pull request #33 from DebalekhaChakraborty/research/t2-o… |
| 2026-08-19 | `bc46fca6b903` | `20ed000c87b3` |  | T2: freeze longitudinal S4D retention decision |
| 2026-08-19 | `1ff85cdbd8d5` | `23924c55af70` |  | T2: make the one-shot artifact guards byte-safe |
| 2026-08-19 | `b3004da9dcd8` | `0e7a9d9b387c` | **yes** | Merge pull request #34 from DebalekhaChakraborty/research/t2-r… |
| 2026-08-20 | `7544ad0eb07e` | `aea59d2fa44e` | **yes** | T1: freeze the prospective causal episode-state protocol |
| 2026-08-20 | `9fa7e88ee648` | `759ad4d5d83d` | **yes** | Merge pull request #35 from DebalekhaChakraborty/research/t1-s… |
| 2026-08-20 | `f30350d6322f` | `bee594f5bff8` | **yes** | T1: add the model-agnostic episode-state execution harness |
| 2026-08-20 | `377995089314` | `fdf2748214e2` |  | T1: freeze canonical development execution specification |
| 2026-08-20 | `0229f3fdb626` | `f342bbf5b57b` |  | T1: make the comment-repair proof interpreter-independent |
| 2026-08-20 | `724299555741` | `39c88a6a8d7a` | **yes** | Merge pull request #37 from DebalekhaChakraborty/research/t1-e… |
| 2026-08-20 | `139b5a40e979` | `5514a46f4c2f` |  | Merge branch 'master' into research/t1-execution-harness-v1 |
| 2026-08-20 | `c472fba6f822` | `e8ad07182ce3` | **yes** | T1: harden the episode-state engine against the merged executi… |
| 2026-08-20 | `2672a723f2c5` | `bfd32281a651` | **yes** | Merge pull request #36 from DebalekhaChakraborty/research/t1-e… |
| 2026-08-20 | `2feb76c2bc64` | `6a964e6393d6` | **yes** | T1: implement the canonical development harness |
| 2026-08-21 | `f91c417054c4` | `535a9a042f81` | **yes** | T1: skip canonical-claim tests outside the frozen interpreter |
| 2026-08-21 | `5804e66668dd` | `1ed115da5712` | **yes** | Merge pull request #38 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-21 | `6937b49e493a` | `3c10f4e7e356` |  | T1: make the authorization tests environment-honest |
| 2026-08-21 | `0639c9e20a58` | `a059d6ca81f1` |  | T1: add the canonical development execution driver |
| 2026-08-21 | `bbefa385b7d1` | `7a9d3e26ba71` |  | T1: add the fold-scoped evaluation authority |
| 2026-08-21 | `e6f5dfeacd03` | `ed5bb2872e57` |  | Merge pull request #40 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-21 | `bbb78d8cbb5e` | `50338e22a85d` |  | Merge pull request #41 from DebalekhaChakraborty/research/t1-f… |
| 2026-08-21 | `74f4c94ae2e9` | `c752e1a4f674` |  | T1: add the controlled fold evaluation capability |
| 2026-08-21 | `c7a458ab835c` | `d711303fe256` |  | Merge pull request #42 from DebalekhaChakraborty/research/t1-f… |
| 2026-08-21 | `e72c93ae4a6c` | `ac72487a8e0a` |  | T1: prove capability before the claim, not after it |
| 2026-08-21 | `68478afc1689` | `43e2c082e117` |  | T1: add the label-bearing assembly collaborators |
| 2026-08-21 | `c578f21867be` | `7a7dbcee4c90` |  | T1: make the assembly collaborators answerable to the capabili… |
| 2026-08-21 | `a54566699a8b` | `5e1c8e7835a5` |  | Merge pull request #43 from DebalekhaChakraborty/research/t1-a… |
| 2026-08-21 | `34abdc8beb69` | `790637bfa36b` |  | T1: implement the canonical fold evaluator |
| 2026-08-21 | `95254b773830` | `9d38a8fe7219` |  | Merge pull request #44 from DebalekhaChakraborty/research/t1-f… |
| 2026-08-21 | `b202840bd58d` | `e47e32f2a827` |  | T1: derive challenge membership from the canonical identity |
| 2026-08-21 | `9e16e328555f` | `c8463ef68f35` |  | T1: assemble subject evidence from the held-out evaluations |
| 2026-08-21 | `c87be5dbcc40` | `c3ca4d98f087` |  | T1: implement the final all-VALIDATION configuration selection |
| 2026-08-21 | `3c8d43387111` | `cd24de69fea2` |  | T1: compose the canonical execution graph and delegate |
| 2026-08-21 | `64d5fc91c225` | `b0984630dbf7` | **yes** | Merge pull request #45 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-21 | `2a5e83e14526` | `148076820624` |  | Docs: sync plan, scope, and README to actual repository state |
| 2026-08-21 | `064fe5e06857` | `6d42c8574c65` | **yes** | Merge pull request #46 from DebalekhaChakraborty/docs/sync-cur… |
| 2026-08-21 | `d2bd34de2c2c` | `3fa20b634e18` |  | T1: authorize canonical development execution |
| 2026-08-21 | `c538181eb938` | `0a69daa3ae2c` | **yes** | Merge pull request #47 from DebalekhaChakraborty/research/t1-e… |
| 2026-08-21 | `61ad0b6d49b8` | `b83b08b1543e` |  | T1: freeze the execution recovery amendment V1.1 |
| 2026-08-21 | `7a9f92edf3d8` | `b92db8d78c93` |  | Merge pull request #48 from DebalekhaChakraborty/docs/t1-execu… |
| 2026-08-21 | `fb89ae5fe874` | `aa2313c6dfa9` |  | T1: make the canonical path fail diagnosably |
| 2026-08-21 | `166136c803b2` | `d030cbc18527` |  | Merge pull request #49 from DebalekhaChakraborty/research/t1-r… |
| 2026-08-21 | `de47be9e8b70` | `0961ce387756` |  | T1: persist held-out evaluation evidence |
| 2026-08-21 | `8db30ffc8800` | `2ad3f3535192` | **yes** | Merge pull request #50 from DebalekhaChakraborty/research/t1-h… |
| 2026-08-21 | `48cf7d2b84a8` | `62c0d38f0027` |  | T1: prove the attempt was not consumed, not that it never ran |
| 2026-08-21 | `b343bb506d04` | `f98e4b4a1798` |  | T1: bind recovery amendment provenance and reconstruct failed … |
| 2026-08-21 | `a8682e982c09` | `f884be1114ed` |  | T1: make the attempt guard true in both worlds |
| 2026-08-21 | `8c1b1e02a6c5` | `95767ef72e02` |  | T1: branch the recovery gates on attempt presence too |
| 2026-08-22 | `e1c2dc202e5e` | `649eafb8b169` |  | Merge pull request #51 from DebalekhaChakraborty/research/t1-a… |
| 2026-08-22 | `39ede04a3aac` | `df48d713f71e` |  | Merge pull request #52 from DebalekhaChakraborty/research/t1-r… |
| 2026-08-22 | `d7b2d425fa23` | `f8aa0fbbb998` |  | T1: make the continuation reachable under its own governance |
| 2026-08-22 | `fa57bcfb3440` | `30774c7c52fb` |  | T1: make the Layer 2 runtime proof non-vacuous |
| 2026-08-22 | `eae3cda029a6` | `3122ab03c2c9` |  | Merge pull request #53 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-22 | `854317757429` | `be6ccd2590b6` |  | T1: give the continuation its own evidence contract |
| 2026-08-22 | `ec62302d761f` | `6b60b47366e4` |  | Merge pull request #54 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-22 | `a0b2e198885c` | `926d2ef11243` |  | T1: implement gated continuation measurement execution engine |
| 2026-08-22 | `bd61c1413456` | `b8ffae576f4d` |  | Merge pull request #55 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-22 | `e5432761c71e` | `5fde651f8832` |  | T1: reach held-out labels through the authority, not past it |
| 2026-08-22 | `8ed90c631716` | `b4f0d20d8332` |  | T1: validate the identity artifact without opening a label |
| 2026-08-22 | `467272220ea4` | `32a5124552a2` | **yes** | Merge pull request #56 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-22 | `7eb3579cc258` | `2f2f532d47cb` |  | T1: record continuation pre-authorization, unsigned |
| 2026-08-22 | `a888b13380f2` | `22b6c2a9ae3c` |  | Merge pull request #57 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-22 | `1feff5972ffb` | `e812ce7dd683` |  | T1: sign the pre-authorization record |
| 2026-08-22 | `b40b4acac168` | `ec91545923bf` | **yes** | T1: authorize the continuation execution |
| 2026-08-22 | `a3f535bb081b` | `0d78058cbb77` |  | T1: name the package guard rather than counting fixtures |
| 2026-08-22 | `ec438468446c` | `ab1dc3d8261b` |  | Merge pull request #58 from DebalekhaChakraborty/research/t1-a… |
| 2026-08-22 | `76e35d496822` | `9cf120d195cb` |  | T1: execute the claim-to-lock seam before it executes for real |
| 2026-08-22 | `61704aa7259d` | `d1b2e7e96e3d` | **yes** | Merge pull request #59 from DebalekhaChakraborty/research/t1-c… |
| 2026-08-22 | `08152c87fe70` | `1151d5f29417` |  | Record T1 analysis pre-registration and continuation execution |
| 2026-08-22 | `086161f6c3b0` | `645ca9e899e7` |  | Add endpoint and claim hierarchy to the T1 analysis plan |
| 2026-08-22 | `8a0132c1c9e5` | `9959e650ab54` |  | Pin the bootstrap's estimand before the values are read |
| 2026-08-22 | `67422912496f` | `2e10d6771b9b` |  | Fix the primary estimate, the latency wording, and the exclusi… |
| 2026-08-22 | `a8784053e4ed` | `30d546eb0e2a` |  | Merge pull request #60 from DebalekhaChakraborty/t1/analysis-p… |
| 2026-08-22 | `16c96f613501` | `ae19fd467e8f` |  | T1: generate the preregistered evidence report |
| 2026-08-22 | `9a037356aa72` | `e45cb3a47f7d` |  | Merge pull request #61 from DebalekhaChakraborty/t1/preregiste… |
| 2026-08-22 | `c3374044b2f3` | `b8fdc63c5144` |  | T1: post-hoc failure mode analysis and interpretation |
| 2026-08-22 | `73358bc1469b` | `fac810ccb334` |  | Merge pull request #62 from DebalekhaChakraborty/t1/post-hoc-f… |
| 2026-08-22 | `b79185f4c67f` | `ebf6d6d87658` |  | T2: preregistered S4D vs GRU outer validation analysis plan |
| 2026-08-22 | `1bbbd4702009` | `1f63261170c2` | **yes** | Merge pull request #63 from DebalekhaChakraborty/t2/arm-compar… |
| 2026-08-22 | `b779926c3eac` | `31f4c17ac77b` |  | Docs: refresh CURRENT_STATE against master 1bbbd47 |
| 2026-08-22 | `36eb54aa1d09` | `a6cc4e034652` |  | Docs: Research Execution Handbook v1.2, a revision of v1.1 |
| 2026-08-22 | `f39021de60bb` | `53aebb171f04` |  | Handbook v1.2: add system inventory, findings, and roadmap |
| 2026-08-22 | `05094d79874a` | `e360914c61d2` |  | Merge pull request #64 from DebalekhaChakraborty/docs/refresh-… |
| 2026-08-22 | `c99c8a85a22d` | `4aa71e7d863b` | **yes** | Merge pull request #65 from DebalekhaChakraborty/docs/research… |
| 2026-08-22 | `0ec0999d6cf9` | `0625cead0374` |  | Docs: rename Handbook v1.2 to the v1.0/v1.1 convention, add .d… |
| 2026-08-22 | `c3237d1ec3e8` | `ff41a786e0cc` |  | Track the document generators that produced the T1 reports and… |
| 2026-08-22 | `c06644f46b6a` | `696e0080d1da` |  | Correct stale status claims in IMPLEMENTATION_PLAN and README |
| 2026-08-22 | `3863384dc0c3` | `fc2fff5d2e9d` |  | Repair 13 stale continuation assertions and three stale firewa… |
| 2026-08-22 | `25a6b5dcac5e` | `f982a7e51a60` |  | T2: implement the one derived analysis the arm-comparison plan… |
| 2026-08-22 | `3684ca1ab68e` | `2b4cd9ad0864` |  | U1: preregister the calibration reliability analysis, and buil… |
| 2026-08-22 | `89ec154db522` | `6ad87420cd52` |  | Merge pull request #66 from DebalekhaChakraborty/docs/handbook… |
| 2026-08-22 | `7f44dab9e8fd` | `49c49e388dc7` |  | Merge pull request #67 from DebalekhaChakraborty/docs/track-re… |
| 2026-08-22 | `fac743fe4d77` | `796d6493a3b4` |  | Merge pull request #68 from DebalekhaChakraborty/docs/correct-… |
| 2026-08-22 | `8898772370aa` | `770bbb370023` |  | Merge pull request #69 from DebalekhaChakraborty/fix/stale-fir… |
| 2026-08-22 | `4018435b4493` | `5f6162272a61` | **yes** | Merge pull request #70 from DebalekhaChakraborty/t2/paired-sub… |
| 2026-08-22 | `4faaf131315f` | `fe8f54eccf75` | **yes** | T2: arm-comparison report — the first read of outer-validation… |
| 2026-08-22 | `1b36bcf269a9` | `08477ab74b78` |  | W1: preregister the window-only comparator, and build its arm |
| 2026-08-22 | `5c1da8ac7dd6` | `5303c4639fa0` | **yes** | T2: amend the analysis plan to report descriptively rather tha… |
| 2026-08-22 | `c0be2584804f` | `8fbaa5df9677` |  | Merge pull request #71 from DebalekhaChakraborty/u1/calibratio… |
| 2026-08-22 | `f998bf5e0797` | `8ddebb15c371` | **yes** | Merge pull request #73 from DebalekhaChakraborty/w1/window-com… |
| 2026-08-22 | `f06040bb3b30` | `b68497daea69` | **yes** | T2 report: state the interval's post-selection boundary, and r… |
| 2026-08-22 | `173c2a79439a` | `333b179ca91e` |  | W1: window-only comparator report — RQ4 answered, and two regi… |
| 2026-08-22 | `67a5e1aa4492` | `f1320629ef4d` |  | Merge pull request #72 from DebalekhaChakraborty/t2/arm-compar… |
| 2026-08-22 | `d29007fdd55d` | `bf7275ab742b` |  | Docs: external validation strategy — identify and audit, decid… |
| 2026-08-22 | `27f30ac9bd45` | `09038b72aa77` |  | Merge pull request #74 from DebalekhaChakraborty/w1/window-com… |
| 2026-08-22 | `3e7d1d00d146` | `48dead25c582` | **yes** | W1 report: renumber the trailing section, which collided at §5 |
| 2026-08-22 | `9cee11f767d9` | `a541a244cf81` | **yes** | Merge pull request #75 from DebalekhaChakraborty/docs/external… |
| 2026-08-22 | `286e076d8cf6` | `99e32d04979c` |  | W1 report: renumber the trailing section, which collided at §5 |
| 2026-08-22 | `4bdf18064a46` | `09049153a932` | **yes** | Merge pull request #76 from DebalekhaChakraborty/fix/w1-report… |
| 2026-08-22 | `ac20164cb630` | `70da0d427266` |  | U1 generator: record the commit the report was generated at |
| 2026-08-22 | `9700c0a0b7ec` | `75dc026c2b28` |  | U1 generator: implement the parts of the plan it had left out |
| 2026-08-22 | `de4ccf7d1325` | `c8790ce1b60b` | **yes** | U1 generator: report the gap direction without implying false … |
| 2026-08-22 | `a8d257908c52` | `652c94c9e665` |  | Docs: bring README, IMPLEMENTATION_PLAN and REPO_AUDIT up to m… |
| 2026-08-22 | `473fb3ca5a4a` | `3cd0be43e99f` |  | U1: per-bin calibration reliability report -- the first read |
| 2026-08-22 | `eb3de5c972fe` | `9579329be49c` | **yes** | Merge pull request #77 from DebalekhaChakraborty/docs/refresh-… |
| 2026-08-22 | `d5a86ce0a257` | `ce984c94730b` | **yes** | Merge pull request #78 from DebalekhaChakraborty/u1/calibratio… |
| 2026-08-22 | `af5eb5fb2bf4` | `7af4d2e5ac7d` |  | Docs: Research Execution Handbook v1.3, a revision of v1.2 |
| 2026-08-22 | `3c25d3069a30` | `8de4f0d9d4cb` |  | Docs: Research Baseline v1.0 — architecture map and experiment… |
| 2026-08-23 | `0105c309f485` | `880ec3939bf7` |  | Handbook v1.3: promote the three denominator caveats to a find… |
| 2026-08-23 | `6c54e3cbf2f6` | `4bcabbdef509` |  | Docs: Research Baseline v1.0 — CURRENT_STATE refresh, and defe… |
| 2026-08-23 | `7485de9b284f` | `9b3bf28c93a2` |  | Handbook v1.3: date the revision the day it lands |
| 2026-08-23 | `7620434f0a83` | `14d86b50585e` |  | Docs: evidence map and paper outline |
| 2026-08-23 | `c12285c969e9` | `7f001d029d43` |  | Paper outline: price the apparatus in 9.5 instead of counting … |
| 2026-08-23 | `f64f0ba51faa` | `b09976838da1` |  | Merge pull request #79 from DebalekhaChakraborty/docs/handbook… |
| 2026-08-23 | `1698d3f22e8f` | `bf0c7f495cdc` |  | Merge pull request #80 from DebalekhaChakraborty/docs/research… |
| 2026-08-23 | `eee77af9c033` | `825fef62660b` |  | Merge pull request #81 from DebalekhaChakraborty/docs/evidence… |
| 2026-08-23 | `51b818aa9bf8` | `e87d9f1e54d4` |  | Edge: the representation bridge, and proof that it reproduces … |
| 2026-08-23 | `1016d04141c8` | `ac099a7f62c2` |  | Merge pull request #82 from DebalekhaChakraborty/edge/runtime-… |
| 2026-08-23 | `381ac7811128` | `b6865811230e` |  | Edge: the streaming inference session, from ECG chunk to alert |
| 2026-08-23 | `7f3e2da9a7b7` | `1f7359721350` |  | Merge pull request #83 from DebalekhaChakraborty/edge/runtime-… |
| 2026-08-23 | `a45dd9b28f38` | `452c67fb7695` |  | Agents: Evidence Agent foundation, and the claim boundary as c… |
| 2026-08-23 | `5a13c8d4b404` | `0e3a5cec32b6` |  | Merge pull request #84 from DebalekhaChakraborty/agents/eviden… |
| 2026-08-23 | `f79a23c7b452` | `0e8b2edfaf5f` |  | Agents: the evidence graph -- provenance you traverse instead … |
| 2026-08-23 | `f5b4f34cc614` | `5534a07d965b` |  | Merge pull request #85 from DebalekhaChakraborty/agents/eviden… |
| 2026-08-23 | `20a86ce3f0fe` | `26100c971cba` |  | Agents: Patient Explanation Agent -- language over evidence, n… |
| 2026-08-23 | `577c77de5f16` | `d0af27905c7f` |  | Merge pull request #86 from DebalekhaChakraborty/agents/patien… |
| 2026-08-23 | `762e1d74b08b` | `851bc7a64ff3` |  | Agents: Evidence-Grounded Research Assistant -- retrieval over… |
| 2026-08-23 | `fb758ddbf8a7` | `05f28d2e16fe` | **yes** | Merge pull request #87 from DebalekhaChakraborty/agents/resear… |
| 2026-08-23 | `b17a696f6803` | `b5f14a25b114` |  | Docs: Research Execution Handbook v1.4 -- the system stops bei… |
| 2026-08-23 | `9f38f478cde9` | `a491cfaf78d9` | **yes** | Merge pull request #88 from DebalekhaChakraborty/docs/handbook… |
| 2026-08-23 | `d7785a4b29cd` | `d0a5d01b26e3` |  | Docs: align the repository with the IPS runtime, and fix an RQ… |
| 2026-08-23 | `475e73a4f304` | `7699d9f5f295` |  | Merge pull request #89 from DebalekhaChakraborty/docs/ips-alig… |
| 2026-08-23 | `c27c0fddeeaf` | `eb56b1be8738` |  | Reproducibility: a committed 1.63 MiB demo bundle a reviewer c… |
| 2026-08-23 | `bb1a4137a913` | `e53101f47582` |  | Merge pull request #90 from DebalekhaChakraborty/docs/reproduc… |
| 2026-08-23 | `4628a9badfbb` | `5b997f25338f` |  | Reproducibility: prove the bundle WORKS, not only that it is i… |
| 2026-08-23 | `f8fce362a214` | `da8d6cb56f8c` | **yes** | Reproducibility: prove the bundle WORKS, not only that it is i… |
| 2026-08-23 | `32e43b3d2f7a` | `73a034e226bf` |  | Merge pull request #91 from DebalekhaChakraborty/tests/reprodu… |
| 2026-08-23 | `1dbb1e432d6b` | `02646f2f81f0` |  | Agents: Architecture Selection Intelligence -- lifecycle, not … |
| 2026-08-23 | `bf10213d4551` | `ca3dbfd1e09f` |  | Merge pull request #92 from DebalekhaChakraborty/agents/archit… |
| 2026-08-23 | `647cd86b6ed9` | `d62a8d417be1` |  | Edge: the IPS demonstration console, contracted before it was … |
| 2026-08-24 | `bd361f73a779` | `01e9499a140e` | **yes** | Merge pull request #93 from DebalekhaChakraborty/edge/demonstr… |
| 2026-08-24 | `95ccc351fde2` | `d578e258a155` | **yes** | Agents: Evidence-Constrained Explanation Evaluation framework |
| 2026-08-24 | `a8f1b472a18f` | `ff382d5176a1` | **yes** | Merge pull request #94 from DebalekhaChakraborty/agents/explan… |
| 2026-08-24 | `d891a1ac05ae` | `72344983048e` |  | Docs: paper outline V2, and correct §53.2's undercount of its … |
| 2026-08-24 | `54835ee7bb5a` | `7a3eb3475295` |  | Provenance: correct a tracked-generator digest that was stale … |
| 2026-08-24 | `13e153a8f87e` | `060302bc56f2` |  | Merge pull request #95 from DebalekhaChakraborty/docs/paper-ou… |
| 2026-08-24 | `0fc7f524d37a` | `adb67843aa3a` |  | Merge pull request #96 from DebalekhaChakraborty/docs/generato… |
| 2026-08-24 | `5bc31a5f277c` | `288e9166fdfa` |  | Docs: synchronise CURRENT_STATE.md and ARCHITECTURE.md with ma… |
| 2026-08-24 | `0480b34c9c3e` | `544581e6813e` | **yes** | Merge pull request #97 from DebalekhaChakraborty/docs/repo-sta… |
| 2026-08-24 | `7a9e5fff588e` | `c16c5510503d` |  | Docs: synchronise every living document with master 0480b34 |
| 2026-08-24 | `be70d656f24c` | `f5e9a0912b09` | **yes** | Merge pull request #98 from DebalekhaChakraborty/docs/state-sy… |
| 2026-08-24 | `f481d7419a5f` | `35165b9f1a81` |  | Docs: rewrite the README for readers arriving from the manuscr… |
| 2026-08-24 | `a1a8dc50eefe` | `312e882f6bf5` |  | Preservation: the S3 evidence mirror is verified again, 2026-0… |
| 2026-08-24 | `323bd85db628` | `2950c975320c` |  | Legacy: rename college-v1 to v0, and finish what the rename le… |
| 2026-08-24 | `f9e8a5a7e429` | `82b6c02e0bf1` |  | Handoffs: track the session chain in the repository |
| 2026-08-24 | `54299fe643eb` | `30a902f083e9` |  | Merge pull request #99 from DebalekhaChakraborty/docs/readme-f… |
| 2026-08-24 | `05efc23671b3` | `7f6dfbb6a45f` |  | Merge pull request #100 from DebalekhaChakraborty/docs/track-s… |
| 2026-08-24 | `02102a374e45` | `ae0f5d48eb88` |  | Docs: the legacy archive tag is legacy/v0, matching its direct… |
| 2026-08-24 | `824df84f0c20` | `97927d2cb52f` |  | Handoff: the remote is DebalekhaChakraborty/CardioSentinel, an… |
| 2026-08-24 | `ceb339be2d81` | `0fc999ea7930` |  | README: Project evolution, in the author's own voice |

---

## 5. Reverse index — new → old

For a reader holding a current SHA who needs to find which record cites it.
Sorted by new SHA.

| New SHA | Old SHA | Date |
|---|---|---|
| `01291bc8cfc7` | `2620da3eec31` | 2026-08-19 |
| `019c85120f94` | `917cb1eb34ca` | 2026-08-10 |
| `01e9499a140e` | `bd361f73a779` | 2026-08-24 |
| `02646f2f81f0` | `1dbb1e432d6b` | 2026-08-23 |
| `0462d2bb23ba` | `e6a2368e2257` | 2026-08-13 |
| `05f28d2e16fe` | `fb758ddbf8a7` | 2026-08-23 |
| `060302bc56f2` | `13e153a8f87e` | 2026-08-24 |
| `0625cead0374` | `0ec0999d6cf9` | 2026-08-22 |
| `067b75e1cf4d` | `1aece7f26a51` | 2026-08-13 |
| `082b2b8c83a0` | `ea2a3632866e` | 2026-08-14 |
| `08477ab74b78` | `1b36bcf269a9` | 2026-08-22 |
| `09038b72aa77` | `27f30ac9bd45` | 2026-08-22 |
| `09049153a932` | `4bdf18064a46` | 2026-08-22 |
| `0961ce387756` | `de47be9e8b70` | 2026-08-21 |
| `0a69daa3ae2c` | `c538181eb938` | 2026-08-21 |
| `0aa30d5b6edb` | `0aa30d5b6edb` | 2026-08-07 |
| `0cc4925eeab0` | `62b56c312518` | 2026-08-19 |
| `0cec1e271850` | `26fdbdb34500` | 2026-08-13 |
| `0d78058cbb77` | `a3f535bb081b` | 2026-08-22 |
| `0e3a5cec32b6` | `5a13c8d4b404` | 2026-08-23 |
| `0e7a9d9b387c` | `b3004da9dcd8` | 2026-08-19 |
| `0e8b2edfaf5f` | `f79a23c7b452` | 2026-08-23 |
| `0f059ad2f2e0` | `0f059ad2f2e0` | 2026-08-07 |
| `0fc999ea7930` | `ceb339be2d81` | 2026-08-24 |
| `111bea4467e6` | `3c4584e53280` | 2026-08-17 |
| `1151d5f29417` | `08152c87fe70` | 2026-08-22 |
| `12a7e8972e7e` | `cdc33797c3b7` | 2026-08-14 |
| `148076820624` | `2a5e83e14526` | 2026-08-21 |
| `14d86b50585e` | `7620434f0a83` | 2026-08-23 |
| `184646218ef1` | `184646218ef1` | 2026-08-07 |
| `1c0451e270fe` | `1c0451e270fe` | 2020-06-27 |
| `1e58ac116f0e` | `32aae59a56ec` | 2026-08-16 |
| `1ed115da5712` | `5804e66668dd` | 2026-08-21 |
| `1f63261170c2` | `1bbbd4702009` | 2026-08-22 |
| `1f7359721350` | `7f3e2da9a7b7` | 2026-08-23 |
| `1f803f394947` | `1f803f394947` | 2026-08-06 |
| `2038104a690f` | `7e5896a48d8f` | 2026-08-13 |
| `20ed000c87b3` | `bc46fca6b903` | 2026-08-19 |
| `22b6c2a9ae3c` | `a888b13380f2` | 2026-08-22 |
| `23450db9a12d` | `23450db9a12d` | 2020-06-25 |
| `23500c3ed15e` | `27c246247f91` | 2026-08-12 |
| `2383e33ac64d` | `2383e33ac64d` | 2020-06-25 |
| `23924c55af70` | `1ff85cdbd8d5` | 2026-08-19 |
| `23d642febb34` | `cf55d9f4ee6d` | 2026-08-13 |
| `24acff5210cf` | `24acff5210cf` | 2026-08-06 |
| `26100c971cba` | `20a86ce3f0fe` | 2026-08-23 |
| `288e9166fdfa` | `5bc31a5f277c` | 2026-08-24 |
| `2950c975320c` | `323bd85db628` | 2026-08-24 |
| `2ad3f3535192` | `8db30ffc8800` | 2026-08-21 |
| `2b4cd9ad0864` | `3684ca1ab68e` | 2026-08-22 |
| `2c931cfa397e` | `ea2784659e08` | 2026-08-07 |
| `2cc8baaa7545` | `2cc8baaa7545` | 2026-08-06 |
| `2d395e1c1e39` | `1e6f0da8c83d` | 2026-08-10 |
| `2e10d6771b9b` | `67422912496f` | 2026-08-22 |
| `2f2f532d47cb` | `7eb3579cc258` | 2026-08-22 |
| `2f5bfbeff630` | `2f5bfbeff630` | 2026-08-07 |
| `301d4bd6ca55` | `301d4bd6ca55` | 2026-08-07 |
| `30774c7c52fb` | `fa57bcfb3440` | 2026-08-22 |
| `30a840a14473` | `80a1466c7d6c` | 2026-08-11 |
| `30a902f083e9` | `54299fe643eb` | 2026-08-24 |
| `30d546eb0e2a` | `a8784053e4ed` | 2026-08-22 |
| `3111f4e186f2` | `3111f4e186f2` | 2020-06-25 |
| `3122ab03c2c9` | `eae3cda029a6` | 2026-08-22 |
| `312e882f6bf5` | `a1a8dc50eefe` | 2026-08-24 |
| `315fcace71dc` | `82a9cff6a778` | 2026-08-13 |
| `3171540cf989` | `fc7ac01a2758` | 2026-08-08 |
| `31f4c17ac77b` | `b779926c3eac` | 2026-08-22 |
| `32a5124552a2` | `467272220ea4` | 2026-08-22 |
| `33002b07dcfb` | `0c202795a7a0` | 2026-08-10 |
| `333b179ca91e` | `173c2a79439a` | 2026-08-22 |
| `35165b9f1a81` | `f481d7419a5f` | 2026-08-24 |
| `35e803c675b1` | `35e803c675b1` | 2020-06-25 |
| `387f8351ce70` | `387f8351ce70` | 2026-08-07 |
| `39c88a6a8d7a` | `724299555741` | 2026-08-20 |
| `39fb6cc863b9` | `3fd41927dc7c` | 2026-08-10 |
| `3a718b379355` | `9b5027522c37` | 2026-08-10 |
| `3bbff123326b` | `3bbff123326b` | 2020-06-25 |
| `3c10f4e7e356` | `6937b49e493a` | 2026-08-21 |
| `3cd0be43e99f` | `473fb3ca5a4a` | 2026-08-22 |
| `3d6a3f2a0a08` | `3d6a3f2a0a08` | 2020-06-25 |
| `3f52dfe12362` | `8268587994f0` | 2026-08-13 |
| `3fa20b634e18` | `d2bd34de2c2c` | 2026-08-21 |
| `43e2c082e117` | `68478afc1689` | 2026-08-21 |
| `44fc30bcc911` | `cb34ca08745c` | 2026-08-17 |
| `452c67fb7695` | `a45dd9b28f38` | 2026-08-23 |
| `45b21c733dcf` | `45b21c733dcf` | 2020-06-25 |
| `463f6da8be16` | `8e7c773f072f` | 2026-08-13 |
| `46e9fe3d34ab` | `83238686d7aa` | 2026-08-13 |
| `475d58aa2dd8` | `475d58aa2dd8` | 2020-06-25 |
| `483f8eefa654` | `483f8eefa654` | 2020-06-25 |
| `4891f5171519` | `4891f5171519` | 2020-06-25 |
| `48b0305a683b` | `e7ee78ea8d44` | 2026-08-10 |
| `48dead25c582` | `3e7d1d00d146` | 2026-08-22 |
| `48f4aab504ec` | `8de65aca300a` | 2026-08-13 |
| `49c49e388dc7` | `7f44dab9e8fd` | 2026-08-22 |
| `4a2363dc1be9` | `598e6c363b38` | 2026-08-08 |
| `4aa71e7d863b` | `c99c8a85a22d` | 2026-08-22 |
| `4b20a284aac9` | `4b20a284aac9` | 2026-08-07 |
| `4bcabbdef509` | `6c54e3cbf2f6` | 2026-08-23 |
| `4d1d738c500c` | `4d1d738c500c` | 2026-08-06 |
| `4f57ba38d4df` | `4f57ba38d4df` | 2026-08-07 |
| `50338e22a85d` | `bbb78d8cbb5e` | 2026-08-21 |
| `51d1e8a22bee` | `997df407376e` | 2026-08-17 |
| `5303c4639fa0` | `5c1da8ac7dd6` | 2026-08-22 |
| `530da77621e5` | `3c1ba4ce87ad` | 2026-08-13 |
| `535a9a042f81` | `f91c417054c4` | 2026-08-21 |
| `53aebb171f04` | `f39021de60bb` | 2026-08-22 |
| `53b495144bfe` | `e246c84ac7bc` | 2026-08-13 |
| `544581e6813e` | `0480b34c9c3e` | 2026-08-24 |
| `5514a46f4c2f` | `139b5a40e979` | 2026-08-20 |
| `5534a07d965b` | `f5b4f34cc614` | 2026-08-23 |
| `5583dca8d400` | `5583dca8d400` | 2026-08-07 |
| `5751417e5b0b` | `2a75a90c5c2a` | 2026-08-08 |
| `586fb06a38a1` | `a185689f43e5` | 2026-08-10 |
| `5b997f25338f` | `4628a9badfbb` | 2026-08-23 |
| `5d3a29fd6ee0` | `8260b718ab23` | 2026-08-12 |
| `5dea66cc674b` | `5dea66cc674b` | 2026-08-07 |
| `5e1c8e7835a5` | `a54566699a8b` | 2026-08-21 |
| `5ee1733efce2` | `0e60c1d3584d` | 2026-08-13 |
| `5f6162272a61` | `4018435b4493` | 2026-08-22 |
| `5f66f6e48b24` | `5f66f6e48b24` | 2020-06-25 |
| `5fde651f8832` | `e5432761c71e` | 2026-08-22 |
| `5ff66ea1c7a0` | `f8abf535cdf7` | 2026-08-11 |
| `602b17c45ca4` | `4b8f087657fe` | 2026-08-08 |
| `6147811b6ce6` | `0223a5bf0826` | 2026-08-18 |
| `62c0d38f0027` | `48cf7d2b84a8` | 2026-08-21 |
| `6316a300f50d` | `3af94bfcb743` | 2026-08-13 |
| `645ca9e899e7` | `086161f6c3b0` | 2026-08-22 |
| `649eafb8b169` | `e1c2dc202e5e` | 2026-08-22 |
| `652c94c9e665` | `a8d257908c52` | 2026-08-22 |
| `653c96fe586d` | `a4001dfb3168` | 2026-08-10 |
| `679c46e7de6e` | `679c46e7de6e` | 2020-06-25 |
| `67b5ec8c5492` | `abfbdc562afb` | 2026-08-13 |
| `67e0615f6f32` | `f2b9268b6bd2` | 2026-08-08 |
| `6863f5f503e9` | `8956f2195e3c` | 2026-08-14 |
| `696e0080d1da` | `c06644f46b6a` | 2026-08-22 |
| `6a80c07f2152` | `36497d94097c` | 2026-08-19 |
| `6a964e6393d6` | `2feb76c2bc64` | 2026-08-20 |
| `6ad85039f5eb` | `a889f22cd4c7` | 2026-08-17 |
| `6ad87420cd52` | `89ec154db522` | 2026-08-22 |
| `6b60b47366e4` | `ec62302d761f` | 2026-08-22 |
| `6d42c8574c65` | `064fe5e06857` | 2026-08-21 |
| `6ea2df11af10` | `6ea2df11af10` | 2020-06-25 |
| `6f7f62455056` | `4cab34f18f45` | 2026-08-14 |
| `70da0d427266` | `ac20164cb630` | 2026-08-22 |
| `70dfc24516ea` | `951503ea6439` | 2026-08-19 |
| `72344983048e` | `d891a1ac05ae` | 2026-08-24 |
| `72e1a1cf97ca` | `8455e748cfb0` | 2026-08-08 |
| `73600ae338db` | `d39bcf53c102` | 2026-08-17 |
| `73a034e226bf` | `32e43b3d2f7a` | 2026-08-23 |
| `74321a88c1f7` | `d6af68d61931` | 2026-08-10 |
| `752148e5ceef` | `510eea036da6` | 2026-08-12 |
| `759ad4d5d83d` | `9fa7e88ee648` | 2026-08-20 |
| `75dc026c2b28` | `9700c0a0b7ec` | 2026-08-22 |
| `7699d9f5f295` | `475e73a4f304` | 2026-08-23 |
| `770bbb370023` | `8898772370aa` | 2026-08-22 |
| `7760d012e07e` | `251bcb7a74dc` | 2026-08-13 |
| `7828db772b69` | `233a474aca14` | 2026-08-17 |
| `790637bfa36b` | `34abdc8beb69` | 2026-08-21 |
| `796d6493a3b4` | `fac743fe4d77` | 2026-08-22 |
| `7a3eb3475295` | `54835ee7bb5a` | 2026-08-24 |
| `7a7dbcee4c90` | `c578f21867be` | 2026-08-21 |
| `7a9d3e26ba71` | `bbefa385b7d1` | 2026-08-21 |
| `7af4d2e5ac7d` | `af5eb5fb2bf4` | 2026-08-22 |
| `7cfe77095e4a` | `fcb5ebb14ae3` | 2026-08-13 |
| `7edebe382b75` | `5a84b382bebb` | 2026-08-18 |
| `7f001d029d43` | `c12285c969e9` | 2026-08-23 |
| `7f6dfbb6a45f` | `05efc23671b3` | 2026-08-24 |
| `80fe6e813bfd` | `efdb5a2e9f24` | 2026-08-17 |
| `825fef62660b` | `eee77af9c033` | 2026-08-23 |
| `828e34f318ea` | `2f379c75503d` | 2026-08-08 |
| `8299d43e13a7` | `60855531ea24` | 2026-08-12 |
| `82b6c02e0bf1` | `f9e8a5a7e429` | 2026-08-24 |
| `8325aec47ff9` | `566b955bd660` | 2026-08-10 |
| `8410080c3bdc` | `88e793399961` | 2026-08-12 |
| `851bc7a64ff3` | `762e1d74b08b` | 2026-08-23 |
| `85cfa2056c69` | `85cfa2056c69` | 2026-08-07 |
| `86b4bdfcba02` | `86b4bdfcba02` | 2026-08-07 |
| `87b5d39d9103` | `87b5d39d9103` | 2026-08-07 |
| `880ec3939bf7` | `0105c309f485` | 2026-08-23 |
| `8916668ef849` | `f4759e2a97d1` | 2026-08-19 |
| `89a9af8294c0` | `ba20fc94465a` | 2026-08-14 |
| `8ccce22a4641` | `9c9c631dcd7a` | 2026-08-08 |
| `8d2dd0bf18c7` | `8d2dd0bf18c7` | 2020-06-25 |
| `8d62f4e7c64b` | `b27d528c7851` | 2026-08-08 |
| `8ddebb15c371` | `f998bf5e0797` | 2026-08-22 |
| `8de4f0d9d4cb` | `3c25d3069a30` | 2026-08-22 |
| `8e2af81c8e81` | `74df6cc3f2cd` | 2026-08-14 |
| `8f488dcd23d9` | `8f488dcd23d9` | 2026-08-07 |
| `8fbaa5df9677` | `c0be2584804f` | 2026-08-22 |
| `91bece082be5` | `b6ccb8e80ee7` | 2026-08-08 |
| `926d2ef11243` | `a0b2e198885c` | 2026-08-22 |
| `95767ef72e02` | `8c1b1e02a6c5` | 2026-08-21 |
| `9579329be49c` | `eb3de5c972fe` | 2026-08-22 |
| `97927d2cb52f` | `824df84f0c20` | 2026-08-24 |
| `98d2b0f7e036` | `98d2b0f7e036` | 2020-06-25 |
| `9959e650ab54` | `8a0132c1c9e5` | 2026-08-22 |
| `99b13064c2f6` | `03647df18219` | 2026-08-10 |
| `99e32d04979c` | `286e076d8cf6` | 2026-08-22 |
| `9a1715c325bc` | `9a1715c325bc` | 2026-08-07 |
| `9b3bf28c93a2` | `7485de9b284f` | 2026-08-23 |
| `9c77902b3f43` | `eb89ed1438f4` | 2026-08-10 |
| `9c8ac4697b93` | `9c8ac4697b93` | 2026-08-07 |
| `9cf120d195cb` | `76e35d496822` | 2026-08-22 |
| `9d38a8fe7219` | `95254b773830` | 2026-08-21 |
| `a0344cc8ffd6` | `6e272ff61598` | 2026-08-13 |
| `a059d6ca81f1` | `0639c9e20a58` | 2026-08-21 |
| `a089a601b07f` | `c975ce709c2c` | 2026-08-18 |
| `a178a5b00160` | `d77fbdc37415` | 2026-08-14 |
| `a415074c8a53` | `9ed8fc930740` | 2026-08-08 |
| `a491cfaf78d9` | `9f38f478cde9` | 2026-08-23 |
| `a4e71e287e7f` | `a4e71e287e7f` | 2026-08-06 |
| `a541a244cf81` | `9cee11f767d9` | 2026-08-22 |
| `a600c7ee4f82` | `a600c7ee4f82` | 2026-08-07 |
| `a6cc4e034652` | `36eb54aa1d09` | 2026-08-22 |
| `aa0ede8ebd70` | `4e1dbd0171a6` | 2026-08-11 |
| `aa2313c6dfa9` | `fb89ae5fe874` | 2026-08-21 |
| `ab1dc3d8261b` | `ec438468446c` | 2026-08-22 |
| `ac099a7f62c2` | `1016d04141c8` | 2026-08-23 |
| `ac72487a8e0a` | `e72c93ae4a6c` | 2026-08-21 |
| `ad02266bb691` | `ad02266bb691` | 2026-08-07 |
| `adb67843aa3a` | `0fc7f524d37a` | 2026-08-24 |
| `ae0f5d48eb88` | `02102a374e45` | 2026-08-24 |
| `ae19fd467e8f` | `16c96f613501` | 2026-08-22 |
| `aea59d2fa44e` | `7544ad0eb07e` | 2026-08-20 |
| `af0eca0dd9b9` | `8179091a72d3` | 2026-08-10 |
| `b01c16315542` | `ab15137fe8ba` | 2026-08-08 |
| `b0984630dbf7` | `64d5fc91c225` | 2026-08-21 |
| `b09976838da1` | `f64f0ba51faa` | 2026-08-23 |
| `b19e93d5aa67` | `b19e93d5aa67` | 2026-08-07 |
| `b4f0d20d8332` | `8ed90c631716` | 2026-08-22 |
| `b54d4f9f9650` | `229fb6ecda98` | 2026-08-10 |
| `b5f14a25b114` | `b17a696f6803` | 2026-08-23 |
| `b63f082d5141` | `b63f082d5141` | 2020-06-25 |
| `b68497daea69` | `f06040bb3b30` | 2026-08-22 |
| `b6865811230e` | `381ac7811128` | 2026-08-23 |
| `b79d3553b298` | `6e675e8a7ead` | 2026-08-13 |
| `b83b08b1543e` | `61ad0b6d49b8` | 2026-08-21 |
| `b8fdc63c5144` | `c3374044b2f3` | 2026-08-22 |
| `b8ffae576f4d` | `bd61c1413456` | 2026-08-22 |
| `b92db8d78c93` | `7a9f92edf3d8` | 2026-08-21 |
| `baf5260236ff` | `64dcc14dac53` | 2026-08-10 |
| `bc15e4ee7674` | `7e02c22d29bb` | 2026-08-10 |
| `bcba9b00aaea` | `3ce81f41c22b` | 2026-08-08 |
| `be6ccd2590b6` | `854317757429` | 2026-08-22 |
| `bee594f5bff8` | `f30350d6322f` | 2026-08-20 |
| `bf0c7f495cdc` | `1698d3f22e8f` | 2026-08-23 |
| `bf5566e18209` | `bf5566e18209` | 2026-08-07 |
| `bf7275ab742b` | `d29007fdd55d` | 2026-08-22 |
| `bfd32281a651` | `2672a723f2c5` | 2026-08-20 |
| `c16c5510503d` | `7a9e5fff588e` | 2026-08-24 |
| `c20baa31be1a` | `f7dd23946718` | 2026-08-13 |
| `c2af2662fe25` | `c2af2662fe25` | 2020-06-25 |
| `c3ca4d98f087` | `c87be5dbcc40` | 2026-08-21 |
| `c4eb9e2862fb` | `3d03fa6cce7b` | 2026-08-08 |
| `c5c3942da97a` | `c5c3942da97a` | 2020-06-25 |
| `c61bb6e3f8fb` | `80b4b3995983` | 2026-08-12 |
| `c752e1a4f674` | `74f4c94ae2e9` | 2026-08-21 |
| `c8463ef68f35` | `9e16e328555f` | 2026-08-21 |
| `c8790ce1b60b` | `de4ccf7d1325` | 2026-08-22 |
| `ca0c3728a60d` | `ca0c3728a60d` | 2020-06-25 |
| `ca3dbfd1e09f` | `bf10213d4551` | 2026-08-23 |
| `cd24de69fea2` | `3c8d43387111` | 2026-08-21 |
| `cdedb270c304` | `71c73617e880` | 2026-08-10 |
| `ce984c94730b` | `d5a86ce0a257` | 2026-08-22 |
| `d030cbc18527` | `166136c803b2` | 2026-08-21 |
| `d0a5d01b26e3` | `d7785a4b29cd` | 2026-08-23 |
| `d0af27905c7f` | `577c77de5f16` | 2026-08-23 |
| `d1b2e7e96e3d` | `61704aa7259d` | 2026-08-22 |
| `d25abca2ed85` | `d25abca2ed85` | 2020-06-25 |
| `d578e258a155` | `95ccc351fde2` | 2026-08-24 |
| `d62a8d417be1` | `647cd86b6ed9` | 2026-08-23 |
| `d638e4c770a7` | `8cf1cb03ca5d` | 2026-08-08 |
| `d6e8c3937c71` | `f1bf641fc54b` | 2026-08-08 |
| `d711303fe256` | `c7a458ab835c` | 2026-08-21 |
| `d8923caae2bf` | `90ad879f5e69` | 2026-08-10 |
| `d91b7716169b` | `64ff2673ec84` | 2026-08-19 |
| `da8d6cb56f8c` | `f8fce362a214` | 2026-08-23 |
| `dcb3913cf0f0` | `31c7e415e79b` | 2026-08-07 |
| `de1c7d1d9f24` | `51b95de59d9c` | 2026-08-10 |
| `df48d713f71e` | `39ede04a3aac` | 2026-08-22 |
| `e107082e45c0` | `b0f189a57bea` | 2026-08-19 |
| `e1479aa8b1b0` | `e1479aa8b1b0` | 2026-08-07 |
| `e24dcc812d7c` | `e24dcc812d7c` | 2020-06-25 |
| `e360914c61d2` | `05094d79874a` | 2026-08-22 |
| `e3647161727f` | `4dac065f43e8` | 2026-08-08 |
| `e3beee788797` | `431bd158b740` | 2026-08-18 |
| `e45cb3a47f7d` | `9a037356aa72` | 2026-08-22 |
| `e47e32f2a827` | `b202840bd58d` | 2026-08-21 |
| `e53101f47582` | `bb1a4137a913` | 2026-08-23 |
| `e67672648a0a` | `4d388bf45469` | 2026-08-14 |
| `e77f23712750` | `eb025dc24820` | 2026-08-14 |
| `e7e06b31da19` | `02f1ee41fe36` | 2026-08-16 |
| `e812ce7dd683` | `1feff5972ffb` | 2026-08-22 |
| `e87d9f1e54d4` | `51b818aa9bf8` | 2026-08-23 |
| `e8ad07182ce3` | `c472fba6f822` | 2026-08-20 |
| `e964fd131534` | `e964fd131534` | 2026-08-07 |
| `ea14c4d41a99` | `32b505d27250` | 2026-08-13 |
| `ea9af1d27df7` | `16a82deae5da` | 2026-08-12 |
| `eab171343431` | `eab171343431` | 2026-08-06 |
| `eb56b1be8738` | `c27c0fddeeaf` | 2026-08-23 |
| `ebf6d6d87658` | `b79185f4c67f` | 2026-08-22 |
| `ec91545923bf` | `b40b4acac168` | 2026-08-22 |
| `ed5bb2872e57` | `e6f5dfeacd03` | 2026-08-21 |
| `ef27fee38734` | `ef27fee38734` | 2020-06-25 |
| `f1320629ef4d` | `67a5e1aa4492` | 2026-08-22 |
| `f341fe37ffc3` | `21a38ec5c081` | 2026-08-08 |
| `f342bbf5b57b` | `0229f3fdb626` | 2026-08-20 |
| `f5e9a0912b09` | `be70d656f24c` | 2026-08-24 |
| `f79a73ce5590` | `8eccdd9e0ad5` | 2026-08-19 |
| `f7ca017d1082` | `f7ca017d1082` | 2020-06-25 |
| `f884be1114ed` | `a8682e982c09` | 2026-08-21 |
| `f8aa0fbbb998` | `d7b2d425fa23` | 2026-08-22 |
| `f93047a0d167` | `f93047a0d167` | 2026-08-07 |
| `f982a7e51a60` | `25a6b5dcac5e` | 2026-08-22 |
| `f98e4b4a1798` | `b343bb506d04` | 2026-08-21 |
| `fa433ee2313a` | `fe7b8dc27895` | 2026-08-10 |
| `fac810ccb334` | `73358bc1469b` | 2026-08-22 |
| `fb07563e0da3` | `72e6bb3c5516` | 2026-08-13 |
| `fc2fff5d2e9d` | `3863384dc0c3` | 2026-08-22 |
| `fc829ee0da8f` | `fc829ee0da8f` | 2020-06-25 |
| `fd8787109b07` | `fd8787109b07` | 2020-06-25 |
| `fdf2748214e2` | `377995089314` | 2026-08-20 |
| `fe8f54eccf75` | `4faaf131315f` | 2026-08-22 |
| `ff382d5176a1` | `a8f1b472a18f` | 2026-08-24 |
| `ff41a786e0cc` | `c3237d1ec3e8` | 2026-08-22 |

---

## 6. Impact index

| Category | Files | Disposition |
|---|---|---|
| Frozen scientific record | 24 | **Never edited.** Translated here. |
| Generated artifact (immutable) | 3 | **Cannot be edited** — see §7. |
| Runtime provenance constant / test | 18 | **Not edited.** Inert strings; nothing resolves a commit at runtime. |
| Documentation pin | 26 | **Not edited** in this document. Editable in principle; see §8. |

**Frozen scientific record**

- `docs/M1_MEMORY_RETENTION_DECISION_V1.md`
- `docs/M2_CONTAMINATION_SAFE_MEMORY_PROTOCOL_V1.md`
- `docs/M2_DEVELOPMENT_ATTEMPT1_FAILURE_AND_RECOVERY_DECISION_V1.md`
- `docs/M2_DEVELOPMENT_EXECUTION_PROTOCOL_V1.md`
- `docs/M2_DEVELOPMENT_RECOVERY1_FAILURE_AND_RECOVERY2_DECISION_V1.md`
- `docs/M2_GATE_DERIVATION_RECEIPT_V1.json`
- `docs/M2_STRESS_INTERVAL_ELIGIBILITY_DECISION_V1.md`
- `docs/M2_TRAIN_ONLY_RECEIPT_CANONICALIZATION_V1.md`
- `docs/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md`
- `docs/PAPER_OUTLINE_V1.md`
- `docs/PAPER_OUTLINE_V2.md`
- `docs/T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md`
- `docs/T1_DESCRIPTIVE_REPORT_V1.md`
- `docs/T1_EVIDENCE_ANALYSIS_PLAN_V1.md`
- `docs/T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md`
- `docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md`
- `docs/T2_ARM_COMPARISON_REPORT_V1.md`
- `docs/T2_LONGITUDINAL_TEMPORAL_PROTOCOL_V1.md`
- `docs/T2_TRAIN_ARTIFACT_REVIEW_AND_OUTER_ACTIVATION_V1.md`
- `docs/U1_CALIBRATION_RELIABILITY_REPORT_V1.md`
- `docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`
- `docs/U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md`
- `docs/W1_WINDOW_COMPARATOR_REPORT_V1.md`
- `recovery/T1_FAILURE_RECEIPT_RECONSTRUCTED.json`

**Generated artifact (immutable)**

- `reproducibility/demo_bundle/runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json`
- `reproducibility/demo_bundle/runs/phase4-p1-physiology-v1/P1B_phys_fusion_v1/EXPERIMENT_LOCK.json`
- `reproducibility/demo_bundle/runs/phase5-m1-dual-memory-v2/M1L_long_memory_v2/EXPERIMENT_LOCK.json`

**Runtime provenance constant / test**

- `scripts/provenance/README.md`
- `scripts/provenance/gen_t1_descriptive_report.py`
- `src/cardiosentinel/neural/m2_development_run.py`
- `src/cardiosentinel/neural/t1_execution_spec.py`
- `src/cardiosentinel/neural/t1_protocol.py`
- `src/cardiosentinel/neural/t1_recovery_amendment.py`
- `src/cardiosentinel/neural/t2_persistence.py`
- `src/cardiosentinel/neural/t2_protocol.py`
- `src/cardiosentinel/neural/t2_selection.py`
- `src/cardiosentinel/neural/u1_selection.py`
- `tests/neural/data/m2_attempt1_frozen.json`
- `tests/neural/test_t1_continuation_persistence.py`
- `tests/neural/test_t1_execution_authorization.py`
- `tests/neural/test_t1_execution_spec.py`
- `tests/neural/test_t1_protocol.py`
- `tests/neural/test_t2_outer_validation_governance.py`
- `tests/neural/test_t2_protocol.py`
- `tests/neural/test_u1_selection.py`

**Documentation pin**

- `docs/ARCHITECTURE.md`
- `docs/CURRENT_STATE.md`
- `docs/CardioSentinel_Research_Execution_Handbook_v1.2.md`
- `docs/CardioSentinel_Research_Execution_Handbook_v1.3.md`
- `docs/CardioSentinel_Research_Execution_Handbook_v1.4.md`
- `docs/EXPERIMENT_CATALOGUE.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/M1_STAGE1_ATTEMPT1_FAILURE.md`
- `docs/M1_STAGE1_ATTEMPT2_FAILURE.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG10.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG11.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG12.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG13.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG14.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG15.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG16.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG17.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG3.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG4.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG5.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG6.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG7.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG8.md`
- `handoffs/CARDIOSENTINEL_HANDOFF_ECG9.md`
- `handoffs/README.md`
- `recovery/T1_CONTINUATION_PREAUTHORIZATION.md`

---

## 7. Immutable artifacts — why they are not corrected

Three committed `EXPERIMENT_LOCK.json` files carry a `git_sha` field that now
dangles. **They cannot be corrected**, and this is arithmetic rather than policy.

### 6.1 The self-referential digest convention

`experiment_lock_sha256` is the SHA-256 of the lock object **with the
`experiment_lock_sha256` field itself removed**, serialised canonically:

```python
hashlib.sha256(
    json.dumps({k: v for k, v in lock.items() if k != "experiment_lock_sha256"},
               sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
```

A digest cannot contain itself, so the field is excluded from its own input.
Verified against all three B4 candidates — the registered value, the value stored
inside the lock, and independent recomputation agree in every case:

| Candidate | Digest |
|---|---|
| B4-A `B4_raw_compact_cnn_v1` | `ea1e1d76…` |
| B4-B `B4B_cnn_transformer_v1` | `58e44a09…` |
| B4-C `B4C_cnn_ssm_v1` | `22ba491b…` |

### 6.2 Why correcting `git_sha` is impossible

Changing any field of a lock changes its digest by construction:

| Lock | dangling `git_sha` | current digest | digest if corrected |
|---|---|---|---|
| B4B_cnn_transformer_v1 | `b27d528c7851` | `58e44a09…` | `3b997e6ce72f…` |
| P1B_phys_fusion_v1 | `7e02c22d29bb` | — | `18f45e89828f…` |
| M1L_long_memory_v2 | `8260b718ab23` | — | `d34147e035fc…` |

B4-B's digest `58e44a09…` is registered in **28 files**, including
`P1_PHYSIOLOGY_FUSION_PROTOCOL_V1.md`, `M1_DUAL_MEMORY_PROTOCOL_V1.md`,
`M1_DUAL_MEMORY_PROTOCOL_V2.md`, and the P1A, P1B, M1D, M1L and M1S locks — each
of which carries its own self-referential digest that would then also move.
Correcting one `git_sha` invalidates a chain crossing four experiment
generations.

### 6.3 Frozen documents are sealed by reference

16 affected `docs/` records have their own SHA-256 registered in other tracked
files — `M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` in **20** of them. Editing any
of these to repair a pin would falsify every registration of its digest.

**Therefore: no referenced artifact is edited. Translation is the only
non-destructive repair.**

---

## 8. Scope limits

This document does **not** modify any frozen `_V1` record, experiment lock,
manifest, checkpoint, protocol digest, result artifact, or runtime constant. It
does not rewrite history, and it does not authorize anything.

Documentation pins and handoff records are editable in principle. They are left
unedited here so that this table remains the single source of truth for the
migration; correcting some references while others must stay would leave a
repository where a reader cannot tell which convention applies to the pin in
front of them.

---

## 9. Recovery provenance

The pre-rewrite history is preserved in three independent locations. **None may
be deleted, and `git gc --prune=now` must not be run**, until this table is
confirmed sufficient.

| Location | Contents |
|---|---|
| `refs/original/*` (local) | 9 refs, pre-rewrite master `ceb339b` and all pre-rewrite tags |
| `refs/local-backup/pre-coauthor-rewrite` (local) | pre-rewrite master `ceb339b` |
| `~/cardiosentinel-recovery/pre-coauthor-rewrite.bundle` | complete `--all` bundle, 5.5 MiB |

Bundle verification:

```
$ git bundle verify pre-coauthor-rewrite.bundle
ceb339be2d811b4cc98edd06c586b85fa2255998 HEAD
The bundle records a complete history.
```

Pre-rewrite master `ceb339b`, tree `dd89bf3752a8`. The post-rewrite master
carries the identical tree.
