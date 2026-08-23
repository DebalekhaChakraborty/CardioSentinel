# Data access

## Demo tier — one record

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

## Research tier — the cohort

The full LTSTDB cohort, subject-disjoint 70/15/15, seed 2026. Integrity is
recorded in `cardiosentinel-data/ltstdb/1.0.0/source_verification.json`, which
carries `expected_record_count`, the official manifest digest and
`verified_required_file_count`.

## What no tier provides

**There is no independent cohort.** No drop-in external dataset exists in the
public record. EDB is a **secondary** cohort, partly contaminated with LTSTDB,
enforced in code by `validate_edb_secondary_evaluation_policy`, and **may never
be described as external**. See `docs/EXTERNAL_VALIDATION_STRATEGY_V1.md`.
