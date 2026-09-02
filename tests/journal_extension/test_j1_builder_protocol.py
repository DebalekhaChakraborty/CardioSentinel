"""Qualification of the J1 builder selection and controlled build protocol.

NON-SCIENTIFIC QUALIFICATION FIXTURE. **No image is built, no artifact digest is
produced or promoted, no builder is authorized, no environment record exists,
and no scientific data is touched.** Every manifest below is synthetic.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.approved_runtime import (
    APPROVED_DEPENDENCY_DIGEST,
    APPROVED_PACKAGE_COUNT,
    APPROVED_PYTHON_RUNTIME_IDENTITY,
)
from cardiosentinel.journal_extension.j1.builder_protocol import (
    ARTIFACT_MEDIA_TYPE,
    FIRST_PARTY_SOURCE,
    INDEX_MEDIA_TYPES,
    PYPI,
    PYTORCH_CPU_INDEX,
    REQUIRED_BUILD_CONFIGURATION_INPUTS,
    TARGET_ACCELERATOR,
    TARGET_COMPUTE_DEVICE,
    TARGET_PLATFORM,
    BaseImageAuthority,
    BuilderProtocolError,
    ControlledBuilderIdentity,
    build_configuration_digest,
    classify_dependency_source,
    derived_build_input,
    derived_input_digest,
    require_artifact_identity_separate_from_location,
    require_base_image_authority,
    require_declared_platform,
    require_derived_input_matches_authority,
    require_host_does_not_redefine_target,
    require_independent_builds,
    require_pinned_action,
    require_pinned_dependency_specifier,
    require_single_platform_manifest,
    require_specific_builder_identity,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
MODULE = Path(preflight.J1_PACKAGE_ROOT) / "builder_protocol.py"

LOCK = (
    REPOSITORY_ROOT
    / "reproducibility/demo_bundle/runs/phase3b2-architecture-v1"
    / "B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json"
)


def _identity(**overrides: object) -> ControlledBuilderIdentity:
    base: dict[str, object] = {
        "provider": "github-actions",
        "workflow_repository": "DebalekhaChakraborty/CardioSentinel",
        "workflow_path": ".github/workflows/j1-environment-build.yml",
        "workflow_commit": "0" * 40,
        "runner_class": "ubuntu-24.04",
    }
    base.update(overrides)
    return ControlledBuilderIdentity(**base)  # type: ignore[arg-type]


def _packages() -> list[dict[str, str]]:
    return json.loads(LOCK.read_text(encoding="utf-8"))["environment"][
        "dependencies"
    ]["installed_packages"]


# -- builder identity is exact, not generic --------------------------------


def test_a_specific_workflow_at_a_commit_qualifies() -> None:
    identity = require_specific_builder_identity(_identity())
    assert identity.builder_id.endswith("#ubuntu-24.04")
    assert ".github/workflows/" in identity.builder_id


@pytest.mark.parametrize(
    "repository", ["GitHub Actions", "github", "CI", "the builder", "pipeline"]
)
def test_a_provider_name_is_not_a_builder_identity(repository: str) -> None:
    """Authorizing it would authorize every future workflow it covers."""
    with pytest.raises(BuilderProtocolError, match="names a provider"):
        require_specific_builder_identity(_identity(workflow_repository=repository))


@pytest.mark.parametrize("ref", ["main", "v1", "HEAD", "abc1234", ""])
def test_a_workflow_referenced_by_a_mutable_ref_is_refused(ref: str) -> None:
    """The thing authorized and the thing that runs must be one object."""
    with pytest.raises(BuilderProtocolError):
        require_specific_builder_identity(_identity(workflow_commit=ref))


@pytest.mark.parametrize(
    "field", ["provider", "workflow_path", "runner_class", "workflow_repository"]
)
def test_no_builder_identity_field_may_be_blank(field: str) -> None:
    with pytest.raises(BuilderProtocolError):
        require_specific_builder_identity(_identity(**{field: "   "}))


# -- floating action versions refuse ---------------------------------------


def test_a_commit_pinned_action_is_accepted() -> None:
    pinned = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
    assert require_pinned_action(pinned) == pinned


@pytest.mark.parametrize(
    "uses",
    [
        "actions/checkout@v4",
        "actions/checkout@main",
        "actions/checkout@master",
        "docker/build-push-action@v6",
        "actions/checkout",
    ],
)
def test_a_floating_action_version_is_refused(uses: str) -> None:
    with pytest.raises(BuilderProtocolError):
        require_pinned_action(uses)


# -- host runtime cannot redefine target runtime ---------------------------


def test_a_differing_builder_host_runtime_is_permitted() -> None:
    """CI runs 3.11 today. The runner orchestrates; it does not substitute."""
    require_host_does_not_redefine_target(
        host_python_identity="CPython-3.11.16",
        target_python_identity=APPROVED_PYTHON_RUNTIME_IDENTITY,
    )


def test_the_host_runtime_may_not_become_the_target() -> None:
    with pytest.raises(BuilderProtocolError, match="not the approved one"):
        require_host_does_not_redefine_target(
            host_python_identity="CPython-3.11.16",
            target_python_identity="CPython-3.11.16",
        )


# -- OCI artifact type is explicit -----------------------------------------


def test_the_frozen_artifact_object_is_a_single_platform_manifest() -> None:
    assert require_single_platform_manifest(ARTIFACT_MEDIA_TYPE) == ARTIFACT_MEDIA_TYPE


@pytest.mark.parametrize("media_type", INDEX_MEDIA_TYPES)
def test_an_image_index_is_not_the_artifact_object(media_type: str) -> None:
    """A tag commonly resolves to an index; its digest names a list."""
    with pytest.raises(BuilderProtocolError, match="image index"):
        require_single_platform_manifest(media_type)


@pytest.mark.parametrize(
    "media_type",
    ["application/vnd.docker.distribution.manifest.v2+json", "application/json"],
)
def test_another_manifest_media_type_is_refused(media_type: str) -> None:
    with pytest.raises(BuilderProtocolError, match="not the frozen artifact"):
        require_single_platform_manifest(media_type)


# -- target platform is explicit, and read from frozen evidence ------------


def test_the_target_platform_matches_the_frozen_scaffold() -> None:
    environment = json.loads(LOCK.read_text(encoding="utf-8"))["environment"]
    assert environment["device"] == TARGET_COMPUTE_DEVICE == "cpu"
    assert environment["gpu_model"] is None
    assert environment["cuda_version"] is None
    assert TARGET_ACCELERATOR == "none"
    assert "x86_64" in environment["platform"]
    assert TARGET_PLATFORM == "linux/amd64"


def test_the_approved_torch_build_cannot_use_an_accelerator() -> None:
    """`+cpu` is a CPU-only wheel. A GPU target would need a different build,
    which would change the approved dependency digest."""
    torch = [p for p in _packages() if p["name"].lower() == "torch"]
    assert torch and torch[0]["version"].endswith("+cpu")


@pytest.mark.parametrize(
    "os_name,arch", [("linux", "arm64"), ("windows", "amd64"), ("", "amd64")]
)
def test_another_platform_is_refused(os_name: str, arch: str) -> None:
    with pytest.raises(BuilderProtocolError):
        require_declared_platform(os_name=os_name, architecture=arch)


# -- base image authority ---------------------------------------------------


def _base_image(**overrides: object) -> BaseImageAuthority:
    base: dict[str, object] = {
        "descriptive_tag": "python:3.12.6-slim-bookworm",
        "digest_reference": "python@sha256:" + "c" * 64,
        "index_digest": "sha256:" + "a" * 64,
        "platform": "linux/amd64",
    }
    base.update(overrides)
    return BaseImageAuthority(**base)  # type: ignore[arg-type]


def test_a_digest_pinned_base_image_qualifies() -> None:
    assert require_base_image_authority(_base_image()).as_attestation()[
        "authority"
    ] == "digest_reference"


@pytest.mark.parametrize(
    "reference",
    ["python:3.12", "python:3.12.6", "ubuntu:latest", "python", "python@sha256:xx"],
)
def test_a_base_image_by_tag_is_refused(reference: str) -> None:
    with pytest.raises(BuilderProtocolError, match="addressed by digest"):
        require_base_image_authority(_base_image(digest_reference=reference))


def test_a_base_image_without_a_readable_tag_is_refused() -> None:
    """A digest alone is unreadable to the human who must review it."""
    with pytest.raises(BuilderProtocolError, match="no descriptive tag"):
        require_base_image_authority(_base_image(descriptive_tag=""))


# -- artifact identity versus location -------------------------------------


def test_identity_and_location_stay_separate() -> None:
    require_artifact_identity_separate_from_location(
        output_artifact_digest="sha256:" + "a" * 64,
        artifact_location="registry.invalid/cardiosentinel/j1-env",
    )


def test_a_digest_carrying_a_location_is_refused() -> None:
    """Two mirrors share one identity."""
    with pytest.raises(BuilderProtocolError, match="carries a location"):
        require_artifact_identity_separate_from_location(
            output_artifact_digest="registry.invalid/j1@sha256:" + "a" * 64,
            artifact_location="registry.invalid/j1",
        )


def test_an_artifact_nobody_can_fetch_is_refused() -> None:
    with pytest.raises(BuilderProtocolError, match="blank"):
        require_artifact_identity_separate_from_location(
            output_artifact_digest="sha256:" + "a" * 64, artifact_location="  "
        )


# -- dependency reconstruction, sections 13 and 17 -------------------------


def test_the_approved_set_splits_into_three_named_sources() -> None:
    grouped = derived_build_input(_packages())
    assert len(grouped[PYTORCH_CPU_INDEX]) == 2
    assert len(grouped[FIRST_PARTY_SOURCE]) == 1
    assert len(grouped[PYPI]) == APPROVED_PACKAGE_COUNT - 3


def test_the_derived_input_is_exactly_the_frozen_authority() -> None:
    packages = _packages()
    require_derived_input_matches_authority(derived_build_input(packages), packages)


def test_a_package_added_to_make_the_build_succeed_is_refused() -> None:
    packages = _packages()
    grouped = derived_build_input(packages)
    grouped[PYPI].append(("some-missing-wheel", "1.0.0"))
    with pytest.raises(BuilderProtocolError, match="added:"):
        require_derived_input_matches_authority(grouped, packages)


def test_a_package_dropped_to_make_the_build_succeed_is_refused() -> None:
    packages = _packages()
    grouped = derived_build_input(packages)
    grouped[PYPI].pop()
    with pytest.raises(BuilderProtocolError, match="dropped:"):
        require_derived_input_matches_authority(grouped, packages)


def test_the_derived_input_has_its_own_identity() -> None:
    packages = _packages()
    first = derived_input_digest(derived_build_input(packages))
    assert len(first) == 64
    assert first == derived_input_digest(derived_build_input(packages))


@pytest.mark.parametrize(
    "name,version,expected",
    [
        ("numpy", "2.3.2", PYPI),
        ("torch", "2.13.0+cpu", PYTORCH_CPU_INDEX),
        ("torchvision", "0.28.0+cpu", PYTORCH_CPU_INDEX),
        ("cardiosentinel", "0.1.0", FIRST_PARTY_SOURCE),
    ],
)
def test_each_package_is_routed_to_a_named_source(
    name: str, version: str, expected: str
) -> None:
    assert classify_dependency_source(name, version) == expected


def test_an_unrecognised_local_version_is_refused_rather_than_guessed() -> None:
    with pytest.raises(BuilderProtocolError, match="undetermined"):
        classify_dependency_source("mystery", "1.0.0+custom")


@pytest.mark.parametrize(
    "specifier", ["numpy>=1.26,<3", "numpy", "numpy~=2.3", "numpy>2"]
)
def test_mutable_dependency_resolution_is_refused(specifier: str) -> None:
    with pytest.raises(BuilderProtocolError, match="not an exact pin"):
        require_pinned_dependency_specifier(specifier)


def test_an_exact_pin_is_accepted() -> None:
    assert require_pinned_dependency_specifier("numpy==2.3.2")


def test_the_dependency_authority_is_imported_not_retyped() -> None:
    from cardiosentinel.journal_extension.j1 import builder_protocol

    assert builder_protocol.approved_dependency_digest() == APPROVED_DEPENDENCY_DIGEST
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    hex64 = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and len(node.value) == 64
        and all(c in "0123456789abcdef" for c in node.value)
    ]
    assert not hex64, f"a frozen digest is retyped in the module: {hex64}"


# -- build configuration digest covers every influencing input -------------


def _config() -> dict[str, str]:
    return {
        name: format(index, "064x")
        for index, name in enumerate(REQUIRED_BUILD_CONFIGURATION_INPUTS, start=1)
    }


def test_the_configuration_digest_covers_every_declared_input() -> None:
    assert len(build_configuration_digest(_config())) == 64


@pytest.mark.parametrize("omitted", REQUIRED_BUILD_CONFIGURATION_INPUTS)
def test_a_configuration_missing_an_influencing_input_is_refused(
    omitted: str,
) -> None:
    """A digest over the container file alone would call two builds identical."""
    config = _config()
    del config[omitted]
    with pytest.raises(BuilderProtocolError, match="every influencing input"):
        build_configuration_digest(config)


def test_a_configuration_input_must_be_identified_by_digest() -> None:
    config = _config()
    config["workflow"] = "the workflow file"
    with pytest.raises(BuilderProtocolError, match="full lowercase SHA-256"):
        build_configuration_digest(config)


def test_changing_any_input_changes_the_configuration_digest() -> None:
    baseline = build_configuration_digest(_config())
    for name in REQUIRED_BUILD_CONFIGURATION_INPUTS:
        altered = _config()
        altered[name] = "f" * 64
        assert build_configuration_digest(altered) != baseline


# -- two genuinely independent builds, section 18 --------------------------


def test_two_independent_builds_are_accepted() -> None:
    require_independent_builds(
        first_build_id="build-a",
        second_build_id="build-b",
        first_run_identity="run-1",
        second_run_identity="run-2",
        second_consumed_first_artifact=False,
    )


def test_one_build_recorded_twice_is_refused() -> None:
    with pytest.raises(BuilderProtocolError, match="one build recorded twice"):
        require_independent_builds(
            first_build_id="build-a",
            second_build_id="build-a",
            first_run_identity="run-1",
            second_run_identity="run-2",
            second_consumed_first_artifact=False,
        )


def test_two_builds_from_the_same_run_are_refused() -> None:
    """A shared cache can make two invocations agree without reproducibility."""
    with pytest.raises(BuilderProtocolError, match="same run identity"):
        require_independent_builds(
            first_build_id="build-a",
            second_build_id="build-b",
            first_run_identity="run-1",
            second_run_identity="run-1",
            second_consumed_first_artifact=False,
        )


def test_a_second_build_consuming_the_first_artifact_is_refused() -> None:
    """It would reproduce a copy rather than the build."""
    with pytest.raises(BuilderProtocolError, match="consumed the first"):
        require_independent_builds(
            first_build_id="build-a",
            second_build_id="build-b",
            first_run_identity="run-1",
            second_run_identity="run-2",
            second_consumed_first_artifact=True,
        )


# -- nothing here builds, promotes or authorizes ---------------------------


def test_the_module_neither_builds_nor_promotes_anything() -> None:
    """Structural, by AST over the module."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            assert name not in {
                "run",
                "check_call",
                "check_output",
                "Popen",
                "system",
                "EnvironmentAuthorityRecord",
                "verify_authority_record",
                "environment_sha256",
            }, f"the builder protocol calls {name!r} at line {node.lineno}"
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in {"subprocess", "os", "docker"}, (
                    f"the builder protocol imports {alias.name!r}"
                )


def test_the_controlled_build_workflow_is_present_and_inert() -> None:
    """This assertion replaced one that required the workflow to be *absent*.

    At #149 the protection was absence: a file under `.github/workflows/` is
    live on push, so shipping one would have been an uncontrolled build
    attempt. The workflow now exists, because a human authorization must be
    able to name an actual object, and the protection changed shape from
    absence to proven inertness -- which is stronger only if it is checked
    structurally. It is: `test_j1_controlled_build_workflow.py` parses the
    trigger set and the job dependency graph rather than grepping the file.

    What this test keeps is the narrow claim that belongs here: no *additional*
    workflow appeared, and the one that did is manual-only.
    """
    import yaml

    workflows = sorted((REPOSITORY_ROOT / ".github" / "workflows").glob("*.yml"))
    assert [p.name for p in workflows] == [
        "ci.yml",
        "j1-environment-artifact-build.yml",
    ]
    document = yaml.safe_load(
        (REPOSITORY_ROOT / ".github/workflows/j1-environment-artifact-build.yml")
        .read_text(encoding="utf-8")
    )
    # PyYAML parses a bare `on:` key as the boolean True.
    triggers = document["on"] if "on" in document else document[True]
    assert set(triggers) == {"workflow_dispatch"}
