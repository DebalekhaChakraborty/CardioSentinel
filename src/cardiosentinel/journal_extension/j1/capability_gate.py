"""The J1 pre-claim capability gate: can this graph finish?

Adapted from `neural/t1_capability_gate`. The invariant it preserves is the same
one, and it is the reason the module exists:

    an attempt must never be consumed by an execution path that cannot complete.

`callable` is true of a function whose entire body is a refusal, so binding a
collaborator proves nothing about finishing. Three independent checks run before
any claim, and none executes a scientific body.

This module reads no scientific data and consults no permission. Whether a run
*could* finish and whether it *may* start are different questions, and the
second is `authorization.py`'s. A capability attestation never implies
authorization.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import dataclass
from typing import Any

#: Every collaborator the canonical J1 driver calls, with the call it makes.
#: Second-phase methods are included: a graph that completes the inner barrier
#: and refuses at the outer one has still consumed the attempt.
REQUIRED_COLLABORATORS: dict[str, tuple[str, ...]] = {
    "fold_allocator": ("allocate",),
    "calibration_fitter": ("fit_inner", "fit_outer"),
    "threshold_deriver": ("derive",),
    "candidate_evaluator": ("evaluate_inner", "evaluate_outer"),
    "selection_ranker": ("rank",),
    "bootstrap": ("resample",),
    "provenance_sink": ("open_attempt", "promote"),
}


class J1CapabilityError(RuntimeError):
    """A collaborator graph that cannot complete a canonical J1 run."""


@dataclass(frozen=True)
class J1CapabilityAttestation:
    """One collaborator's declaration that it can finish."""

    collaborator: str
    execution_capable: bool
    detail: str = ""


def _structurally_completes(function: Any) -> bool:
    """Proof, not heuristic: is a `return` or `yield` reachable in the body?

    An attestation is a claim and a claim can be wrong. A function whose body
    cannot produce a value cannot feed the next stage, whatever it says about
    itself, so when proof and attestation disagree the proof wins.
    """
    try:
        source = textwrap.dedent(inspect.getsource(function))
    except (OSError, TypeError):
        return False
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom)):
            return True
    return False


def _attestation_of(collaborator: Any, name: str) -> J1CapabilityAttestation:
    """Silence is a refusal. This is an allowlist, never a denylist.

    A denylist of known placeholder types would admit the next placeholder
    somebody writes, which is exactly the case this gate must survive.
    """
    marker = getattr(collaborator, "j1_execution_capability", None)
    if marker is None:
        raise J1CapabilityError(
            f"{name!r} does not attest execution capability. Silence is a "
            "refusal: a collaborator must positively declare it can finish."
        )
    attestation = marker() if callable(marker) else marker
    if not isinstance(attestation, J1CapabilityAttestation):
        raise J1CapabilityError(
            f"{name!r} attested with {type(attestation).__name__}, not a "
            "J1CapabilityAttestation."
        )
    return attestation


def require_execution_capability(collaborators: dict[str, Any]) -> dict[str, bool]:
    """Prove the whole graph can finish. Raises rather than reporting a score."""
    missing = sorted(set(REQUIRED_COLLABORATORS) - set(collaborators))
    if missing:
        raise J1CapabilityError(
            "collaborator graph incomplete: " + ", ".join(missing)
        )

    proven: dict[str, bool] = {}
    for name, methods in REQUIRED_COLLABORATORS.items():
        collaborator = collaborators[name]
        for method_name in methods:
            method = getattr(collaborator, method_name, None)
            if method is None or not callable(method):
                raise J1CapabilityError(
                    f"{name!r} does not expose a callable {method_name!r}; the "
                    "driver calls it, so a graph without it cannot finish."
                )
            if not _structurally_completes(method):
                raise J1CapabilityError(
                    f"{name}.{method_name} has no reachable return or yield. It "
                    "cannot produce what the next stage consumes, whatever it "
                    "attests about itself."
                )
        attestation = _attestation_of(collaborator, name)
        if not attestation.execution_capable:
            raise J1CapabilityError(
                f"{name!r} attests it cannot execute: {attestation.detail!r}."
            )
        proven[name] = True
    return proven
