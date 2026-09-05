"""The artifact-bound V2 dependency candidate, and the claims it may not make.

**No package is installed, no environment is mutated, no build runs, and no
authority is activated.** These tests read the committed candidate objects and
hold them to the boundary they declare.

The V1 audit could bind a name and a version. This candidate binds bytes: every
external member carries the SHA-256 of one artifact selected for the frozen
target, and the dependency closure was derived from the metadata inside those
artifacts rather than from whatever happens to be installed anywhere.

What it still cannot claim is that those bytes are the bytes V1 used. The
historical records carry name and version only, so no historical artifact
identity exists to compare against, and a candidate is not an authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
from packaging.markers import Marker
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.builder_authorization import (
    BUILDER_AUTHORIZATION_PATH,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
J1_DOCS = REPOSITORY_ROOT / "docs/journal-extension/j1"
CONTAINER_DIR = REPOSITORY_ROOT / "containers/j1-environment"

MANIFEST_PATH = J1_DOCS / "J1_V2_DEPENDENCY_ARTIFACT_MANIFEST_CANDIDATE_V1.json"
GRAPH_PATH = J1_DOCS / "J1_V2_ARTIFACT_DERIVED_DEPENDENCY_GRAPH_V1.json"
WHEELHOUSE_PATH = J1_DOCS / "J1_V2_CANDIDATE_WHEELHOUSE_MANIFEST_V1.json"
CANDIDATE_V2_PATH = J1_DOCS / "J1_V2_DEPENDENCY_AUTHORITY_CANDIDATE_V2.json"
CANDIDATE_V1_PATH = J1_DOCS / "J1_V2_DEPENDENCY_AUTHORITY_CANDIDATE_V1.json"
PACKET_PATH = J1_DOCS / "J1_V2_DEPENDENCY_AUTHORITY_DECISION_PACKET_V1.md"

REQUIREMENTS_PYPI = CONTAINER_DIR / "requirements.v2-candidate-pypi.txt"
REQUIREMENTS_PYTORCH = CONTAINER_DIR / "requirements.v2-candidate-pytorch.txt"

# The establishing locks as they appear in the tracked tree. The copies under
# cardiosentinel-runs/ are untracked, so a CI checkout only carries these.
ESTABLISHING_LOCK_BYTES = {
    "reproducibility/demo_bundle/runs/phase3b2-architecture-v1/"
    "B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json":
        "5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc",
    "reproducibility/demo_bundle/runs/phase4-p1-physiology-v1/"
    "P1B_phys_fusion_v1/EXPERIMENT_LOCK.json":
        "fdde6475a02e0249e0238b89168e6b043b3ade1ec2bfd75922628127fb27d2ca",
    "reproducibility/demo_bundle/runs/phase5-m1-dual-memory-v2/"
    "M1L_long_memory_v2/EXPERIMENT_LOCK.json":
        "6aa199ea5410dde860fd3fcce9ceef0194a364ed2ed5b01678e0648fea60a452",
}

HISTORICAL_DEPENDENCY_DIGEST = (
    "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a"
)

REQUIREMENT_LINE = re.compile(r"^(?P<name>[A-Za-z0-9._-]+)==(?P<version>[^\s\\]+) \\$")
HASH_LINE = re.compile(r"^    --hash=sha256:(?P<digest>[0-9a-f]{64})$")

TARGET_MARKER_ENVIRONMENT = {
    "python_version": "3.12",
    "python_full_version": "3.12.6",
    "implementation_name": "cpython",
    "implementation_version": "3.12.6",
    "platform_python_implementation": "CPython",
    "os_name": "posix",
    "sys_platform": "linux",
    "platform_system": "Linux",
    "platform_machine": "x86_64",
    "platform_release": "",
    "platform_version": "",
}


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


@pytest.fixture(scope="module")
def graph() -> dict:
    return json.loads(GRAPH_PATH.read_text())


@pytest.fixture(scope="module")
def candidate_v2() -> dict:
    return json.loads(CANDIDATE_V2_PATH.read_text())


def parse_requirements(path: Path) -> dict[str, tuple[str, str]]:
    """name -> (version, artifact sha256), refusing any line that is not both."""
    pins: dict[str, tuple[str, str]] = {}
    lines = [
        line
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert len(lines) % 2 == 0, (
        f"{path.name}: every pin must be followed by exactly one hash line"
    )
    for pin_line, hash_line in zip(lines[0::2], lines[1::2], strict=True):
        pin = REQUIREMENT_LINE.match(pin_line)
        digest = HASH_LINE.match(hash_line)
        assert pin is not None, (
            f"{path.name}: not an exact hash-bound pin: {pin_line!r}"
        )
        assert digest is not None, f"{path.name}: not a sha256 hash line: {hash_line!r}"
        pins[canonicalize_name(pin.group("name"))] = (
            pin.group("version"),
            digest.group("digest"),
        )
    return pins


# --------------------------------------------------------------- 1, 2, 10 ---
def test_every_external_member_has_exactly_one_authorized_artifact_sha256(
    manifest: dict,
) -> None:
    seen: dict[str, str] = {}
    for package in manifest["external_packages"]:
        name = package["normalized_name"]
        assert name not in seen, f"{name} appears twice in the manifest"
        digest = package["artifact_sha256"]
        assert re.fullmatch(r"[0-9a-f]{64}", digest), f"{name}: not a sha256"
        assert package["artifact_filename"].endswith(".whl")
        seen[name] = digest
    assert len(seen) == manifest["external_package_count"]


def test_no_external_member_carries_absent_byte_authority(manifest: dict) -> None:
    for package in manifest["external_packages"]:
        name = package["normalized_name"]
        assert package["wheel_or_sdist_byte_authority"] == "PRESENT", name
        assert package["artifact_size"] > 0
        assert package["metadata_sha256"]


def test_cardiosentinel_is_source_bound_and_carries_no_fabricated_wheel(
    manifest: dict,
) -> None:
    first_party = manifest["first_party_package"]
    assert first_party["source_kind"] == "FIRST_PARTY_CARDIOSENTINEL"
    assert first_party["wheel_or_sdist_byte_authority"] == "NOT_APPLICABLE_SOURCE_BOUND"
    assert "artifact_sha256" not in first_party
    # The builder's authorized source commit is not decided by this candidate.
    assert first_party["authorized_source_commit"] is None
    names = {package["normalized_name"] for package in manifest["external_packages"]}
    assert "cardiosentinel" not in names


# ------------------------------------------------------------------ 3, 4 ---
def test_no_unhashed_requirement_exists() -> None:
    for path in (REQUIREMENTS_PYPI, REQUIREMENTS_PYTORCH):
        pins = parse_requirements(path)
        assert pins, f"{path.name} is empty"
        for name, (version, digest) in pins.items():
            assert version and digest, name
            assert not any(c in version for c in "*<>~^"), f"{name}: not an exact pin"


def test_hash_requirements_reconcile_exactly_to_the_artifact_manifest(
    manifest: dict,
) -> None:
    pins = {
        **parse_requirements(REQUIREMENTS_PYPI),
        **parse_requirements(REQUIREMENTS_PYTORCH),
    }
    expected = {
        package["normalized_name"]: (package["version"], package["artifact_sha256"])
        for package in manifest["external_packages"]
    }
    assert pins == expected

    by_source = {
        "PYPI_INDEX": REQUIREMENTS_PYPI,
        "PYTORCH_CPU_INDEX": REQUIREMENTS_PYTORCH,
    }
    for source_class, path in by_source.items():
        in_file = set(parse_requirements(path))
        in_manifest = {
            package["normalized_name"]
            for package in manifest["external_packages"]
            if package["source_class"] == source_class
        }
        assert in_file == in_manifest, source_class


# ---------------------------------------------------------------- 5, 6, 7 ---
def test_the_artifact_derived_graph_reaches_closure(
    manifest: dict, graph: dict
) -> None:
    assert graph["closure_reached_fixed_point"] is True
    assert graph["node_count"] == manifest["external_package_count"]
    nodes = {package["normalized_name"] for package in manifest["external_packages"]}
    assert {edge["parent_distribution"] for edge in graph["edges"]} <= nodes
    for root in graph["roots"]:
        assert root in nodes


def test_every_active_dependency_edge_resolves_into_the_candidate(
    manifest: dict, graph: dict
) -> None:
    nodes = {package["normalized_name"] for package in manifest["external_packages"]}
    for edge in graph["edges"]:
        if not edge["active_on_target"]:
            assert edge["selected_version"] is None
            continue
        assert edge["selection_basis"] == (
            "HISTORICAL_VERSION_WITNESS_SATISFIES_BOUND_ARTIFACT_METADATA"
        )
        assert edge["required_distribution"] in nodes, edge["required_distribution"]
        assert edge["selected_version"]


def test_every_selected_version_satisfies_its_parent_specifier(
    manifest: dict, graph: dict
) -> None:
    versions = {
        package["normalized_name"]: package["version"]
        for package in manifest["external_packages"]
    }
    for edge in graph["edges"]:
        if not edge["active_on_target"]:
            continue
        specifier = edge["required_specifier"]
        selected = versions[edge["required_distribution"]]
        assert selected == edge["selected_version"]
        if specifier:
            assert SpecifierSet(specifier).contains(selected, prereleases=True), edge


def test_every_edge_carries_the_parent_artifact_and_metadata_binding(
    manifest: dict, graph: dict
) -> None:
    artifacts = {
        package["normalized_name"]: (
            package["artifact_sha256"],
            package["metadata_sha256"],
        )
        for package in manifest["external_packages"]
    }
    for edge in graph["edges"]:
        parent = edge["parent_distribution"]
        observed = (edge["parent_artifact_sha256"], edge["parent_metadata_sha256"])
        assert observed == artifacts[parent]


# --------------------------------------------------------------------- 8 ---
def test_markers_were_evaluated_for_cpython_312_linux_x86_64(graph: dict) -> None:
    assert graph["marker_environment"] == TARGET_MARKER_ENVIRONMENT

    evaluated = 0
    for edge in graph["edges"]:
        raw = edge["requires_dist_raw"]
        requirement = Requirement(raw)
        if requirement.marker is None:
            assert edge["marker_evaluation"] == "NO_MARKER"
            assert edge["active_on_target"] is True
            continue
        evaluated += 1
        extras = edge["activated_extras_on_parent"] or [""]
        expected = any(
            Marker(str(requirement.marker)).evaluate(
                {**TARGET_MARKER_ENVIRONMENT, "extra": extra}
            )
            for extra in [*extras, ""]
        )
        assert edge["active_on_target"] == expected, raw
    assert evaluated, "no marker was evaluated at all"


def test_no_extra_was_activated_without_an_edge_requiring_it(
    manifest: dict, graph: dict
) -> None:
    requested = {
        extra
        for edge in graph["edges"]
        if edge["active_on_target"]
        for extra in edge["requested_extras_on_child"]
    }
    for package in manifest["external_packages"]:
        for extra in package["activated_extras"]:
            assert extra in requested, (
                f"{package['normalized_name']}: extra {extra} activated with no edge"
            )


# --------------------------------------------------------------------- 9 ---
def test_the_seed_versus_artifact_delta_is_explicit(candidate_v2: dict) -> None:
    delta = candidate_v2["seed_vs_artifact_delta"]
    for key in (
        "seed_only_packages",
        "artifact_only_packages",
        "common_packages",
        "version_conflicts",
    ):
        assert key in delta

    seed = json.loads(CANDIDATE_V1_PATH.read_text())
    seed_external = {
        package["normalized_name"]
        for package in seed["candidate_packages"]
        if package["normalized_name"] != "cardiosentinel"
    }
    artifact = set(candidate_v2["artifact_derived_packages"]) - {"cardiosentinel"}
    assert delta["seed_only_packages"] == sorted(seed_external - artifact)
    assert delta["artifact_only_packages"] == sorted(artifact - seed_external)
    assert delta["common_packages"] == sorted(seed_external & artifact)

    # The count is a result, never a target.
    assert candidate_v2["seed_candidate_count"] == seed["candidate_package_count"]


# -------------------------------------------------------------------- 11 ---
def test_incident_management_is_not_declared_historically_invalid(
    candidate_v2: dict,
) -> None:
    disposition = candidate_v2["incident_management_disposition"]
    assert disposition["finding"] == "NOT_IN_ARTIFACT_DERIVED_J1_CLOSURE"
    assert disposition["in_artifact_derived_j1_closure"] is False
    assert disposition["prospective_disposition"] == (
        "EXCLUDE_FROM_V2_J1_SCIENTIFIC_RUNTIME_IF_HUMAN_AUTHORIZED"
    )

    # It is still one of the 335, and this candidate does not remove it from them.
    seed = json.loads(CANDIDATE_V1_PATH.read_text())
    assert candidate_v2["historical_package_count"] == 335
    assert seed["historical_package_count"] == 335

    # No selected artifact declares it.
    graph = json.loads(GRAPH_PATH.read_text())
    for edge in graph["edges"]:
        assert canonicalize_name(edge["required_distribution"]) != "incident-management"


def test_the_candidate_does_not_reach_for_the_stronger_claim(
    candidate_v2: dict,
) -> None:
    """Absence from a closure is not proof of global extraneousness.

    Checked by structure, not by substring. The fields whose job is to *state*
    the bound necessarily contain the phrases the finding may not make, so
    scanning the whole object for them fails on the sentence that forbids them.
    """
    disposition = candidate_v2["incident_management_disposition"]
    claim_bearing = {
        key: value
        for key, value in disposition.items()
        if key not in {"bound"}
    }
    blob = json.dumps(claim_bearing).lower()
    for forbidden in (
        "safe to remove",
        "globally extraneous",
        "proven contamination",
        "never existed",
        "cannot be obtained",
    ):
        assert forbidden not in blob, forbidden

    # The bound is present, and it is the field carrying those words.
    bound = disposition["bound"].lower()
    assert "not a finding that the package is globally extraneous" in bound
    assert "not proof of contamination" in bound


# -------------------------------------------------------------------- 12 ---
def test_the_historical_locks_remain_byte_unchanged() -> None:
    for relative, expected in ESTABLISHING_LOCK_BYTES.items():
        path = REPOSITORY_ROOT / relative
        assert path.is_file(), relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative
        lock = json.loads(path.read_text())
        dependencies = lock["environment"]["dependencies"]
        assert dependencies["installed_package_count"] == 335
        assert dependencies["installed_packages_sha256"] == HISTORICAL_DEPENDENCY_DIGEST


def test_the_candidate_does_not_supersede_the_historical_snapshot(
    candidate_v2: dict,
) -> None:
    assert candidate_v2["historical_snapshot_digest"] == HISTORICAL_DEPENDENCY_DIGEST
    assert "HISTORICAL_SNAPSHOT_AUTHORITY" in candidate_v2["historical_snapshot_role"]
    outside = candidate_v2["historical_packages_outside_v2_runtime_count"]
    assert outside == 335 - candidate_v2["artifact_derived_package_count"]
    assert outside == 287


# ---------------------------------------------------------------- 13, 14 ---
def test_the_candidate_remains_candidate_only_and_not_authorized(
    manifest: dict, graph: dict, candidate_v2: dict
) -> None:
    wheelhouse = json.loads(WHEELHOUSE_PATH.read_text())
    for document in (manifest, graph, candidate_v2, wheelhouse):
        assert document["status"] == "CANDIDATE_ONLY"
        assert document["authorization_status"] == "NOT_AUTHORIZED"


def test_the_candidate_digest_is_never_named_an_approved_digest(
    candidate_v2: dict,
) -> None:
    assert "candidate_v2_dependency_authority_digest" in candidate_v2
    for forbidden in ("approved_dependency_digest", "active_dependency_digest"):
        assert forbidden not in candidate_v2


def test_the_decision_packet_refuses_to_authorize() -> None:
    text = PACKET_PATH.read_text()
    assert "THIS DOCUMENT DOES NOT AUTHORIZE THE DEPENDENCY AUTHORITY." in text


def test_the_candidate_digest_recomputes_from_the_object() -> None:
    document = json.loads(CANDIDATE_V2_PATH.read_text())
    recorded = document.pop("candidate_v2_dependency_authority_digest")
    payload = json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    assert hashlib.sha256(payload.encode()).hexdigest() == recorded


# ------------------------------------------------------------ 15, 16, 17 ---
def test_no_builder_authorization_004_exists() -> None:
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    for path in J1_DOCS.rglob("*"):
        assert "AUTH-004" not in path.name
        assert "AUTH_004" not in path.name


def test_no_environment_authority_record_exists() -> None:
    for path in J1_DOCS.rglob("*"):
        assert "ENVIRONMENT_AUTHORITY_RECORD" not in path.name.upper()


def test_the_candidate_records_zero_scientific_attempts(candidate_v2: dict) -> None:
    state = candidate_v2["governance_state_at_completion"]
    assert state["active_builder_authorization"] == "ABSENT"
    assert state["authorization_004"] == "ABSENT"
    assert state["environment_authority_record"] == "ABSENT"
    assert state["j1_scientific_authorization"] == "ABSENT"
    assert state["j1_attempt_budget"] == "NOT_ESTABLISHED"
    assert state["j1_scientific_attempts_used"] == 0
    assert state["scientific_data_accessed"] is False
    assert state["controlled_build_run_count"] == 3


# ------------------------------------------------------- readiness state ---
def test_the_readiness_state_follows_from_the_criteria(candidate_v2: dict) -> None:
    criteria = candidate_v2["readiness_criteria"]
    blocked = not all(criteria.values())
    assert blocked, "criteria all pass but the object was written as blocked"
    expected_state = "V2_DEPENDENCY_AUTHORITY_CANDIDATE_BLOCKED"
    assert candidate_v2["readiness_state"] == expected_state
    assert candidate_v2["blockers"], "a blocked candidate must enumerate its blockers"
    for blocker in candidate_v2["blockers"]:
        for field in ("id", "kind", "observed", "bound", "owner"):
            assert blocker.get(field), blocker.get("id")


def test_the_blockers_are_bounded_to_what_was_observed(candidate_v2: dict) -> None:
    """Each blocker says where it was seen, and does not generalise past it."""
    for blocker in candidate_v2["blockers"]:
        assert "clean-room" in blocker["bound"] or "container image" in blocker["bound"]
    limitations = " ".join(candidate_v2["limitations"]).lower()
    disclosed = "does not establish that these are the bytes historically used in v1"
    assert disclosed in limitations


def test_the_install_replay_is_not_called_bit_reproducibility(
    candidate_v2: dict,
) -> None:
    replay = candidate_v2["dependency_install_replay"]
    assert replay["classification"] == "DEPENDENCY_INSTALL_REPLAY"
    assert "BIT_REPRODUCIBLE_ENVIRONMENT" in replay["not_claimed"]
    status = candidate_v2["artifact_byte_authority_status"]
    assert status == "PRESENT_FOR_ALL_EXTERNAL_MEMBERS"
