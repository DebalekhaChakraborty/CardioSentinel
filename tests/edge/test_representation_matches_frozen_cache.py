"""The test the whole edge runtime rests on.

**Claim under test:** a representation computed live from an LTSTDB waveform
reproduces the corresponding row of the frozen M1 stream-memory corpus that
every retained model was developed against.

If it does not, the edge runtime is a *different system wearing the validated
system's results*, and no downstream alert may cite the research evidence. That
is why this test exists before the streaming session, the alert layer, or any
agent that would explain an alert.

**Why this skips in CI, and why the skip is loud.** `cardiosentinel-runs/`,
`cardiosentinel-features/` and `cardiosentinel-data/` are gitignored, so a fresh
checkout cannot run this. That is the same asymmetry that once let thirteen
tests pass in CI while failing on every machine holding the evidence -- so the
skip reason names the missing tree explicitly rather than skipping quietly.

**Tolerance, and why it is not exact.** The physiology half is bit-exact: the
same 18 morphology features, through the same frozen transform. The embedding
half agrees to a few float32 ULP, because CPU convolution and attention kernels
do not guarantee a fixed reduction order across runs. The bound below is
asserted in ULP rather than as a bare float so the number stays interpretable.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = REPOSITORY_ROOT / "cardiosentinel-runs"
CORPUS = (
    REPOSITORY_ROOT
    / "cardiosentinel-features"
    / "m1-stream-memory-v2"
    / "validation"
)
SOURCE = REPOSITORY_ROOT / "cardiosentinel-data" / "ltstdb" / "1.0.0"

#: Deterministic, evenly spaced rows: never a hand-picked subset, and stable
#: across runs so a regression is reproducible rather than probabilistic.
AUDIT_ROWS = 24

#: Float32 machine epsilon is 1.19e-07. The observed maximum over 64 evenly
#: spaced rows was 6 ULP; 32 leaves headroom for a different BLAS thread count
#: without admitting a real divergence, which would be orders of magnitude
#: larger than this.
EMBEDDING_ULP_BOUND = 32

_MISSING = [
    str(path.relative_to(REPOSITORY_ROOT))
    for path in (RUN_ROOT, CORPUS, SOURCE)
    if not path.exists()
]

pytestmark = pytest.mark.skipif(
    bool(_MISSING),
    reason=(
        "Frozen evidence tree absent: "
        + ", ".join(_MISSING)
        + ". These are gitignored, so this equivalence check cannot run on a "
        "fresh checkout. It must be run on a machine holding the evidence "
        "before any edge result is believed."
    ),
)


@pytest.fixture(scope="module")
def extractor():
    from cardiosentinel.edge import RepresentationExtractor, load_frozen_artifacts

    return RepresentationExtractor(load_frozen_artifacts(RUN_ROOT))


@pytest.fixture(scope="module")
def corpus():
    return {
        "stable_id": np.load(CORPUS / "stable_id.npy", mmap_mode="r"),
        "representation": np.load(CORPUS / "representation.npy", mmap_mode="r"),
    }


def _audit_rows(total: int) -> list[int]:
    return sorted(set(np.linspace(0, total - 1, AUDIT_ROWS).astype(int).tolist()))


def _live_representation(extractor, stable_id: str):
    from cardiosentinel.signal.io import read_local_segment
    from cardiosentinel.signal.windows import CausalWindowGenerator

    dataset, record, channel, start, end = stable_id.split(":")
    segment = read_local_segment(
        SOURCE, dataset, record, int(start), int(end), (int(channel),)
    )
    windows = CausalWindowGenerator(segment.sampling_frequency_hz, 10.0, 5.0).process(
        segment
    )
    assert len(windows) == 1, f"{stable_id} yielded {len(windows)} windows, expected 1"
    # The reader was asked for one channel, so the window reports index 0
    # regardless of which source channel it is. Pass the source channel through.
    return extractor.extract(windows[0], channel_index=int(channel))


def test_live_representation_matches_frozen_cache(extractor, corpus):
    """The load-bearing assertion. Everything downstream depends on this."""
    stable_ids = corpus["stable_id"]
    stored_all = corpus["representation"]
    rows = _audit_rows(len(stable_ids))

    embedding_deviations: list[float] = []
    physiology_deviations: list[float] = []
    records: set[str] = set()
    channels: set[int] = set()

    for row in rows:
        stable_id = str(stable_ids[row])
        live = _live_representation(extractor, stable_id)
        stored = np.asarray(stored_all[row], dtype=np.float32)

        assert live.stable_id == stable_id, (
            f"row {row}: live identity {live.stable_id!r} does not match the "
            f"corpus row identity {stable_id!r}"
        )
        assert live.values.shape == stored.shape == (146,)

        np.testing.assert_allclose(
            live.values,
            stored,
            rtol=1e-5,
            atol=1e-6,
            err_msg=f"row {row} ({stable_id}) diverged from the frozen corpus",
        )

        embedding_deviations.append(
            float(np.abs(live.embedding - stored[:128]).max())
        )
        physiology_deviations.append(
            float(np.abs(live.physiology - stored[128:]).max())
        )
        records.add(live.record_id)
        channels.add(live.channel_index)

    # Coverage: a pass on one record and one channel would prove very little.
    assert len(records) >= 5, f"audited only {len(records)} records"
    assert len(channels) >= 2, f"audited only channels {sorted(channels)}"

    # The physiology half goes through no floating-point reduction that could
    # reorder, so it is exact. If this ever loosens, the inputs have drifted --
    # which is a different and much more serious failure than kernel jitter.
    assert max(physiology_deviations) == 0.0, (
        "the physiology half is no longer bit-exact against the frozen corpus; "
        "the morphology inputs or the frozen transform have drifted"
    )

    epsilon = float(np.finfo(np.float32).eps)
    worst_ulp = max(embedding_deviations) / epsilon
    assert worst_ulp <= EMBEDDING_ULP_BOUND, (
        f"embedding deviation {worst_ulp:.1f} ULP exceeds the {EMBEDDING_ULP_BOUND} "
        "ULP bound; this is larger than kernel reduction-order jitter and "
        "indicates a real divergence in the encoder path"
    )


def test_the_extractor_reports_the_transform_the_corpus_was_built_with(extractor):
    """Provenance, not just values: same transform digest, proven by comparison.

    The corpus manifest records the physiology transform digest it was built
    with. The edge runtime loads a transform independently. Equality is what
    lets an alert cite the research evidence.
    """
    import json

    manifest = json.loads(
        (CORPUS / "M1_STREAM_CACHE_MANIFEST.json").read_text(encoding="utf-8")
    )
    provenance = extractor.provenance()
    assert (
        provenance["physiology_transform_sha256"]
        == manifest["physiology_transform_sha256"]
    )
    assert (
        provenance["physiology_schema_sha256"] == manifest["physiology_schema_sha256"]
    )
    assert provenance["embedding_tap"] == manifest["embedding_tap"]
    assert provenance["representation_dim"] == manifest["representation_dim"] == 146
    assert provenance["test_accessed"] is False
    assert provenance["sealed_test_state"] == "unopened"
