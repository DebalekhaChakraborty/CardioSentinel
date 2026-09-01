"""Qualification of the J1 environment authority.

NON-SCIENTIFIC QUALIFICATION FIXTURE. Every record below is fabricated. No real
environment is described, none is promoted, and nothing here authorizes J1.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.environment_authority import (
    EnvironmentAuthorityError,
    EnvironmentAuthorityRecord,
    EnvironmentAuthorityState,
    RuntimeMismatch,
    canonical_serialization,
    environment_sha256,
    verify_authority_record,
    verify_runtime_matches,
)
from cardiosentinel.journal_extension.j1.environment_authority import record as rec

AUTHORITY_PACKAGE = (
    Path(preflight.J1_PACKAGE_ROOT) / "environment_authority"
)


def _record(**overrides: object) -> EnvironmentAuthorityRecord:
    base: dict[str, object] = {
        "environment_id": "synthetic-j1-env",
        "environment_version": "1",
        "creation_method": "reproducible-container-build",
        "base_image_identity": "synthetic-base@sha256:aaaa",
        "operating_system_identity": "Linux-x86_64",
        "python_runtime_identity": "CPython-3.12.6",
        "dependency_lock_identity": "synthetic-lock-v1",
        "dependency_digest": "b" * 64,
        "hardware_profile": "cpu-only",
        "accelerator_identity": "none",
        "container_image_digest": "sha256:" + "c" * 64,
        "immutable_artifact_location": "oci://synthetic/registry@sha256:dddd",
        "creation_timestamp": "2026-09-01T00:00:00Z",
        "owner_provenance_identity": "synthetic-owner",
        "runtime_dependencies": {"numpy": "2.3.2", "scipy": "1.0.0"},
    }
    base.update(overrides)
    return EnvironmentAuthorityRecord(**base)  # type: ignore[arg-type]


def _exists(_location: str) -> bool:
    return True


# -- canonical serialization and digest -------------------------------------


def test_the_canonical_form_is_field_ordered_and_newline_terminated() -> None:
    blob = canonical_serialization(_record())
    assert blob.endswith(b"\n") and not blob.endswith(b"\n\n")
    lines = blob.decode("utf-8").rstrip("\n").split("\n")
    emitted = [line.split("=", 1)[0] for line in lines]
    assert emitted == [*rec.ENVIRONMENT_RECORD_FIELDS, "runtime_dependencies"]


def test_excluded_fields_never_reach_the_digest() -> None:
    """A timestamp or owner would bind the digest to where it was written."""
    baseline = environment_sha256(_record())
    for name, value in (
        ("creation_timestamp", "2099-01-01T00:00:00Z"),
        ("owner_provenance_identity", "someone-else"),
    ):
        assert environment_sha256(_record(**{name: value})) == baseline


def test_every_digest_bearing_field_changes_the_digest() -> None:
    baseline = environment_sha256(_record())
    for name in rec.ENVIRONMENT_RECORD_FIELDS:
        altered = environment_sha256(_record(**{name: "altered-value"}))
        assert altered != baseline, f"{name} must participate in the digest"


def test_dependency_mapping_is_order_independent() -> None:
    a = environment_sha256(_record(runtime_dependencies={"a": "1", "b": "2"}))
    b = environment_sha256(_record(runtime_dependencies={"b": "2", "a": "1"}))
    assert a == b


def test_padded_values_are_refused() -> None:
    with pytest.raises(EnvironmentAuthorityError, match="whitespace"):
        canonical_serialization(_record(environment_id=" synthetic "))


# -- record verification ----------------------------------------------------


def test_a_valid_authority_qualifies() -> None:
    record = _record()
    verified = verify_authority_record(
        record, declared_sha256=environment_sha256(record), artifact_exists=_exists
    )
    assert verified.state is EnvironmentAuthorityState.QUALIFIED
    assert verified.state is not EnvironmentAuthorityState.AUTHORIZED


def test_a_modified_digest_fails() -> None:
    with pytest.raises(EnvironmentAuthorityError, match="digest mismatch"):
        verify_authority_record(
            _record(), declared_sha256="0" * 64, artifact_exists=_exists
        )


def test_a_missing_artifact_fails() -> None:
    record = _record()
    with pytest.raises(EnvironmentAuthorityError, match="does not exist"):
        verify_authority_record(
            record,
            declared_sha256=environment_sha256(record),
            artifact_exists=lambda _l: False,
        )


@pytest.mark.parametrize("name", rec.ENVIRONMENT_RECORD_FIELDS)
def test_no_field_may_be_blank(name: str) -> None:
    record = _record(**{name: ""})
    with pytest.raises(EnvironmentAuthorityError, match="incomplete"):
        verify_authority_record(
            record, declared_sha256="0" * 64, artifact_exists=_exists
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("immutable_artifact_location", "/home/dev/env"),
        ("base_image_identity", "localhost/scratch"),
        ("creation_method", "current-machine snapshot"),
        ("hardware_profile", "developer-laptop"),
        ("container_image_digest", "unknown"),
    ],
)
def test_mutable_local_state_cannot_become_authority(field: str, value: str) -> None:
    record = _record(**{field: value})
    with pytest.raises(EnvironmentAuthorityError, match="mutable local state"):
        verify_authority_record(
            record,
            declared_sha256=environment_sha256(record),
            artifact_exists=_exists,
        )


# -- runtime verification ---------------------------------------------------


def _qualified() -> object:
    record = _record()
    return verify_authority_record(
        record, declared_sha256=environment_sha256(record), artifact_exists=_exists
    )


def test_a_matching_runtime_verifies() -> None:
    proof = verify_runtime_matches(
        _qualified(),
        dependency_digest="b" * 64,
        observed={
            "python_runtime_identity": "CPython-3.12.6",
            "operating_system_identity": "Linux-x86_64",
        },
    )
    assert proof["environment_authority_verified"] is True


@pytest.mark.parametrize(
    "observed",
    [
        {"python_runtime_identity": "CPython-3.9.0",
         "operating_system_identity": "Linux-x86_64"},
        {"python_runtime_identity": "CPython-3.12.6",
         "operating_system_identity": "Darwin-arm64"},
    ],
)
def test_a_runtime_mismatch_refuses(observed: dict[str, str]) -> None:
    with pytest.raises(RuntimeMismatch, match="mismatch"):
        verify_runtime_matches(
            _qualified(), dependency_digest="b" * 64, observed=observed
        )


def test_a_dependency_digest_mismatch_refuses() -> None:
    with pytest.raises(RuntimeMismatch, match="dependency digest"):
        verify_runtime_matches(
            _qualified(),
            dependency_digest="f" * 64,
            observed={
                "python_runtime_identity": "CPython-3.12.6",
                "operating_system_identity": "Linux-x86_64",
            },
        )


# -- negative capability: no machine-derived authority ----------------------


def test_no_production_path_derives_authority_from_the_machine() -> None:
    """Structural, by AST -- a text scan would match this test's own names.

    `observe_runtime` may *read* platform facts for comparison, but nothing in
    the package may feed hostname, username, home directory or a filesystem
    scan into a digest.
    """
    forbidden_calls = {
        ("socket", "gethostname"),
        ("os", "getlogin"),
        ("getpass", "getuser"),
        ("pathlib", "home"),
        ("os.path", "expanduser"),
    }
    forbidden_names = {"gethostname", "getlogin", "getuser", "expanduser", "walk"}
    for path in sorted(AUTHORITY_PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = getattr(func, "attr", None) or getattr(func, "id", None)
                assert name not in forbidden_names, (
                    f"{path.name} calls {name!r}; environment authority must "
                    "never be derived from machine state"
                )
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    assert (node.module, alias.name) not in forbidden_calls


def test_the_digest_is_not_a_function_of_live_machine_state() -> None:
    """Same record, same digest, whatever the interpreter reports about itself."""
    record = _record()
    first = environment_sha256(record)
    import platform  # noqa: PLC0415 - deliberately imported inside the test

    _ = platform.node()
    assert environment_sha256(record) == first


# -- preflight integration --------------------------------------------------


def test_preflight_refuses_without_an_environment_authority() -> None:
    """Authorization is checked first, so this is the ordering it proves."""
    with pytest.raises(preflight.PreflightError, match="authorization absent"):
        preflight.run_preflight(
            authorization_document=None,
            environment_authority=None,
            repository_root=Path(preflight.J1_PACKAGE_ROOT).parents[3],
        )


def test_there_is_no_environment_bypass_parameter() -> None:
    import inspect

    signature = inspect.signature(preflight.run_preflight)
    for forbidden in ("dev_mode", "force_environment", "skip_env_check"):
        assert forbidden not in signature.parameters


def test_authorized_is_not_reachable_from_this_package() -> None:
    reachable = EnvironmentAuthorityState.reachable_without_human_authorization()
    assert EnvironmentAuthorityState.AUTHORIZED not in reachable
    assert reachable == (
        EnvironmentAuthorityState.CANDIDATE,
        EnvironmentAuthorityState.QUALIFIED,
    )
