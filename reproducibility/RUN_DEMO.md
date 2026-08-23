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

A live state stream (`.` NORMAL, `w` WATCH, `E` EVENT), then:

```
  record            s20201 channel 0
  windows           1079
  simulated ECG     90.0 min in 89.1 s wall (61x real time)
  memory updates    0/1079 admitted
  alerts            2
    EVENT 00:17:05 -> 00:27:45 [640 s] 129 windows, peak p_t 0.5456
```

Followed by the provenance of every frozen component that produced it.

**`memory updates 0/1079` is correct, not a bug.** The contamination-safe gate
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

## Two records worth trying

| Record | What it shows |
|---|---|
| `s20201` | two EVENT runs, one still open at end of stream |
| `s20591` | **zero alerts** — which reproduces the published result that subject s2059 has 47 reference episodes and 0 predicted runs |
