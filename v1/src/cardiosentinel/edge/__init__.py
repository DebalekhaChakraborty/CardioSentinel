"""Edge runtime: the laptop simulation of the validated inference pipeline.

This package was a one-line docstring through the whole research phase. It is
now the seam between two halves that were each complete and never joined: the
streaming signal path, and the retained model chain that read a precomputed
corpus instead of a live stream.

Nothing here is a new model, a new threshold, or a new experiment. Every weight,
transform and policy is loaded frozen from a completed run.
"""

from .artifacts import EdgeArtifactError, FrozenArtifacts, load_frozen_artifacts
from .representation import (
    EMBEDDING_SLICE,
    PHYSIOLOGY_SLICE,
    REPRESENTATION_DIM,
    RepresentationError,
    RepresentationExtractor,
    WindowRepresentation,
    require_raw_profile,
    stable_id_for,
)

__all__ = [
    "EMBEDDING_SLICE",
    "PHYSIOLOGY_SLICE",
    "REPRESENTATION_DIM",
    "EdgeArtifactError",
    "FrozenArtifacts",
    "RepresentationError",
    "RepresentationExtractor",
    "WindowRepresentation",
    "load_frozen_artifacts",
    "require_raw_profile",
    "stable_id_for",
]
