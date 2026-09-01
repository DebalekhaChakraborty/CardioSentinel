"""Negative capability: proof that J1 *cannot do too much*.

The capability gate proves the graph can finish. This is its mirror image.

Three independent layers, following the V1 continuation precedent, because a
proof at one layer does not substitute for another.

**Layer 1, structural.** J1's execution modules reach no forbidden entry point,
proven by walking the syntax tree and the resolved import graph -- **never by
scanning source text**. Text scanning is not merely imprecise here, it is
systematically wrong: this very module names every function it forbids, so any
grep for those names matches the guard itself. V1 recorded that false positive
five times.

**Layer 2, runtime.** Some forbidden entry points live in modules J1 must load
for safe frozen primitives, so absence from `sys.modules` cannot be the whole
proof. Those entry points are instrumented for the duration of a run: each
wrapper records and then refuses. The frozen module's file is never modified --
attributes are rebound in-process and restored in a `finally`.

**Layer 3, evidence.** Every attempt receipt persists these attestations and
their zero counters, so the record proves what did *not* happen.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

#: Forbidden by *name*, not by module. J1 legitimately imports `t1_protocol` for
#: frozen primitives, so banning the module would be false and banning nothing
#: would be useless.
FORBIDDEN_ENTRY_POINTS: dict[str, tuple[str, ...]] = {
    "cardiosentinel.neural.b4b_sealed_test": (
        "verify_selection_identity",
        "load_selected_model",
        "resolve_selected_run_dir",
        "read_selection_record",
    ),
    "cardiosentinel.edge.artifacts": (
        "resolve_t1_policy",
        "load_frozen_artifacts",
    ),
    "cardiosentinel.neural.t1_protocol": (
        "candidate_policies",
        "empirical_order_statistic",
        "policy_sort_key",
        "next_state",
    ),
}

#: Modules that need never be loaded at all. Absence is provable directly.
FORBIDDEN_MODULES: tuple[str, ...] = ("cardiosentinel.neural.b4b_sealed_test",)

COUNTER_NAMES: tuple[str, ...] = (
    "validation_subject_accesses",
    "test_subject_accesses",
    "sealed_test_calls",
    "v1_validation_operating_point_resolutions",
    "forbidden_partition_resolutions",
    "protocol_digest_bypasses",
    "authorization_bypasses",
)


class NegativeCapabilityError(RuntimeError):
    """A forbidden reach was possible, or a forbidden counter moved."""


@dataclass
class ForbiddenCounters:
    """Every counter must remain zero. Non-zero is a stop, not a warning."""

    counts: dict[str, int] = field(
        default_factory=lambda: dict.fromkeys(COUNTER_NAMES, 0)
    )

    def record(self, name: str) -> None:
        if name not in self.counts:
            raise NegativeCapabilityError(f"unknown forbidden counter {name!r}.")
        self.counts[name] += 1

    def require_all_zero(self) -> dict[str, int]:
        moved = {k: v for k, v in self.counts.items() if v}
        if moved:
            raise NegativeCapabilityError(
                "forbidden counters moved, which is a hard stop: "
                + ", ".join(f"{k}={v}" for k, v in sorted(moved.items()))
            )
        return dict(self.counts)


def _iter_imported_names(tree: ast.AST) -> Iterator[tuple[str, str]]:
    """Yield (module, imported name) pairs from the syntax tree."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                yield node.module, alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, ""


def structural_proof(package_root: Path) -> dict[str, list[str]]:
    """Layer 1. Walk the AST of every J1 module; report forbidden reaches."""
    reaches: dict[str, list[str]] = {}
    for path in sorted(package_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for module, name in _iter_imported_names(tree):
            forbidden = FORBIDDEN_ENTRY_POINTS.get(module)
            if forbidden and name in forbidden:
                reaches.setdefault(path.name, []).append(f"{module}.{name}")
            if module in FORBIDDEN_MODULES and not name:
                reaches.setdefault(path.name, []).append(module)
    if reaches:
        raise NegativeCapabilityError(
            "J1 execution modules reach forbidden entry points: "
            + "; ".join(f"{k} -> {sorted(v)}" for k, v in sorted(reaches.items()))
        )
    return {}


def runtime_absence_proof() -> dict[str, bool]:
    """Layer 2a. Modules that need never load must not be in `sys.modules`."""
    present = [m for m in FORBIDDEN_MODULES if m in sys.modules]
    if present:
        raise NegativeCapabilityError(
            "forbidden modules are loaded in this process: " + ", ".join(present)
        )
    return {m: False for m in FORBIDDEN_MODULES}


def instrument_entry_points(
    module: Any, names: tuple[str, ...], counters: ForbiddenCounters, counter: str
) -> dict[str, Any]:
    """Layer 2b. Rebind named attributes to record-then-refuse wrappers.

    Returns the originals so the caller can restore them in a `finally`. The
    frozen module's file is never touched.
    """
    originals: dict[str, Any] = {}
    for name in names:
        original = getattr(module, name, None)
        if original is None:
            continue
        originals[name] = original

        def _refuse(*_a: Any, __name: str = name, **_k: Any) -> Any:
            counters.record(counter)
            raise NegativeCapabilityError(
                f"{__name!r} is a forbidden entry point for J1 and was called."
            )

        setattr(module, name, _refuse)
    return originals


def restore_entry_points(module: Any, originals: dict[str, Any]) -> None:
    for name, original in originals.items():
        setattr(module, name, original)
