# Run the demonstration

Four steps. Everything except the ECG record is already in this repository.

```bash
# 1. environment
python -m pip install -e ".[dev,signal,ml,neural]"

# 2. verify the bundle you are about to run
python reproducibility/verify_reproducibility.py

# 3. one ECG record (see DATA_ACCESS.md)
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

## Two records worth trying

| Record | What it shows |
|---|---|
| `s20201` | at the contracted 2400 seconds: one 640-second EVENT run |
| `s20591` | **zero alerts** — which reproduces the published result that subject s2059 has 47 reference episodes and 0 predicted runs |

A longer replay is a different scenario. Its output is not the 2400-second
contract above and is not predicted by this document.
