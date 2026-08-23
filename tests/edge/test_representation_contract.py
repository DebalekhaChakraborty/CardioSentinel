"""Hermetic contract tests for the edge representation bridge.

These run everywhere, including CI, because they need no frozen evidence. They
prove the *shape* of the contract; `test_representation_matches_frozen_cache.py`
proves the *values*, and needs the evidence tree.

Every fixture here uses real numpy arrays and a real `CausalWindow`. A test that
passes Python lists proves the code accepts lists, which is not the code path
the runtime takes -- a lesson this repository learned when 27 green tests for a
paired bootstrap were followed by a `ValueError` on the first real numpy call.
"""

from __future__ import annotations

import numpy as np
import pytest

from cardiosentinel.edge.representation import (
    EMBEDDING_SLICE,
    PHYSIOLOGY_SLICE,
    REPRESENTATION_DIM,
    SAMPLING_FREQUENCY_HZ,
    WINDOW_SAMPLES,
    RepresentationError,
    WindowRepresentation,
    require_raw_profile,
    stable_id_for,
)
from cardiosentinel.signal.config import FilterProfile, HighPassConfig, raw_profile
from cardiosentinel.signal.models import CausalWindow


def make_window(
    values: np.ndarray | None = None,
    *,
    fs: float = SAMPLING_FREQUENCY_HZ,
    unit: str = "mV",
    record: str = "s20041",
    channel: int = 0,
    start: int = 0,
) -> CausalWindow:
    if values is None:
        values = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    return CausalWindow(
        record,
        "ltstdb:s2004",
        channel,
        "I",
        "I",
        unit,
        fs,
        start,
        start + len(values),
        start / fs,
        (start + len(values)) / fs,
        start + len(values),
        False,
        values,
    )


def test_representation_dim_is_the_frozen_146():
    """128 encoder + 18 physiology. A drift here breaks every retained model."""
    assert REPRESENTATION_DIM == 146
    assert EMBEDDING_SLICE == slice(0, 128)
    assert PHYSIOLOGY_SLICE == slice(128, 146)


def test_the_physiology_half_is_exactly_morphology_v1():
    """The bridge only exists because these two tuples are the same tuple."""
    from cardiosentinel.features import MORPHOLOGY_V1
    from cardiosentinel.neural.physiology_fusion import PHYSIOLOGY_FEATURE_NAMES

    assert tuple(PHYSIOLOGY_FEATURE_NAMES) == tuple(MORPHOLOGY_V1.names)
    assert len(MORPHOLOGY_V1.names) == 18


def test_stable_id_reproduces_the_corpus_row_identity():
    window = make_window(record="s20041", channel=0, start=0)
    assert stable_id_for(window) == "ltstdb:s20041:0:0:2500"
    shifted = make_window(record="s30732", channel=2, start=19287500)
    assert stable_id_for(shifted) == "ltstdb:s30732:2:19287500:19290000"


def test_a_filtered_profile_is_refused():
    """The frozen corpus is `processing_profile: raw`; filtering diverges."""
    assert require_raw_profile(raw_profile()).is_raw
    filtered = FilterProfile(
        name="st_preserving",
        highpass=HighPassConfig(enabled=True, cutoff_hz=0.05, order=2),
    )
    with pytest.raises(RepresentationError, match="raw identity profile"):
        require_raw_profile(filtered)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"fs": 500.0}, "250 Hz"),
        ({"unit": "V"}, "mV"),
    ],
)
def test_window_validation_refuses_a_non_conforming_window(kwargs, match):
    from cardiosentinel.edge.representation import _validate_window

    with pytest.raises(RepresentationError, match=match):
        _validate_window(make_window(**kwargs))


def test_a_short_window_is_refused_rather_than_padded():
    from cardiosentinel.edge.representation import _validate_window

    short = make_window(np.zeros(2499, dtype=np.float64))
    with pytest.raises(RepresentationError, match="2500"):
        _validate_window(short)


def test_a_non_finite_window_is_refused_rather_than_imputed():
    """Physiology imputes; the waveform never does."""
    from cardiosentinel.edge.representation import _validate_window

    values = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    values[17] = np.nan
    with pytest.raises(RepresentationError, match="non-finite"):
        _validate_window(make_window(values))


def test_the_encoder_input_is_the_frozen_b4_contract():
    """[1, 1, 2500] float32 -- the sole float64 cast, as B4WaveformDataset does."""
    from cardiosentinel.edge.representation import _encoder_input, _validate_window

    values = np.linspace(-1.0, 1.0, WINDOW_SAMPLES, dtype=np.float64)
    tensor = _encoder_input(_validate_window(make_window(values)))
    assert tuple(tensor.shape) == (1, 1, WINDOW_SAMPLES)
    assert str(tensor.dtype) == "torch.float32"
    assert np.array_equal(tensor.numpy().reshape(-1), values.astype(np.float32))


def test_window_representation_slices_the_two_halves():
    values = np.arange(REPRESENTATION_DIM, dtype=np.float32)
    representation = WindowRepresentation(
        values=values,
        stable_id="ltstdb:s20041:0:0:2500",
        record_id="s20041",
        subject_id="ltstdb:s2004",
        channel_index=0,
        start_sample=0,
        end_sample=2500,
        contains_filter_warmup=False,
    )
    assert representation.embedding.shape == (128,)
    assert representation.physiology.shape == (18,)
    assert representation.physiology[0] == pytest.approx(128.0)


def test_channel_identity_can_be_overridden_for_channel_selected_reads():
    """A single-channel read reports index 0 whatever channel it actually is.

    Without the override every alert from a non-zero channel would cite the
    wrong signal, and the identity would silently miss its corpus row.
    """
    window = make_window(record="s20041", channel=0, start=5272500)
    assert stable_id_for(window) == "ltstdb:s20041:0:5272500:5275000"
    assert (
        stable_id_for(window, channel_index=1)
        == "ltstdb:s20041:1:5272500:5275000"
    )
