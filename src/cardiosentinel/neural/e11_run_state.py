"""The run-state machine for a future E11-class experiment.

E11 ATTEMPT 1 died mid-fold and left a receipt with no `finished_utc`; the only
reason its state was legible afterwards is that a human read the traceback. A
future run should not depend on that.

**States advance in one direction, and only on evidence:**

    AUTHORIZED -> DATA_BOUND -> PHASE1_COMPLETE -> SELECTION_FROZEN
               -> PHASE2_COMPLETE -> OUTER_SCORED -> GEOMETRY_COMPLETE
               -> ANALYSIS_READY

A transition requires the artifacts the stage declares, each present and each
matching the digest recorded for it. Advancing to a state whose predecessor was
never recorded is refused.

**A later state cannot be reached by dropping a file into the directory.** Each
stage's entry is sealed with a digest computed over the previous stage's seal,
so the record is a chain rather than a list. Forging a stage requires forging
every stage before it, and the artifacts each one names.

**Fail closed, and no automatic retry.** An interrupted run keeps whatever
stages were durably sealed and its `failure_state` is recorded; nothing here
resumes, reruns or reseeds. Re-execution after a failure is a new attempt and a
human decision -- exactly the rule the E11 authorization already states.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

from cardiosentinel.baseline.cache import write_json_atomic

__all__ = [
    "E11_RUN_STATE_SCHEMA_VERSION",
    "E11RunStateError",
    "E11RunState",
    "E11RunReceipt",
]

E11_RUN_STATE_SCHEMA_VERSION: Final[str] = "e11-run-state-v1"


class E11RunStateError(RuntimeError):
    """An illegal transition, or evidence that did not verify."""


class E11RunState(Enum):
    AUTHORIZED = 0
    DATA_BOUND = 1
    PHASE1_COMPLETE = 2
    SELECTION_FROZEN = 3
    PHASE2_COMPLETE = 4
    OUTER_SCORED = 5
    GEOMETRY_COMPLETE = 6
    ANALYSIS_READY = 7


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def _seal(payload: Mapping[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "seal"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class E11RunReceipt:
    """A hash-chained, atomically written record of how far a run legally got."""

    path: Path
    authorization_identity: str
    experiment_id: str
    stages: list[dict[str, Any]] = field(default_factory=list)
    failure_state: dict[str, Any] | None = None

    @property
    def current_state(self) -> E11RunState:
        if not self.stages:
            return E11RunState.AUTHORIZED
        return E11RunState[self.stages[-1]["state"]]

    @property
    def completed(self) -> tuple[str, ...]:
        return tuple(stage["state"] for stage in self.stages)

    def advance(
        self,
        state: E11RunState,
        *,
        artifacts: Sequence[Path] = (),
        digests: Mapping[str, str] | None = None,
        detail: Mapping[str, Any] | None = None,
    ) -> str:
        """Seal one stage. Refuses to skip, repeat, or advance on absent evidence."""
        expected = self.current_state.value + 1 if self.stages else 1
        if state is E11RunState.AUTHORIZED:
            raise E11RunStateError("AUTHORIZED is the initial state, not a transition")
        if state.value != expected:
            raise E11RunStateError(
                f"illegal transition {self.current_state.name} -> {state.name}: "
                f"expected {E11RunState(expected).name}"
            )
        if self.failure_state is not None:
            raise E11RunStateError(
                "this run recorded a failure state; re-execution is a new attempt "
                "requiring a new human authorization"
            )

        recorded: dict[str, str] = {}
        for artifact in artifacts:
            artifact = Path(artifact)
            if not artifact.exists():
                raise E11RunStateError(
                    f"{state.name} requires {artifact} but it does not exist"
                )
            recorded[str(artifact)] = _sha256_file(artifact)
        for name, digest in (digests or {}).items():
            if not digest:
                raise E11RunStateError(f"{state.name} requires a digest for {name}")
            recorded[name] = digest

        entry: dict[str, Any] = {
            "state": state.name,
            "index": state.value,
            "recorded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "artifacts": recorded,
            "detail": dict(detail or {}),
            "previous_seal": self.stages[-1]["seal"] if self.stages else None,
        }
        entry["seal"] = _seal(entry)
        self.stages.append(entry)
        self._flush()
        return entry["seal"]

    def record_failure(self, stage: str, exception: BaseException) -> None:
        """Record a failure and stop. Nothing here retries."""
        import traceback

        self.failure_state = {
            "stage": stage,
            "failed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "exception_type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exc(),
            "relaunched": False,
            "note": (
                "STOPPED. No relaunch, no reseed, no fold rerun. Re-execution "
                "after a failure is a new attempt requiring new human authorization."
            ),
        }
        self._flush()

    def _flush(self) -> None:
        write_json_atomic(
            Path(self.path),
            {
                "schema": E11_RUN_STATE_SCHEMA_VERSION,
                "experiment_id": self.experiment_id,
                "authorization_identity": self.authorization_identity,
                "current_state": self.current_state.name,
                "completed_stages": list(self.completed),
                "stages": self.stages,
                "failure_state": self.failure_state,
            },
        )

    @staticmethod
    def load(path: Path) -> "E11RunReceipt":
        """Load and verify the chain. A forged or torn stage is refused."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema") != E11_RUN_STATE_SCHEMA_VERSION:
            raise E11RunStateError(f"unknown schema: {payload.get('schema')!r}")
        stages = payload.get("stages", [])
        previous: str | None = None
        for position, stage in enumerate(stages, start=1):
            if stage.get("index") != position:
                raise E11RunStateError(
                    f"stage {stage.get('state')!r} is out of order: a later state "
                    "cannot be reached without its predecessors"
                )
            if stage.get("previous_seal") != previous:
                raise E11RunStateError(
                    f"broken chain at {stage.get('state')!r}: this stage does not "
                    "follow the one recorded before it"
                )
            if stage.get("seal") != _seal(stage):
                raise E11RunStateError(
                    f"stage {stage.get('state')!r} failed its seal check"
                )
            for artifact, digest in stage.get("artifacts", {}).items():
                candidate = Path(artifact)
                if candidate.exists() and _sha256_file(candidate) != digest:
                    raise E11RunStateError(
                        f"artifact {artifact} no longer matches the digest sealed "
                        f"at {stage.get('state')!r}"
                    )
            previous = stage["seal"]
        receipt = E11RunReceipt(
            path=Path(path),
            authorization_identity=payload["authorization_identity"],
            experiment_id=payload["experiment_id"],
            stages=stages,
            failure_state=payload.get("failure_state"),
        )
        return receipt
