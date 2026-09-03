"""The import boundary that stopped the first authorized controlled build.

Run 33800630377 -- the single dispatch under `J1-ENV-BUILDER-AUTH-001` -- died
in its authorization gate with `ModuleNotFoundError: No module named 'numpy'`,
before verifying anything and before any qualification claim existed. The gate
job installs base dependencies only, deliberately, because the gate is not the
scientific environment. `approved_runtime` reached through into
`cardiosentinel.neural` at module scope anyway.

**Every test in this module existed in spirit before and passed**, because they
all ran inside the 335-package `tactics` interpreter, where numpy is present.
That is the whole lesson: a suite executed in the rich environment is evidence
about the rich environment. The tests here run the real import in a *stripped*
interpreter and inspect the import graph structurally, so neither can be
satisfied by the fixture's own surroundings.

**No build is dispatched, no authorization is created, and no scientific data is
read.**
"""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.approved_runtime import (
    APPROVED_DEPENDENCY_DIGEST,
    APPROVED_PACKAGE_COUNT,
    ESTABLISHING_EXPERIMENT_LOCKS,
    ApprovedRuntimeError,
    _resolve_approved_dependency_digest,
    approved_runtime_fields,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
APPROVED_RUNTIME_SOURCE = (
    REPOSITORY_ROOT
    / "src/cardiosentinel/journal_extension/j1/approved_runtime.py"
)
P1_EXPERIMENT_SOURCE = (
    REPOSITORY_ROOT / "src/cardiosentinel/neural/p1_experiment.py"
)

#: Packages the authorization gate's interpreter does not have and must not need.
SCIENTIFIC_PACKAGES = ("numpy", "scipy", "sklearn", "torch", "pandas", "wfdb")

EXPECTED_DIGEST = "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a"


# -- the frozen dependency authority, resolved rather than copied ----------


def test_all_establishing_locks_agree_on_the_approved_digest() -> None:
    """Three locks, one answer. The resolution reads all of them."""
    digests = set()
    for relative in ESTABLISHING_EXPERIMENT_LOCKS:
        dependencies = json.loads(
            (REPOSITORY_ROOT / relative).read_text(encoding="utf-8")
        )["environment"]["dependencies"]
        assert dependencies["installed_package_count"] == APPROVED_PACKAGE_COUNT
        assert len(dependencies["installed_packages"]) == APPROVED_PACKAGE_COUNT
        digests.add(dependencies["installed_packages_sha256"])
    assert len(digests) == 1
    assert digests == {EXPECTED_DIGEST}
    assert APPROVED_DEPENDENCY_DIGEST == EXPECTED_DIGEST


def test_disagreeing_locks_are_a_hard_refusal(tmp_path: Path) -> None:
    """No majority vote, no first-file-wins, no fallback literal.

    Three locks that disagree about which environment the scaffold was built in
    mean the question has no answer. Answering it anyway would invent one.
    """
    for index, relative in enumerate(ESTABLISHING_EXPERIMENT_LOCKS):
        source = REPOSITORY_ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        document = json.loads(source.read_text(encoding="utf-8"))
        if index == 1:
            document["environment"]["dependencies"][
                "installed_packages_sha256"
            ] = "f" * 64
        target.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ApprovedRuntimeError, match="do not agree"):
        _resolve_approved_dependency_digest(tmp_path)


def test_a_missing_lock_is_a_refusal_not_a_default(tmp_path: Path) -> None:
    with pytest.raises(ApprovedRuntimeError, match="is missing"):
        _resolve_approved_dependency_digest(tmp_path)


def test_a_lock_with_the_wrong_population_is_refused(tmp_path: Path) -> None:
    for relative in ESTABLISHING_EXPERIMENT_LOCKS:
        source = REPOSITORY_ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        document = json.loads(source.read_text(encoding="utf-8"))
        document["environment"]["dependencies"]["installed_package_count"] = 334
        target.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ApprovedRuntimeError, match="the approved set is"):
        _resolve_approved_dependency_digest(tmp_path)


def test_the_resolved_digest_agrees_with_v1s_compiled_constant() -> None:
    """Parsed out of V1's source with `ast`, never imported.

    Importing `p1_experiment` to read this constant is exactly what broke the
    gate. The constant is a string literal, so the syntax tree carries it, and
    the agreement can be checked without numpy or torch being present.

    This is a verification test, not a second production authority path.
    """
    tree = ast.parse(P1_EXPERIMENT_SOURCE.read_text(encoding="utf-8"))
    found: list[str] = []
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == "FROZEN_DEPENDENCY_DIGEST":
                value = node.value
                assert isinstance(value, ast.Constant), (
                    "FROZEN_DEPENDENCY_DIGEST is not a literal; the AST check "
                    "cannot resolve it and must not guess"
                )
                found.append(str(value.value))
    assert len(found) == 1, f"expected exactly one assignment, found {len(found)}"
    assert found[0] == APPROVED_DEPENDENCY_DIGEST


# -- the import graph, inspected structurally ------------------------------


def _module_scope_imports(source: Path) -> set[str]:
    """Names imported at module scope. Nested imports are deliberately ignored."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_approved_runtime_has_no_scientific_module_scope_imports() -> None:
    """The guard against silently recreating the failure.

    AST rather than grep: a comment or a docstring mentioning `numpy` -- and
    this module's docstring mentions it repeatedly, explaining the incident --
    would defeat a text search. Only real import statements count.
    """
    imported = _module_scope_imports(APPROVED_RUNTIME_SOURCE)
    forbidden = {
        name
        for name in imported
        if name.startswith("cardiosentinel.neural")
        or name.split(".")[0] in SCIENTIFIC_PACKAGES
    }
    assert not forbidden, f"module-scope scientific imports returned: {forbidden}"


def test_the_lazy_import_is_still_present_where_it_belongs() -> None:
    """`observed_dependency_digest` may need the stack; it must load it itself."""
    tree = ast.parse(APPROVED_RUNTIME_SOURCE.read_text(encoding="utf-8"))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    observer = functions["observed_dependency_digest"]
    nested = {
        node.module
        for node in ast.walk(observer)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "cardiosentinel.neural.provenance" in nested


# -- the process boundary, exercised for real ------------------------------


def _stripped(*arguments: str) -> subprocess.CompletedProcess[str]:
    """Run in an interpreter with normal site packages disabled.

    `-S` is what makes this a real test rather than a restatement of the source.
    The previous suite ran the gate inside the 335-package interpreter, where
    the defect was invisible.
    """
    return subprocess.run(
        [sys.executable, "-S", *arguments],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
        env={
            "PYTHONPATH": str(REPOSITORY_ROOT / "src"),
            "PATH": "/usr/bin:/bin",
            "HOME": str(REPOSITORY_ROOT),
        },
    )


def test_the_stripped_interpreter_really_lacks_numpy() -> None:
    """Prove the negative first, or the positive proves nothing."""
    completed = _stripped(
        "-c",
        "import importlib.util,sys;"
        "print(';'.join(n for n in "
        f"{SCIENTIFIC_PACKAGES!r} if importlib.util.find_spec(n) is not None))",
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "", (
        f"scientific packages reachable in the stripped interpreter: "
        f"{completed.stdout.strip()}"
    )


def test_the_gate_module_imports_without_the_scientific_stack() -> None:
    """The exact import that failed in run 33800630377."""
    completed = _stripped(
        "-c",
        "import sys;"
        "import cardiosentinel.journal_extension.j1.builder_authorization;"
        "from cardiosentinel.journal_extension.j1.approved_runtime import "
        "approved_runtime_fields;"
        "print(approved_runtime_fields()['dependency_digest']);"
        "print('neural' if any(m.startswith('cardiosentinel.neural') "
        "for m in sys.modules) else 'clean');"
        "print('numpy' if 'numpy' in sys.modules else 'no-numpy')",
    )
    assert completed.returncode == 0, completed.stderr
    assert "ModuleNotFoundError" not in completed.stderr
    lines = completed.stdout.split()
    assert lines[0] == APPROVED_DEPENDENCY_DIGEST
    assert lines[1] == "clean"
    assert lines[2] == "no-numpy"


def test_the_gate_cli_runs_without_the_scientific_stack() -> None:
    """The process boundary the workflow actually crosses.

    The gate's verdict depends on whether an authorization is present, and this
    test deliberately does not care which. What it proves is that the gate
    *reaches* its own logic instead of dying during import -- the failure that
    made run 33800630377's verdict meaningless.
    """
    completed = _stripped(
        "-m",
        "cardiosentinel.journal_extension.j1.builder_authorization",
        "--repository-root",
        str(REPOSITORY_ROOT),
        "--running-workflow-ref",
        "owner/repo/.github/workflows/j1-environment-artifact-build.yml@x",
        "--running-commit",
        "0" * 40,
    )
    combined = completed.stdout + completed.stderr
    assert "ModuleNotFoundError" not in combined, combined
    for package in SCIENTIFIC_PACKAGES:
        assert f"No module named '{package}'" not in combined
    # It reached the authorization logic: either it verified, or it refused in
    # the gate's own words. Both are the gate deciding; neither is an import
    # crash.
    reached = completed.returncode == 0 or "builder authorization" in combined
    assert reached, combined


def test_approved_runtime_fields_needs_no_scientific_stack() -> None:
    """Sanity in this interpreter too, so the contract is stated in both places."""
    fields = approved_runtime_fields()
    assert fields["dependency_digest"] == APPROVED_DEPENDENCY_DIGEST
    assert fields["dependency_lock_identity"].endswith(
        f"{APPROVED_PACKAGE_COUNT}-packages"
    )
    assert importlib.util.find_spec("numpy") is not None, (
        "this interpreter is expected to have numpy; the stripped-interpreter "
        "tests above are the ones that prove independence from it"
    )
