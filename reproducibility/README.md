# Reproducing CardioSentinel

**Two tiers.** They ask for very different things, and conflating them is why
reproducibility packages get abandoned.

| | Demo tier | Research tier |
|---|---|---|
| Reproduces | the IPS demonstration: ECG → state → alert → evidence → explanation | the published scientific claims |
| Artifacts | **1.63 MiB, in this repository** (`demo_bundle/`) | ~24 GB, not distributed |
| Data | **one** PhysioNet record (~55 MB) | the LTSTDB cohort |
| Time | minutes | hours |
| Start at | [Run the demonstration](#run-the-demonstration) | [`EXPERIMENT_MAP.md`](EXPERIMENT_MAP.md) |

## Scope of the demo bundle

> This bundle exists only to reproduce the CardioSentinel IPS demonstration.
>
> It is **not** the complete research artifact archive, is **not** sufficient to
> reproduce all experiments, and does **not** replace the locked experiment
> stores. Full scientific validation requires the research tier.

## Run the demonstration

Four steps. Everything except the ECG record is already in this repository.

```bash
# 1. environment (detail: Environment, below)
python -m pip install -e ".[dev,signal,ml,neural]"

# 2. verify the bundle you are about to run
python reproducibility/verify_reproducibility.py

# 3. one ECG record (see Data access, below)
#    -> cardiosentinel-data/ltstdb/1.0.0/s20201.{dat,hea}

# 4. run it
cardiosentinel edge simulate s20201 --seconds 2400 \
  --run-root reproducibility/demo_bundle/runs \
  --feature-root reproducibility/demo_bundle/features
```

## What you should see

A live state stream (`.` NORMAL, `w` WATCH, `E` EVENT), then the contracted
40-minute outcome (wall time and real-time factor are machine-dependent):

```
  record            s20201 channel 0
  windows           479
  simulated ECG     40.0 min
  memory updates    0/479 admitted
  alerts            1
    EVENT 00:17:05 -> 00:27:45 [640 s] 129 windows, peak p_t 0.545613
```

Followed by the provenance of every frozen component that produced it.

**`memory updates 0/479` is correct, not a bug.** The contamination-safe gate
only admits windows that look normal and sit outside a 60-second refractory. A
blocked update is the control working.

## Then ask why

```bash
# the deterministic evidence path: gate conditions, measured values, provenance
cardiosentinel agent why s20201 --seconds 2400 \
  --run-root reproducibility/demo_bundle/runs \
  --feature-root reproducibility/demo_bundle/features

# the provenance graph, traversable
cardiosentinel agent graph s20201 --format lineage --of measurement:p_t \
  --run-root reproducibility/demo_bundle/runs \
  --feature-root reproducibility/demo_bundle/features

# research decisions, from curated evidence objects only
cardiosentinel agent research "Why was the selective router rejected?"

# the claim boundary, executable
cardiosentinel agent check-claims "S4D outperforms GRU"   # exits 1
```

## Expect the explanation to say DETERMINISTIC

Without a generative provider configured, the explanation agent falls back to a
template renderer and **declares that it did**:

```
[1/1]  mode=DETERMINISTIC  provider=template  source=EVIDENCE_GRAPH
  fell back because: no provider configured
```

That is the designed behaviour. The generator is a communication layer, not a
source of truth.

Generation is opt-in. `--provider local` uses only the pinned local cache;
there is no hosted fallback. `--provider gemini` explicitly selects a hosted
service and sends the structured evidence context off the local machine.
`GOOGLE_API_KEY` alone never selects it. `--no-generative` always keeps the
deterministic path.

## The same run, in a browser

`reproducibility/demo-ui/` renders this replay as a dashboard. It is a
presentation layer over the runtime above: no inference, no threshold, no state
machine, and no second detector in the browser.

```bash
# generate the snapshot -- the exporter checks the replay against the contracted
# demonstration above and writes nothing on a mismatch
python reproducibility/demo-ui/export_snapshot.py

# serve the repository root
python -m http.server 8081 --bind 0.0.0.0
#   -> http://localhost:8081/reproducibility/demo-ui/
```

Every value on screen is read from an `EdgeObservation`, an `AlertEvent`, an
`EvidenceRecord` or the existing agent output -- including the `0/479` admitted
memory updates and the `mode=DETERMINISTIC` explanation above.

It is not a clinical dashboard and not edge-hardware validation.
[`demo-ui/README.md`](demo-ui/README.md) carries the full contract, the
display-decimation semantics and the boundaries.

## Two records worth trying

| Record | What it shows |
|---|---|
| `s20201` | at the contracted 2400 seconds: one 640-second EVENT run |
| `s20591` | **zero alerts** — which reproduces the published result that subject s2059 has 47 reference episodes and 0 predicted runs |

A longer replay is a different scenario. Its output is not the 2400-second
contract above and is not predicted by this document.

## Environment

| | |
|---|---|
| Python | 3.12.6 |
| Packages | **335**, frozen |
| Digest | `installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` |

### Verify it, do not assume it

```bash
python -c "from cardiosentinel.neural.provenance import dependency_environment as d; print(d())"
```

**Verify with `dependency_environment()`, not a pip-freeze hash.** The digest is
computed over a normalised package snapshot; a freeze hash will not match and
its mismatch means nothing.

### Rules

- **Never install, upgrade or downgrade** anything in the scientific
  environment. Every experiment lock binds this digest; changing it detaches the
  artifacts from their provenance.
- **No generative-model SDK is a project dependency.** The agents' provider
  adapters import lazily and are skipped when absent, so the deterministic path
  is always available.

## Data access

### Demo tier — one record

The demonstration needs a single LTSTDB record. `s20201` is used throughout the
documentation because it raises two alerts within 90 simulated minutes.

```bash
# from PhysioNet, ~55 MB
wget -r -np -nH --cut-dirs=3 \
  https://physionet.org/files/ltstdb/1.0.0/s20201.dat \
  https://physionet.org/files/ltstdb/1.0.0/s20201.hea
```

Place under `cardiosentinel-data/ltstdb/1.0.0/`, or pass `--source-root`.

**Only the twelve validation subjects can be replayed.** T1 thresholds are
leave-one-subject-out; every other record has no validated operating point and
the runtime refuses it rather than borrowing another subject's thresholds.

```bash
cardiosentinel edge subjects   # lists them
```

### Research tier — the cohort

The full LTSTDB cohort, subject-disjoint 70/15/15, seed 2026. Integrity is
recorded in `cardiosentinel-data/ltstdb/1.0.0/source_verification.json`, which
carries `expected_record_count`, the official manifest digest and
`verified_required_file_count`.

### What no tier provides

**There is no independent cohort.** No drop-in external dataset exists in the
public record. EDB is a **secondary** cohort, partly contaminated with LTSTDB,
enforced in code by `validate_edb_secondary_evaluation_policy`, and **may never
be described as external**. See `docs/external-validation/EXTERNAL_VALIDATION_STRATEGY_V1.md`.

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
