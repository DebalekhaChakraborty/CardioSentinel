"""Qualification of the J1 environment artifact build authority.

NON-SCIENTIFIC QUALIFICATION FIXTURE. Every manifest, builder and digest below
is fabricated and describes no real artifact. **No image is built, no artifact
digest is promoted, no environment authority is created, and no authorization
field is populated.** J1 remains `PRE-REGISTERED — NOT AUTHORIZED`.

Synthetic artifacts live only here. Nothing is written under a canonical
scientific run path.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.approved_runtime import (
    APPROVED_DEPENDENCY_DIGEST,
)
from cardiosentinel.journal_extension.j1.build_authority import (
    BIT_REPRODUCIBLE,
    BUILD_AUTHORITY_FIELDS,
    MANIFEST_DIGEST_FIELDS,
    MANIFEST_EXCLUDED_FROM_DIGEST,
    MANIFEST_FIELDS,
    NOT_REPRODUCIBLE_DOCUMENTED,
    BuildAuthorityError,
    BuilderDeclaration,
    BuilderState,
    J1EnvironmentBuildManifest,
    canonical_manifest_serialization,
    manifest_sha256,
    require_build_authority_declaration,
    verify_build_manifest,
    verify_builder,
    verify_reproducible_pair,
)

MODULE = Path(preflight.J1_PACKAGE_ROOT) / "build_authority.py"

ARTIFACT = "sha256:" + "a" * 64
BASE_IMAGE = "registry.invalid/synthetic/base@sha256:" + "b" * 64


def _builder(**overrides: object) -> BuilderDeclaration:
    base: dict[str, object] = {
        "builder_id": "synthetic-build-service-1",
        "builder_environment_identity": "synthetic-builder-env@sha256:" + "c" * 64,
        "build_tool_version": "synthetic-buildkit-0.0.0",
        "container_runtime_version": "synthetic-runtime-0.0.0",
        "build_command_identity": "synthetic-build --no-cache",
        "provenance_output": "s3://synthetic-provenance/j1/build-1.json",
    }
    base.update(overrides)
    return BuilderDeclaration(**base)  # type: ignore[arg-type]


def _manifest(**overrides: object) -> J1EnvironmentBuildManifest:
    base: dict[str, object] = {
        "build_id": "synthetic-build-1",
        "source_commit": "0" * 40,
        "runtime_authority_id": "j1-approved-runtime-v1",
        "dependency_digest": APPROVED_DEPENDENCY_DIGEST,
        "base_image_digest": BASE_IMAGE,
        "builder_identity": "synthetic-build-service-1",
        "build_configuration_digest": "d" * 64,
        "output_artifact_digest": ARTIFACT,
        "provenance_reference": "s3://synthetic-provenance/j1/build-1.json",
        "creation_timestamp": "2026-09-02T00:00:00Z",
    }
    base.update(overrides)
    return J1EnvironmentBuildManifest(**base)  # type: ignore[arg-type]


def _verify(**overrides: object):
    return verify_build_manifest(
        _manifest(**overrides), builder=_builder(), worktree_clean=True
    )


# -- the chain qualifies, and qualifying is not authorizing -----------------


def test_a_complete_chain_qualifies_without_authorizing_anything() -> None:
    verified = _verify()
    assert verified.builder.state is BuilderState.QUALIFIED
    assert verified.builder.state is not BuilderState.AUTHORIZED
    assert verified.as_attestation()["environment_authority_submitted"] == "false"


def test_the_builder_ladder_stops_short_of_authorized() -> None:
    reachable = BuilderState.reachable_without_human_authorization()
    assert BuilderState.AUTHORIZED not in reachable
    assert reachable == (BuilderState.CANDIDATE, BuilderState.QUALIFIED)


def test_a_builder_may_not_declare_itself_authorized() -> None:
    """The thing being vouched for cannot also be the voucher."""
    with pytest.raises(BuildAuthorityError, match="may not assert AUTHORIZED"):
        _builder(state=BuilderState.AUTHORIZED)


def test_no_code_path_promotes_a_builder_to_authorized() -> None:
    """Structural, by AST: a text scan would match the enum and this docstring."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    # The module may *name* the state -- the enum defines it and two refusals
    # cite it -- but no return or assignment may ever produce it.
    produced = [
        inner.lineno
        for node in ast.walk(tree)
        if isinstance(node, (ast.Return, ast.Assign, ast.AnnAssign))
        for inner in ast.walk(node)
        if isinstance(inner, ast.Attribute)
        and inner.attr == "AUTHORIZED"
        and isinstance(inner.value, ast.Name)
        and inner.value.id == "BuilderState"
    ]
    assert not produced, (
        f"BuilderState.AUTHORIZED is produced at lines {produced}; no code "
        "path may promote a builder"
    )


def test_verification_has_no_bypass_parameter() -> None:
    signature = inspect.signature(verify_build_manifest)
    for forbidden in ("force", "dev_mode", "skip_provenance", "allow_dirty"):
        assert forbidden not in signature.parameters


# -- no mutable inputs, specification section 10 ---------------------------


@pytest.mark.parametrize(
    "reference",
    [
        "cardiosentinel:j1-latest",
        "registry.invalid/base:latest",
        "registry.invalid/base",
        "registry.invalid/base@sha256:tooshort",
        "sha256:" + "b" * 64,
    ],
)
def test_a_base_image_not_addressed_by_digest_is_refused(reference: str) -> None:
    with pytest.raises(BuildAuthorityError, match="addressed by digest"):
        _verify(base_image_digest=reference)


@pytest.mark.parametrize(
    "reference",
    [
        "cardiosentinel:j1-latest",
        "j1-latest",
        "sha256:" + "a" * 63,
        "SHA256:" + "a" * 64,
        "registry.invalid/j1@sha256:" + "a" * 64,
    ],
)
def test_a_tag_is_not_an_artifact_digest(reference: str) -> None:
    """`cardiosentinel:j1-latest` is a mutable pointer, not authority."""
    with pytest.raises(BuildAuthorityError):
        _verify(output_artifact_digest=reference)


@pytest.mark.parametrize("commit", ["abc1234", "", "HEAD", "v1.0.0", "A" * 40])
def test_a_source_that_is_not_one_immutable_commit_is_refused(commit: str) -> None:
    with pytest.raises(BuildAuthorityError):
        _verify(source_commit=commit)


def test_a_dirty_worktree_is_refused() -> None:
    """What was built is then not what the commit describes."""
    with pytest.raises(BuildAuthorityError, match="worktree was dirty"):
        verify_build_manifest(
            _manifest(), builder=_builder(), worktree_clean=False
        )


@pytest.mark.parametrize("ref", ["latest", "main", "HEAD", "nightly", "stable"])
def test_a_floating_source_ref_is_refused(ref: str) -> None:
    with pytest.raises(BuildAuthorityError, match="floating ref"):
        verify_build_manifest(
            _manifest(), builder=_builder(), worktree_clean=True, source_ref=ref
        )


def test_the_build_may_not_redefine_the_runtime_authority() -> None:
    """It may consume the qualified runtime. It may not define a new one."""
    with pytest.raises(BuildAuthorityError, match="not the approved one"):
        _verify(dependency_digest="e" * 64)


def test_the_build_must_name_the_runtime_authority_it_consumes() -> None:
    with pytest.raises(BuildAuthorityError):
        _verify(runtime_authority_id="   ")


def test_an_unpinned_build_configuration_is_refused() -> None:
    with pytest.raises(BuildAuthorityError, match="build_configuration_digest"):
        _verify(build_configuration_digest="default")


# -- no local self-promotion, specification section 10 ---------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("builder_id", "current-machine"),
        ("builder_id", "developer-laptop-3"),
        ("builder_environment_identity", "/home/dev/build"),
        ("build_tool_version", "unknown"),
        ("provenance_output", "localhost:9000/provenance"),
        ("builder_id", "TBD"),
    ],
)
def test_a_local_machine_cannot_become_the_build_authority(
    field: str, value: str
) -> None:
    with pytest.raises(BuildAuthorityError, match="mutable local state"):
        verify_builder(_builder(**{field: value}))


def test_running_the_command_is_not_authority() -> None:
    """The refusal says so, because the reason is the point."""
    with pytest.raises(BuildAuthorityError) as caught:
        verify_builder(_builder(builder_id="my-machine"))
    assert "candidate builder" in str(caught.value)


# -- no missing provenance, specification section 10 -----------------------


@pytest.mark.parametrize("field", MANIFEST_FIELDS)
def test_every_manifest_field_is_required(field: str) -> None:
    with pytest.raises(BuildAuthorityError, match="incomplete"):
        _verify(**{field: "   "})


@pytest.mark.parametrize("field", ["builder_id", "provenance_output"])
def test_a_builder_that_will_not_identify_itself_is_refused(field: str) -> None:
    with pytest.raises(BuildAuthorityError, match="blank"):
        verify_builder(_builder(**{field: ""}))


def test_a_manifest_naming_a_different_builder_is_refused() -> None:
    """An artifact's manifest and its builder's declaration must be one story."""
    with pytest.raises(BuildAuthorityError, match="but the declaration is from"):
        verify_build_manifest(
            _manifest(builder_identity="someone-else"),
            builder=_builder(),
            worktree_clean=True,
        )


@pytest.mark.parametrize("field", BUILD_AUTHORITY_FIELDS)
def test_no_build_authority_field_may_silently_default(field: str) -> None:
    document = dict.fromkeys(BUILD_AUTHORITY_FIELDS, "synthetic")
    del document[field]
    with pytest.raises(BuildAuthorityError, match="silently default"):
        require_build_authority_declaration(document)


# -- the manifest digest ---------------------------------------------------


def test_the_canonical_form_is_field_ordered_and_newline_terminated() -> None:
    blob = canonical_manifest_serialization(_manifest())
    assert blob.endswith(b"\n") and not blob.endswith(b"\n\n")
    emitted = [
        line.split("=", 1)[0]
        for line in blob.decode("utf-8").rstrip("\n").split("\n")
    ]
    assert emitted == list(MANIFEST_DIGEST_FIELDS)


@pytest.mark.parametrize("field", MANIFEST_DIGEST_FIELDS)
def test_every_digest_bearing_field_changes_the_digest(field: str) -> None:
    assert manifest_sha256(_manifest(**{field: "altered-value"})) != (
        manifest_sha256(_manifest())
    )


@pytest.mark.parametrize("field", MANIFEST_EXCLUDED_FROM_DIGEST)
def test_the_timestamp_never_reaches_the_digest(field: str) -> None:
    """If the moment of writing were hashed, no two builds could ever agree
    and the reproducibility contract would be untestable by construction."""
    assert manifest_sha256(_manifest(**{field: "2099-01-01T00:00:00Z"})) == (
        manifest_sha256(_manifest())
    )


@pytest.mark.parametrize("separator", ["\n", "\r"])
def test_a_manifest_field_may_not_inject_a_line(separator: str) -> None:
    """The same canonical-form rule the environment authority froze."""
    with pytest.raises(Exception, match="canonical-form structure"):
        canonical_manifest_serialization(
            _manifest(build_id=f"one{separator}source_commit=x")
        )


def test_the_canonical_rule_is_imported_not_restated() -> None:
    """A second canonical serialization would be a second authority."""
    from cardiosentinel.journal_extension.j1 import build_authority
    from cardiosentinel.journal_extension.j1.environment_authority import (
        reject_uncanonical,
    )

    assert build_authority.reject_uncanonical is reject_uncanonical


# -- the reproducibility contract, specification section 7 -----------------


def test_identical_inputs_and_identical_artifacts_agree() -> None:
    result = verify_reproducible_pair(_manifest(), _manifest(build_id="b2"))
    assert result["reproducible"] is True


def test_identical_inputs_and_different_artifacts_refuse() -> None:
    """Neither finding is reconciled by choosing one digest."""
    with pytest.raises(BuildAuthorityError, match="claims to be bit-reproducible"):
        verify_reproducible_pair(
            _manifest(),
            _manifest(output_artifact_digest="sha256:" + "f" * 64),
        )


def test_a_documented_divergence_is_permitted_with_a_reason() -> None:
    result = verify_reproducible_pair(
        _manifest(),
        _manifest(output_artifact_digest="sha256:" + "f" * 64),
        reproducibility_class=NOT_REPRODUCIBLE_DOCUMENTED,
        non_reproducibility_reason="synthetic: embedded build timestamp",
    )
    assert result["reproducible"] is False


def test_an_undocumented_divergence_is_refused() -> None:
    with pytest.raises(BuildAuthorityError, match="must document why"):
        verify_reproducible_pair(
            _manifest(),
            _manifest(output_artifact_digest="sha256:" + "f" * 64),
            reproducibility_class=NOT_REPRODUCIBLE_DOCUMENTED,
        )


def test_builds_with_different_inputs_say_nothing_about_reproducibility() -> None:
    with pytest.raises(BuildAuthorityError, match="do not share the contract"):
        verify_reproducible_pair(_manifest(), _manifest(source_commit="1" * 40))


def test_the_default_class_is_the_strict_one() -> None:
    signature = inspect.signature(verify_reproducible_pair)
    assert signature.parameters["reproducibility_class"].default == BIT_REPRODUCIBLE


# -- nothing here is an environment authority ------------------------------


def test_this_package_creates_no_environment_authority_record() -> None:
    """Structural, by AST over the build authority module.

    A build manifest is provenance for an artifact. Turning one into an
    `EnvironmentAuthorityRecord` is the step this task does not take.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            assert name not in {
                "EnvironmentAuthorityRecord",
                "verify_authority_record",
                "environment_sha256",
            }, f"the build authority constructs {name!r} at line {node.lineno}"


def test_a_verified_manifest_is_still_not_a_submitted_environment() -> None:
    attestation = _verify().as_attestation()
    assert attestation["environment_authority_submitted"] == "false"
    assert "environment_sha256" not in attestation
