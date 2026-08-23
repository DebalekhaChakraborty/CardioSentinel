"""The bridge: one `CausalWindow` to the 146-d representation the models consume.

This is the only link in the pipeline that did not exist before. Everything
upstream of it (`StreamingPreprocessor`, `CausalWindowGenerator`,
`extract_morphology_features`) and everything downstream of it (M1L memory,
M2-G, U1 calibration, T2 S4D, T1) was built, executed and validated during the
research phase. They were never joined, because the research path read a
precomputed 16 GB feature corpus instead of computing the representation live.

**The composition is not a new design.** It restates, for a single live window,
exactly what `m1_experiment._fuse` did for a cached batch::

    z_t[146] = concat(
        B4BTransformerCNN.encode(waveform[1, 1, 2500] float32 mV)  -> [128]
        PhysiologyTransform.transform(morphology_v1)               -> [ 18]
    ).astype(float32)

The 18 physiology features are `MORPHOLOGY_V1.names`, which is the *same tuple*
as `physiology_fusion.PHYSIOLOGY_FEATURE_NAMES` -- so `features/morphology.py`
already produced, live, exactly the physiology half the retained models expect.

**Why this module is verified rather than trusted.** If the live vector differs
from the frozen one, every downstream number is a different system wearing the
validated system's results. `tests/edge/test_representation_matches_frozen_cache.py`
compares this path against `representation.npy` from the frozen M1 stream cache
and is the reason anything built on top of it is allowed to claim continuity.

**Filtering.** The frozen corpus was built under `processing_profile: raw`, an
explicit identity profile that enables no filter. A live stream that applies a
band-pass before this function will not reproduce the frozen representation.
`require_raw_profile` exists so that mistake fails loudly instead of silently
shifting every embedding.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from numpy.typing import NDArray

from ..features.morphology import extract_morphology_features
from ..features.schema import FeatureSchema
from ..neural.physiology_fusion import (
    EMBEDDING_DIM,
    PHYSIOLOGY_DIM,
    extract_frozen_embeddings,
)
from ..signal.config import FilterProfile
from ..signal.models import CausalWindow
from .artifacts import FrozenArtifacts

#: `m1_experiment.REPRESENTATION_DIM`, restated so a mismatch is caught here.
REPRESENTATION_DIM = EMBEDDING_DIM + PHYSIOLOGY_DIM

#: The frozen B4 input contract: one channel, 2500 samples, 10 s at 250 Hz.
WINDOW_SAMPLES = 2500
SAMPLING_FREQUENCY_HZ = 250.0
CANONICAL_PHYSICAL_UNIT = "mV"

EMBEDDING_SLICE = slice(0, EMBEDDING_DIM)
PHYSIOLOGY_SLICE = slice(EMBEDDING_DIM, REPRESENTATION_DIM)


class RepresentationError(RuntimeError):
    """A window cannot produce a representation the frozen models would accept."""


def require_raw_profile(profile: FilterProfile) -> FilterProfile:
    """The frozen corpus is `processing_profile: raw`; anything else diverges."""
    if not profile.is_raw:
        raise RepresentationError(
            f"The frozen representation was built under the raw identity "
            f"profile; profile {profile.name!r} enables filtering and will not "
            "reproduce it. Pass signal.config.raw_profile()."
        )
    return profile


@dataclass(frozen=True)
class WindowRepresentation:
    """One live 146-d representation and the identity it was computed from."""

    values: NDArray[np.float32]
    #: The RAW `morphology_valid` flag, before standardisation.
    #:
    #: The frozen physiology transform standardises every column, the validity
    #: flag included, so `physiology[...]` is **not** the 0/1 reliability signal
    #: M2's G6 admission condition expects. Reading it from the standardised
    #: vector fails G6 on every window and the patient memory silently never
    #: adapts. It is carried here so morphology is extracted exactly once.
    morphology_valid: float
    stable_id: str
    record_id: str
    subject_id: str
    channel_index: int
    start_sample: int
    end_sample: int
    contains_filter_warmup: bool

    @property
    def embedding(self) -> NDArray[np.float32]:
        return self.values[EMBEDDING_SLICE]

    @property
    def physiology(self) -> NDArray[np.float32]:
        return self.values[PHYSIOLOGY_SLICE]


def stable_id_for(
    window: CausalWindow,
    dataset_id: str = "ltstdb",
    *,
    channel_index: int | None = None,
) -> str:
    """Reproduce the corpus row identity `dataset:record:channel:start:end`.

    **`channel_index` is an override, and it is not decorative.**
    `CausalWindow.channel_index` is the channel's position *within the segment
    that produced it*, not its index in the source record. A reader asked for
    channel 1 alone returns a single-channel segment whose window reports
    channel 0, so an identity built from the window would name the wrong
    channel -- and every alert derived from it would cite the wrong signal.

    A live stream that reads all channels needs no override; the window index
    is the source index. Anything that channel-selects at read time must pass
    the source channel explicitly.
    """
    channel = window.channel_index if channel_index is None else int(channel_index)
    return (
        f"{dataset_id}:{window.record_id}:{channel}:"
        f"{window.start_sample}:{window.end_sample}"
    )


def _validate_window(window: CausalWindow) -> NDArray[np.float64]:
    values = np.asarray(window.values, dtype=np.float64)
    if values.ndim != 1 or values.size != WINDOW_SAMPLES:
        raise RepresentationError(
            f"A B4 window must contain exactly {WINDOW_SAMPLES} single-channel "
            f"samples; received shape {values.shape}."
        )
    if float(window.sampling_frequency_hz) != SAMPLING_FREQUENCY_HZ:
        raise RepresentationError(
            "B4 requires an authoritative sampling frequency of 250 Hz; "
            f"received {window.sampling_frequency_hz}."
        )
    if window.physical_unit != CANONICAL_PHYSICAL_UNIT:
        raise RepresentationError(
            f"B4 requires canonical {CANONICAL_PHYSICAL_UNIT} values; received "
            f"{window.physical_unit!r}."
        )
    if not np.isfinite(values).all():
        raise RepresentationError(
            "The window contains non-finite physical values. The frozen path "
            "refuses the window rather than imputing the waveform."
        )
    return values


def _encoder_input(values: NDArray[np.float64]) -> torch.Tensor:
    """The sole float64 -> float32 cast, matching `B4WaveformDataset`."""
    single = np.asarray(values, dtype=np.float32)
    return torch.from_numpy(single.copy()).reshape(1, 1, WINDOW_SAMPLES)


class RepresentationExtractor:
    """Turn live causal windows into the representation the retained models eat.

    Holds the frozen artifacts so the encoder is loaded once per session rather
    than once per window -- the difference between a demo that streams and a
    demo that stutters.
    """

    def __init__(self, artifacts: FrozenArtifacts, *, dataset_id: str = "ltstdb"):
        self._artifacts = artifacts
        self._dataset_id = dataset_id
        names = tuple(artifacts.physiology.feature_names)
        schema: FeatureSchema = _morphology_schema()
        if names != tuple(schema.names):
            raise RepresentationError(
                "The frozen physiology transform's feature order is not "
                "morphology_v1. The live morphology extractor cannot feed it."
            )

    @property
    def artifacts(self) -> FrozenArtifacts:
        return self._artifacts

    def physiology_features(
        self, window: CausalWindow
    ) -> tuple[NDArray[np.float64], float]:
        """The standardised 18 features, plus the raw validity flag.

        Both come from one extraction. The raw flag is returned separately
        because the transform standardises it away.
        """
        from ..features import MORPHOLOGY_V1

        raw = np.asarray(extract_morphology_features(window), dtype=np.float64)
        validity = float(raw[MORPHOLOGY_V1.names.index("morphology_valid")])
        return self._artifacts.physiology.transform(raw.reshape(1, -1)), validity

    def embedding(self, window: CausalWindow) -> NDArray[np.float32]:
        """The pooled B4-B embedding, with the encoder proven unmutated."""
        values = _validate_window(window)
        embeddings, _ = extract_frozen_embeddings(
            self._artifacts.encoder, _encoder_input(values)
        )
        return embeddings.to(torch.float32).numpy()

    def extract(
        self, window: CausalWindow, *, channel_index: int | None = None
    ) -> WindowRepresentation:
        """One window in, one 146-d representation out.

        `channel_index` overrides the window's own index when the segment was
        channel-selected at read time -- see `stable_id_for`.
        """
        embedding = self.embedding(window)
        physiology, morphology_valid = self.physiology_features(window)
        fused = np.concatenate([embedding, physiology], axis=1).astype(np.float32)
        if fused.shape != (1, REPRESENTATION_DIM):
            raise RepresentationError(
                f"Fused representation must be [1, {REPRESENTATION_DIM}]; "
                f"received {fused.shape}."
            )
        if not np.all(np.isfinite(fused)):
            raise RepresentationError(
                "A non-finite representation was produced despite the frozen "
                "physiology transform. The edge runtime refuses the window "
                "rather than emitting a value the models cannot interpret."
            )
        channel = (
            window.channel_index if channel_index is None else int(channel_index)
        )
        return WindowRepresentation(
            values=fused[0],
            morphology_valid=morphology_valid,
            stable_id=stable_id_for(
                window, self._dataset_id, channel_index=channel
            ),
            record_id=window.record_id,
            subject_id=window.subject_id,
            channel_index=channel,
            start_sample=window.start_sample,
            end_sample=window.end_sample,
            contains_filter_warmup=bool(window.contains_filter_warmup),
        )

    def provenance(self) -> dict[str, Any]:
        payload = dict(self._artifacts.provenance())
        payload["representation_dim"] = REPRESENTATION_DIM
        payload["composition"] = "concat(b4b_encode[128], physiology_v1[18])"
        payload["processing_profile"] = "raw"
        return payload


def _morphology_schema() -> FeatureSchema:
    from ..features import MORPHOLOGY_V1

    return MORPHOLOGY_V1
