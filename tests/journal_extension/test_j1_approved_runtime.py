"""Qualification of J1's approved runtime, established from frozen V1 evidence.

NON-SCIENTIFIC. No physiological data, annotation or reference-episode count is
read, no environment is built or submitted, and nothing here authorizes J1.

**These tests must pass on the CI interpreter too.** CI installs Python 3.11
from unpinned `pyproject` ranges and is deliberately not the scientific
environment, so every claim about the *frozen record* is checked purely, and
only the claim about the *live* interpreter is conditional.
"""

from __future__ import annotations

import ast
import hashlib
import json
import platform
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import approved_runtime as ar
from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.neural.p1_experiment import FROZEN_DEPENDENCY_DIGEST

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
MODULE = Path(preflight.J1_PACKAGE_ROOT) / "approved_runtime.py"


def _lock(relative: str) -> dict:
    return json.loads((REPOSITORY_ROOT / relative).read_text(encoding="utf-8"))


# -- what the frozen V1 locks record ---------------------------------------


@pytest.mark.parametrize("relative", ar.ESTABLISHING_EXPERIMENT_LOCKS)
def test_every_establishing_lock_records_the_same_runtime(relative: str) -> None:
    """Three independent V1 experiments, one environment. If they disagreed,
    there would be no single approved runtime to inherit."""
    environment = _lock(relative)["environment"]
    assert environment["python_version"] == "3.12.6"
    assert (
        environment["dependencies"]["installed_package_count"]
        == ar.APPROVED_PACKAGE_COUNT
    )
    assert _lock(relative)["environment_dependency_digest"] == (
        ar.APPROVED_DEPENDENCY_DIGEST
    )


def test_the_digest_recomputes_from_the_locks_own_package_list() -> None:
    """Pins the method, not just the value.

    The canonical form is V1's: PEP 503 names from `importlib.metadata`, then
    `json.dumps(packages, sort_keys=True, separators=(",", ":"))` over UTF-8.
    A future change to that form would break this before it broke a run.
    """
    packages = _lock(ar.ESTABLISHING_EXPERIMENT_LOCKS[0])["environment"][
        "dependencies"
    ]["installed_packages"]
    canonical = json.dumps(list(packages), sort_keys=True, separators=(",", ":"))
    recomputed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert recomputed == ar.APPROVED_DEPENDENCY_DIGEST


def test_the_approved_fields_match_what_the_locks_record() -> None:
    """Editing a constant here without the evidence moving fails the suite."""
    fields = ar.approved_runtime_fields()
    environment = _lock(ar.ESTABLISHING_EXPERIMENT_LOCKS[0])["environment"]
    assert fields["python_runtime_identity"] == (
        f"CPython-{environment['python_version']}"
    )
    assert fields["dependency_digest"] == ar.APPROVED_DEPENDENCY_DIGEST
    system, _, machine = fields["operating_system_identity"].partition("-")
    assert environment["platform"].startswith(f"{system}-")
    assert machine in environment["platform"]


def test_the_digest_is_imported_and_not_a_second_literal() -> None:
    """A second literal of a frozen digest is a second authority.

    Structural, by AST over the module's own string constants: the value must
    reach J1 by import from where V1 compiled it, never by being retyped.
    """
    assert ar.APPROVED_DEPENDENCY_DIGEST == FROZEN_DEPENDENCY_DIGEST
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    hex64 = [
        text
        for text in literals
        if len(text) == 64 and all(c in "0123456789abcdef" for c in text)
    ]
    assert not hex64, f"a frozen digest is retyped in the module: {hex64}"


def test_only_the_four_determined_fields_are_offered() -> None:
    """The rest need an artifact that does not exist; a placeholder there is
    exactly what a later reader mistakes for authority."""
    assert sorted(ar.approved_runtime_fields()) == [
        "dependency_digest",
        "dependency_lock_identity",
        "operating_system_identity",
        "python_runtime_identity",
    ]


# -- the live interpreter ---------------------------------------------------


def _on_the_approved_runtime() -> bool:
    identity = f"{platform.python_implementation()}-{platform.python_version()}"
    return identity == ar.APPROVED_PYTHON_RUNTIME_IDENTITY


@pytest.mark.skipif(
    not _on_the_approved_runtime(),
    reason=(
        "not the approved scientific interpreter "
        f"({platform.python_implementation()}-{platform.python_version()} "
        f"!= {ar.APPROVED_PYTHON_RUNTIME_IDENTITY}); CI is deliberately a "
        "different environment and cannot check for scientific drift"
    ),
)
def test_the_scientific_environment_has_not_drifted() -> None:
    """On the approved interpreter this is a drift alarm, not a formality."""
    assert ar.require_approved_dependencies() == ar.APPROVED_DEPENDENCY_DIGEST


def test_a_drifted_environment_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Runs everywhere: the refusal path does not need a drifted machine."""
    monkeypatch.setattr(
        ar, "observed_dependency_digest", lambda: "0" * 64
    )
    with pytest.raises(ar.ApprovedRuntimeError, match="not the environment"):
        ar.require_approved_dependencies()


def test_the_refusal_does_not_invite_changing_packages() -> None:
    """V1's own gate ends 'Do not change packages to satisfy this check.'"""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(ar, "observed_dependency_digest", lambda: "0" * 64)
    try:
        with pytest.raises(ar.ApprovedRuntimeError) as caught:
            ar.require_approved_dependencies()
    finally:
        monkeypatch.undo()
    assert "Do not change packages" in str(caught.value)


def test_the_approved_runtime_is_not_the_ci_runtime() -> None:
    """Recorded as a fact, because a green badge says nothing about evidence."""
    workflow = (REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert 'python-version: "3.11"' in workflow
    assert ar.APPROVED_PYTHON_RUNTIME_IDENTITY == "CPython-3.12.6"
