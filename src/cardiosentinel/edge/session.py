"""The streaming inference session: the composed pipeline, one window at a time.

Every stage here already existed and was validated. What did not exist was a
thing that holds all five pieces of causal state at once and advances them
together:

===========================  ================================================
state                        owned by
===========================  ================================================
filter / window buffer       `CausalWindowGenerator`
patient memory + refractory  `m2_policy.M2StreamState`
longitudinal temporal state  the S4D block state tuple
episode state                the T1 state string
persistence streaks          `T1Streaks`
===========================  ================================================

**Nothing in this module reimplements a decision rule.** The M2 order comes
from `m2_policy.step`, the calibration from `U1Calibrator`, the temporal carry
from `CausalS4DLongitudinal.forward(values, state)`, and the episode transition
from `t1_protocol.next_state`. This file is composition and bookkeeping.

The four row semantics were **derived from the persisted research evidence, not
assumed**, and each is pinned by a test:

* `detector_decision_d_t` is `m2g_detector_score >= 0.7554003000259399`, the
  frozen M1L operating point inherited through M2-G. Never re-selected here.
* `oof_calibrated_probability_p_t` is the U1 Platt calibrator applied to that
  score.
* `decision_error_uncertainty_u_t` is `1 - p` when the decision is positive and
  `p` when it is negative -- the probability that the decision taken is wrong.
* `s4d_temporal_evidence_s_t` is `sigmoid` of the S4D readout. The persisted
  column is bounded in `[0.000735, 0.998675]`, so it is a squashed score and
  not the raw logit.

**A bounded sigmoid is not a probability.** `s_t` carries
`score_is_calibrated_probability: false` and must never be described as one.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import torch

from ..neural import m2_policy
from ..neural.m2_gate import G3_SQI_COLUMNS
from ..neural.patient_memory import exact_flat_unavailable
from ..neural.t1_protocol import (
    T1_INITIAL_STATE,
    T1_PERSISTENCE_PROFILES,
    T1_ZERO_STREAKS,
    T1Row,
    next_state,
)
from ..signal.models import CausalWindow
from ..signal.quality import compute_signal_quality
from .artifacts import RuntimeArtifacts
from .representation import RepresentationExtractor

#: Frozen: the M1L operating point, inherited through M2-G and never chosen here.
DETECTOR_THRESHOLD = 0.7554003000259399


class SessionError(RuntimeError):
    """The session cannot advance without inventing something."""


@dataclass(frozen=True)
class EdgeObservation:
    """One window's decision, with everything needed to explain it.

    This is the record the agentic layer consumes. It deliberately carries the
    gate provenance and not just the outcome: *why* a window did or did not move
    the patient baseline is the question an Evidence Agent will be asked.
    """

    stable_id: str
    record_id: str
    subject_id: str
    channel_index: int
    start_sample: int
    elapsed_stream_seconds: float
    score_present: bool
    detector_score: float | None
    detector_decision: bool | None
    calibrated_probability: float | None
    decision_error_uncertainty: float | None
    temporal_evidence: float | None
    memory_deviation: float | None
    state_before: str
    state: str
    streaks: dict[str, int]
    memory_update_admitted: bool
    gate: dict[str, Any]
    contains_filter_warmup: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class _SessionState:
    """The five pieces of causal state, held together."""

    m2: Any
    temporal: tuple[torch.Tensor, ...] | None = None
    t1_state: str = T1_INITIAL_STATE
    streaks: Any = T1_ZERO_STREAKS
    windows_seen: int = 0
    history: list[EdgeObservation] = field(default_factory=list)


class StreamingInferenceSession:
    """One patient, one channel, advanced one causal window at a time.

    `subject_id` selects the leave-one-subject-out T1 operating point and the
    memory namespace. It is **never** a model input -- the same rule the
    research pipeline enforced in code.
    """

    def __init__(
        self,
        artifacts: RuntimeArtifacts,
        *,
        subject_id: str,
        record_id: str,
        channel_index: int,
        dataset_id: str = "ltstdb",
    ) -> None:
        policy_subject = artifacts.t1_policy.held_out_subject
        if subject_id != policy_subject:
            raise SessionError(
                f"The loaded T1 policy is the held-out operating point for "
                f"{policy_subject!r}, but this session is for {subject_id!r}. "
                "Thresholds are leave-one-subject-out and are not transferable."
            )
        self._artifacts = artifacts
        self._extractor = RepresentationExtractor(
            artifacts.frozen, dataset_id=dataset_id
        )
        self._subject_id = subject_id
        self._record_id = record_id
        self._channel_index = int(channel_index)
        self._dataset_id = dataset_id
        self._profile = {
            profile.name: profile for profile in T1_PERSISTENCE_PROFILES
        }[artifacts.t1_policy.persistence_profile]
        self._state = _SessionState(
            m2=m2_policy.M2StreamState.cold_start(
                artifacts.standardizer.prior_vector(), arm=artifacts.m2_arm
            )
        )

    # -- introspection -----------------------------------------------------

    @property
    def state(self) -> str:
        return self._state.t1_state

    @property
    def windows_seen(self) -> int:
        return self._state.windows_seen

    @property
    def observations(self) -> tuple[EdgeObservation, ...]:
        return tuple(self._state.history)

    def provenance(self) -> dict[str, Any]:
        payload = dict(self._artifacts.provenance())
        payload.update(
            {
                "subject_id": self._subject_id,
                "record_id": self._record_id,
                "channel_index": self._channel_index,
                "detector_threshold": DETECTOR_THRESHOLD,
                "detector_threshold_selected_here": False,
                "patient_identity_is_a_feature": False,
            }
        )
        return payload

    # -- the causal step ---------------------------------------------------

    def step(self, window: CausalWindow) -> EdgeObservation:
        """Advance the session by exactly one causal window."""
        if window.record_id != self._record_id:
            raise SessionError(
                f"This session streams {self._record_id!r}; received "
                f"{window.record_id!r}. One session is one stream."
            )
        representation = self._extractor.extract(
            window, channel_index=self._channel_index
        )
        values = np.asarray(window.values, dtype=np.float64)

        # Physical observability, by the same rule M1 used: an exactly flat
        # window carries no information and is not an observation.
        unavailable = bool(exact_flat_unavailable(values))
        observation_state = (
            m2_policy.OBSERVATION_UNAVAILABLE_EXACT_FLAT
            if unavailable
            else m2_policy.OBSERVATION_AVAILABLE
        )

        quality = compute_signal_quality(window)
        sqi = {
            column: float(getattr(quality, column))
            for column in G3_SQI_COLUMNS
            if hasattr(quality, column)
        }
        # The RAW flag. The standardised column is not the 0/1 signal G6 wants.
        morphology_valid = representation.morphology_valid

        row = m2_policy.M2TimelineRow(
            record_id=self._record_id,
            channel_index=self._channel_index,
            start_sample=int(window.start_sample),
            observation_state=observation_state,
            representation=(
                np.asarray(representation.values, dtype=np.float64)
                if not unavailable
                else None
            ),
            finite_sample_fraction=(
                None
                if unavailable
                else float(getattr(quality, "finite_sample_fraction", 1.0))
            ),
            sqi=sqi or None,
            morphology_valid=morphology_valid,
        )

        # The frozen M2 order, from the one place it lives.
        evidence = m2_policy.step(
            self._state.m2,
            row,
            arm=self._artifacts.m2_arm,
            standardizer=self._artifacts.standardizer,
            scorer=self._artifacts.m1l_scorer,
        )

        score = evidence.decision.score
        present = score is not None
        decision = calibrated = uncertainty = temporal = None
        if present:
            decision = bool(score >= DETECTOR_THRESHOLD)
            calibrated = float(
                self._artifacts.calibrator.apply_to_scores(np.array([score]))[0]
            )
            # u_t: the probability the taken decision is wrong.
            uncertainty = float(1.0 - calibrated if decision else calibrated)
            temporal = self._temporal_step(representation.values)

        state_before = self._state.t1_state
        t1_row = T1Row(
            stable_id=representation.stable_id,
            score_present=present,
            detector_decision=decision,
            calibrated_probability=calibrated,
            decision_error_uncertainty=uncertainty,
            temporal_evidence=temporal,
            elapsed_stream_seconds=float(window.end_sample)
            / float(window.sampling_frequency_hz),
        )
        self._state.t1_state, self._state.streaks = next_state(
            state_before,
            self._state.streaks,
            t1_row,
            self._artifacts.t1_policy.thresholds,
            self._profile,
        )
        self._state.windows_seen += 1

        observation = EdgeObservation(
            stable_id=representation.stable_id,
            record_id=self._record_id,
            subject_id=self._subject_id,
            channel_index=self._channel_index,
            start_sample=int(window.start_sample),
            elapsed_stream_seconds=t1_row.elapsed_stream_seconds,
            score_present=present,
            detector_score=None if score is None else float(score),
            detector_decision=decision,
            calibrated_probability=calibrated,
            decision_error_uncertainty=uncertainty,
            temporal_evidence=temporal,
            memory_deviation=evidence.d_long,
            state_before=state_before,
            state=self._state.t1_state,
            streaks=dict(self._state.streaks._asdict()),
            memory_update_admitted=bool(evidence.update_admitted),
            gate=evidence.as_dict(),
            contains_filter_warmup=representation.contains_filter_warmup,
        )
        self._state.history.append(observation)
        return observation

    def _temporal_step(self, representation: np.ndarray) -> float:
        """One S4D step, carrying block state across windows.

        The persisted `s4d_temporal_evidence_s_t` column is bounded in
        `[0.000735, 0.998675]`, so the readout logit is squashed. It is a
        bounded score, not a calibrated probability.
        """
        values = torch.from_numpy(
            np.asarray(representation, dtype=np.float32)
        ).reshape(1, 1, -1)
        if self._state.temporal is None:
            self._state.temporal = self._artifacts.temporal_model.initial_state(1)
        with torch.no_grad():
            logits, self._state.temporal = self._artifacts.temporal_model(
                values, self._state.temporal
            )
        return float(torch.sigmoid(logits.reshape(-1)[-1]))

    def step_many(self, windows) -> tuple[EdgeObservation, ...]:
        return tuple(self.step(window) for window in windows)
