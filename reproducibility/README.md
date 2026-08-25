# Reproducing CardioSentinel

**Two tiers.** They ask for very different things, and conflating them is why
reproducibility packages get abandoned.

| | Demo tier | Research tier |
|---|---|---|
| Reproduces | the IPS demonstration: ECG → state → alert → evidence → explanation | the published scientific claims |
| Artifacts | **1.63 MiB, in this repository** (`demo_bundle/`) | ~24 GB, not distributed |
| Data | **one** PhysioNet record (~55 MB) | the LTSTDB cohort |
| Time | minutes | hours |
| Start at | [`RUN_DEMO.md`](RUN_DEMO.md) | [`EXPERIMENT_MAP.md`](EXPERIMENT_MAP.md) |

## Scope of the demo bundle

> This bundle exists only to reproduce the CardioSentinel IPS demonstration.
>
> It is **not** the complete research artifact archive, is **not** sufficient to
> reproduce all experiments, and does **not** replace the locked experiment
> stores. Full scientific validation requires the research tier.

## What is deliberately not a dependency

**No external mirror is required.** Evidence preservation uses cryptographic
manifests; external mirrors are optional and their availability is not required
to reproduce anything here. An S3 mirror exists and was **verified 2026-08-24**
(`CHECKSUM_MANIFEST.md` carries the detail), but nothing in this package depends
on it, and a reproducibility claim that depended on something unverifiable would
not be one.

**No generative-model API.** The explanation agent falls back to a deterministic
renderer and labels the mode. No API key is needed.

**No sealed test access.** The B4 neural sealed test was consumed on 2026-08-25,
and **no path in this package touches it, reads it, or reproduces it.** Nothing
here is derived from the test partition: the demo bundle carries development
artifacts only, and the scenario replays a validation record. The sealed-test
artifacts live under `cardiosentinel-runs/` — gitignored, not distributed, and
immutable. A reader of this package cannot reproduce the sealed-test number and
is not being invited to try; **the one-shot result is a claim you check against
its audit receipt, not one you re-run.**

## Verify before you trust

```bash
python reproducibility/verify_reproducibility.py
```

Checks every bundled file against `DEMO_BUNDLE_SELECTION.json`, refuses
unselected files, and exits non-zero on any drift. Run in CI on every push.
