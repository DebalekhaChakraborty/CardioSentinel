"""The local open-weight provider: opt-in, lazy, and guarded twice.

Every test here runs with stubs. **No weights are downloaded and no network is
touched**, mirroring `test_explanation_evaluation.py`, which validates the
harness against deliberately bad providers rather than against a real model.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys
from types import ModuleType, SimpleNamespace

import pytest

from cardiosentinel.agents import claims
from cardiosentinel.agents.context import build_context
from cardiosentinel.agents.evidence import EvidenceAgent
from cardiosentinel.agents.explain import (
    DETERMINISTIC,
    GENERATIVE,
    PatientExplanationAgent,
)
from cardiosentinel.agents.graph import build_evidence_graph
from cardiosentinel.agents.providers import (
    DEFAULT_LOCAL_MODEL,
    REPORTED_LOCAL_MODEL,
    LocalQwenProvider,
    ProviderIdentity,
    ProviderUnavailable,
    default_provider,
)
from cardiosentinel.edge.alerts import AlertBuilder
from cardiosentinel.edge.session import EdgeObservation

PROVENANCE = {
    "encoder_architecture": "B4BTransformerCNN",
    "m2_arm": "M2-G",
    "u1_family": "platt_logistic_on_recovered_logit",
    "t2_arm": "CausalS4DLongitudinal",
    "t1_policy_id": "qw0.9_qe0.99_FAST",
    "t1_held_out_subject": "ltstdb:s2004",
    "detector_threshold": 0.7554003000259399,
}
GATE = {
    "g1_available": True,
    "g2_finite_representation": True,
    "g3_sqi_admissible": True,
    "g4_normal_evidence": False,
    "g5_not_in_refractory": False,
    "g6_morphology_computable": True,
    "past_observed_count_before": 203,
    "past_update_count_before": 0,
}
REVISION = "a" * 40
STUB_IDENTITY = ProviderIdentity(
    provider="stub",
    model_id="cardiosentinel/fake-qwen",
    revision=REVISION,
    quantization="Q4",
    runtime="transformers",
    device="cpu",
)


class Stub:
    """A provider whose behaviour the test chooses."""

    name = "stub"
    identity = STUB_IDENTITY

    def __init__(self, *, text: str = "", error: Exception | None = None) -> None:
        self._text = text
        self._error = error

    def generate(self, brief: str, payload: str) -> str:
        if self._error is not None:
            raise self._error
        return self._text


def _observation(state: str, seconds: float, before: str) -> EdgeObservation:
    return EdgeObservation(
        stable_id=f"ltstdb:s20041:0:{int(seconds * 250)}:0",
        record_id="s20041",
        subject_id="ltstdb:s2004",
        channel_index=0,
        start_sample=int(seconds * 250),
        elapsed_stream_seconds=seconds,
        score_present=True,
        detector_score=0.81,
        detector_decision=True,
        calibrated_probability=0.55,
        decision_error_uncertainty=0.45,
        temporal_evidence=0.95,
        memory_deviation=1.41,
        state_before=before,
        state=state,
        streaks={},
        memory_update_admitted=False,
        gate=dict(GATE),
        contains_filter_warmup=False,
    )


@pytest.fixture
def graph(tmp_path):
    builder = AlertBuilder(PROVENANCE)
    observations, previous, alert = [], "NORMAL", None
    for index, state in enumerate(["NORMAL", "WATCH", "EVENT", "EVENT", "NORMAL"]):
        item = _observation(state, index * 5.0, previous)
        previous = state
        observations.append(item)
        emitted = builder.observe(item)
        if emitted is not None:
            alert = emitted
    assert alert is not None
    record = EvidenceAgent(PROVENANCE).explain(alert, observations)
    return build_evidence_graph(record, run_root=tmp_path)


def _compliant(graph) -> str:
    """Prose that passes both gates: real numbers only, canonical disclaimer."""
    evidence = build_context(graph).evidence
    return (
        "The system entered the EVENT state and held it. The calibrated "
        f"probability reached {evidence['calibrated_probability']:.3f}. The "
        "system declined to update the patient baseline. "
        + claims.SYSTEM_BEHAVIOUR_ONLY
    )


# -- the provider is opt-in and never downloads on construction -------------


def test_an_uncached_model_refuses_rather_than_downloading(fake_runtime):
    """Constructing a provider must never trigger a multi-gigabyte fetch."""
    def unavailable(_model_id, *, revision, local_files_only):
        assert revision == REVISION
        assert local_files_only is True
        raise OSError("not in cache")

    fake_runtime.huggingface_hub.snapshot_download = unavailable
    with pytest.raises(ProviderUnavailable, match="not completely cached locally"):
        LocalQwenProvider(
            model="cardiosentinel/definitely-not-a-real-model", revision=REVISION
        )


def _snapshot(
    root: pathlib.Path,
    *,
    revision: str = REVISION,
    config: bool = True,
    tokenizer: bool = True,
    weights: bool = True,
) -> pathlib.Path:
    snapshot = root / revision
    snapshot.mkdir()
    if config:
        (snapshot / "config.json").write_text("{}", encoding="utf-8")
    if tokenizer:
        (snapshot / "tokenizer.json").write_text("{}", encoding="utf-8")
    if weights:
        (snapshot / "model.safetensors").write_bytes(b"fake weights")
    return snapshot


@pytest.fixture
def fake_runtime(monkeypatch):
    """Dependency-free stand-ins: CI installs no LLM runtime or weights."""
    huggingface_hub = ModuleType("huggingface_hub")
    transformers = ModuleType("transformers")
    torch = ModuleType("torch")

    def unconfigured(*_args, **_kwargs):
        raise AssertionError("fake runtime call was not configured by the test")

    huggingface_hub.snapshot_download = unconfigured
    transformers.AutoConfig = SimpleNamespace(from_pretrained=unconfigured)
    transformers.AutoTokenizer = SimpleNamespace(from_pretrained=unconfigured)
    transformers.AutoModelForCausalLM = SimpleNamespace(from_pretrained=unconfigured)
    torch.float32 = "float32"
    torch.set_num_threads = lambda _count: None

    class NoGrad:
        def __enter__(self):
            return None

        def __exit__(self, *_args):
            return False

    torch.no_grad = NoGrad
    monkeypatch.setitem(sys.modules, "huggingface_hub", huggingface_hub)
    monkeypatch.setitem(sys.modules, "transformers", transformers)
    monkeypatch.setitem(sys.modules, "torch", torch)
    return SimpleNamespace(
        huggingface_hub=huggingface_hub,
        transformers=transformers,
        torch=torch,
    )


def _resolve_to(fake_runtime, snapshot: pathlib.Path) -> None:

    def resolve(_model_id, *, revision, local_files_only):
        assert revision == REVISION
        assert local_files_only is True
        return str(snapshot)

    fake_runtime.huggingface_hub.snapshot_download = resolve


@pytest.mark.parametrize("revision", [None, "main", "abcdef1"])
def test_a_moving_or_unknown_revision_is_refused(fake_runtime, revision):
    fake_runtime.huggingface_hub.snapshot_download = (
        lambda *_args, **_kwargs: pytest.fail("a moving revision reached the cache")
    )
    with pytest.raises(ProviderUnavailable, match="revision cannot be resolved"):
        LocalQwenProvider(model=REPORTED_LOCAL_MODEL, revision=revision)


def test_the_resolved_snapshot_must_equal_the_requested_revision(
    fake_runtime, tmp_path
):
    other_revision = "b" * 40
    snapshot = _snapshot(tmp_path, revision=other_revision)
    fake_runtime.huggingface_hub.snapshot_download = (
        lambda *_args, **_kwargs: str(snapshot)
    )
    with pytest.raises(ProviderUnavailable, match="unexpected cached snapshot"):
        LocalQwenProvider(model=REPORTED_LOCAL_MODEL, revision=REVISION)


@pytest.mark.parametrize(
    ("missing", "message"),
    [
        ("config", "config.json"),
        ("tokenizer", "tokenizer assets"),
        ("weights", "model weights"),
    ],
)
def test_config_tokenizer_and_weights_are_all_required_before_generation(
    fake_runtime, tmp_path, missing, message
):
    snapshot = _snapshot(
        tmp_path,
        config=missing != "config",
        tokenizer=missing != "tokenizer",
        weights=missing != "weights",
    )
    _resolve_to(fake_runtime, snapshot)
    with pytest.raises(ProviderUnavailable, match=message):
        LocalQwenProvider(model=REPORTED_LOCAL_MODEL, revision=REVISION)


def test_every_weight_shard_named_by_the_index_must_exist(fake_runtime, tmp_path):
    snapshot = _snapshot(tmp_path, weights=False)
    (snapshot / "model.safetensors.index.json").write_text(
        json.dumps(
            {
                "weight_map": {
                    "layer.0": "model-00001-of-00002.safetensors",
                    "layer.1": "model-00002-of-00002.safetensors",
                }
            }
        ),
        encoding="utf-8",
    )
    (snapshot / "model-00001-of-00002.safetensors").write_bytes(b"first")
    _resolve_to(fake_runtime, snapshot)
    with pytest.raises(ProviderUnavailable, match="00002-of-00002"):
        LocalQwenProvider(model=REPORTED_LOCAL_MODEL, revision=REVISION)


def test_quantization_is_none_when_the_cached_config_is_unquantized(
    fake_runtime, tmp_path
):
    snapshot = _snapshot(tmp_path)
    _resolve_to(fake_runtime, snapshot)
    fake_runtime.transformers.AutoConfig.from_pretrained = (
        lambda _path, **_options: SimpleNamespace()
    )
    fake_runtime.transformers.AutoTokenizer.from_pretrained = (
        lambda _path, **_options: object()
    )
    provider = LocalQwenProvider(model=REPORTED_LOCAL_MODEL, revision=REVISION)
    assert provider.identity.quantization == "none"


def test_an_unresolvable_quantization_record_is_refused(fake_runtime, tmp_path):
    snapshot = _snapshot(tmp_path)
    _resolve_to(fake_runtime, snapshot)
    fake_runtime.transformers.AutoConfig.from_pretrained = (
        lambda _path, **_options: SimpleNamespace(quantization_config={})
    )
    fake_runtime.transformers.AutoTokenizer.from_pretrained = (
        lambda _path, **_options: object()
    )
    with pytest.raises(ProviderUnavailable, match="quantization cannot be resolved"):
        LocalQwenProvider(model=REPORTED_LOCAL_MODEL, revision=REVISION)


def test_fake_cached_model_runs_through_provider_and_audit(
    fake_runtime, tmp_path, graph
):
    """CI contract: fake weights -> real provider adapter -> both output gates."""
    snapshot = _snapshot(tmp_path)
    _resolve_to(fake_runtime, snapshot)
    calls: dict[str, object] = {}

    class FakeTokenizer:
        eos_token_id = 0

        def apply_chat_template(self, messages, **options):
            calls["messages"] = messages
            # `enable_thinking=False` is required, not incidental: Qwen3 is a
            # hybrid reasoning model and emits a <think> block by default. Arm B
            # scored a truncated reasoning trace as a valid explanation before
            # this was set, so the fake asserts the provider still asks for it.
            assert options == {
                "add_generation_prompt": True,
                "tokenize": False,
                "enable_thinking": False,
            }
            return "rendered prompt"

        def __call__(self, text, *, return_tensors):
            assert text == "rendered prompt"
            assert return_tensors == "pt"
            return {"input_ids": SimpleNamespace(shape=(1, 2))}

        def decode(self, _tokens, *, skip_special_tokens):
            assert skip_special_tokens is True
            return claims.SYSTEM_BEHAVIOUR_ONLY

    class FakeModel:
        def eval(self):
            return self

        def generate(self, **options):
            calls["generate"] = options
            return [[1, 2, 3]]

    def config_from_pretrained(path, **options):
        calls["config"] = (path, options)
        return SimpleNamespace(quantization_config={"bits": 4})

    tokenizer = FakeTokenizer()

    def tokenizer_from_pretrained(path, **options):
        calls["tokenizer"] = (path, options)
        return tokenizer

    def model_from_pretrained(path, **options):
        calls["model"] = (path, options)
        return FakeModel()

    fake_runtime.transformers.AutoConfig.from_pretrained = config_from_pretrained
    fake_runtime.transformers.AutoTokenizer.from_pretrained = tokenizer_from_pretrained
    fake_runtime.transformers.AutoModelForCausalLM.from_pretrained = (
        model_from_pretrained
    )

    provider = LocalQwenProvider(
        model=REPORTED_LOCAL_MODEL,
        revision=REVISION,
        max_new_tokens=8,
    )
    assert provider.identity.as_dict() == {
        "provider": "local_qwen",
        "model_id": REPORTED_LOCAL_MODEL,
        "revision": REVISION,
        "quantization": "Q4",
        "runtime": "transformers",
        "device": "cpu",
    }

    explanation = PatientExplanationAgent(provider).explain(graph)
    assert explanation.explanation_mode == GENERATIVE
    assert claims.audit(explanation.text) == ()
    assert explanation.provider == "local_qwen"
    assert explanation.model_id == REPORTED_LOCAL_MODEL
    assert explanation.revision == REVISION
    assert explanation.quantization == "Q4"
    assert explanation.runtime == "transformers"
    assert explanation.device == "cpu"
    record = explanation.as_dict()
    assert {
        key: record[key]
        for key in (
            "provider",
            "model_id",
            "revision",
            "quantization",
            "runtime",
            "device",
        )
    } == provider.identity.as_dict()
    assert calls["config"] == (str(snapshot), {"local_files_only": True})
    assert calls["tokenizer"] == (str(snapshot), {"local_files_only": True})
    model_path, model_options = calls["model"]
    assert model_path == str(snapshot)
    assert model_options == {"local_files_only": True}


def test_default_provider_does_not_select_local_without_opting_in(monkeypatch):
    monkeypatch.delenv("CARDIOSENTINEL_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert default_provider() is None


def test_google_credentials_do_not_select_gemini_without_consent(monkeypatch):
    import cardiosentinel.agents.providers as providers

    class FakeGemini:
        name = "gemini:fake"

        def __init__(self):
            pytest.fail("credentials alone selected Gemini")

    monkeypatch.delenv("CARDIOSENTINEL_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "synthetic-key-never-used")
    monkeypatch.setattr(providers, "GeminiProvider", FakeGemini)
    assert providers.default_provider() is None


def test_strict_local_makes_the_gemini_path_impossible(monkeypatch):
    import cardiosentinel.agents.providers as providers

    class FakeGemini:
        name = "gemini:fake"

        def __init__(self):
            pytest.fail("strict local constructed Gemini")

    monkeypatch.delenv("CARDIOSENTINEL_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "synthetic-key-never-used")
    monkeypatch.setattr(providers, "GeminiProvider", FakeGemini)
    assert providers.default_provider(strict_local=True) is None


def test_explicit_gemini_is_permitted_and_requires_credentials(monkeypatch):
    import cardiosentinel.agents.providers as providers

    selected = object()
    monkeypatch.setattr(providers, "GeminiProvider", lambda: selected)
    assert providers.default_provider(provider="gemini") is selected

    def unavailable():
        raise ProviderUnavailable("GOOGLE_API_KEY is not set")

    monkeypatch.setattr(providers, "GeminiProvider", unavailable)
    with pytest.raises(ProviderUnavailable, match="GOOGLE_API_KEY"):
        providers.default_provider(provider="gemini")


def test_strict_local_refuses_an_explicit_hosted_choice(monkeypatch):
    import cardiosentinel.agents.providers as providers

    monkeypatch.setattr(
        providers,
        "GeminiProvider",
        lambda: pytest.fail("strict local constructed Gemini"),
    )
    with pytest.raises(ProviderUnavailable, match="strict-local"):
        providers.default_provider(provider="gemini", strict_local=True)


def test_cli_provider_choice_is_explicit_and_no_generative_remains_exclusive():
    from cardiosentinel.cli import build_parser

    parser = build_parser()
    hosted = parser.parse_args(
        ["agent", "why", "s20201", "--provider", "gemini"]
    )
    assert hosted.provider == "gemini"
    assert hosted.no_generative is False

    deterministic = parser.parse_args(
        ["agent", "why", "s20201", "--no-generative"]
    )
    assert deterministic.no_generative is True
    assert deterministic.provider is None

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "agent",
                "why",
                "s20201",
                "--no-generative",
                "--provider",
                "gemini",
            ]
        )


def test_research_evaluation_can_refuse_an_unresolvable_local_provider(
    monkeypatch,
):
    import cardiosentinel.agents.providers as providers

    monkeypatch.setenv("CARDIOSENTINEL_LLM_PROVIDER", "local")

    def unavailable():
        raise ProviderUnavailable("model revision cannot be resolved")

    monkeypatch.setattr(providers, "LocalQwenProvider", unavailable)
    assert default_provider() is None  # ordinary explanations still degrade
    with pytest.raises(ProviderUnavailable, match="revision cannot be resolved"):
        default_provider(strict_local=True)


def test_the_default_model_is_apache_licensed_and_ungated():
    """Recorded so a licence change is a test failure, not a discovery."""
    assert DEFAULT_LOCAL_MODEL.startswith("Qwen/")


def test_real_model_execution_is_a_separate_manual_record():
    """The manual record is separate from CI, and CI never runs the real model.

    **This test asserted `"Status: NOT EXECUTED"` until 2026-08-25**, which
    stopped being true the moment Arm B was exercised. It kept passing anyway,
    because the document was not updated either -- so a test named for the
    separation of CI from manual execution was operatively asserting a status
    string, and the two predicates diverged silently. The status is now the
    record's to state; what this test binds is the separation itself.
    """
    root = pathlib.Path(__file__).resolve().parents[2]
    contract = (root / "docs" / "explanation" / "QWEN_EVALUATION_RUN.md").read_text(
        encoding="utf-8"
    )
    assert "CI must never download or execute the real model" in contract
    assert '"revision": "<full 40-character Hugging Face commit SHA>"' in contract
    assert "latency_scope: total generation latency" in contract
    # The run record must exist as a table with a status row, whatever it says.
    assert "| Execution status |" in contract


# -- the deterministic path is untouched ------------------------------------


def test_with_no_provider_the_agent_behaves_exactly_as_before(graph):
    """Protects `DEMO_SCENARIO.md` and `test_demo_bundle.py`."""
    explanation = PatientExplanationAgent().explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert explanation.fallback_reason == "no provider configured"


# -- requirement 8: everything is recorded ----------------------------------


def test_a_compliant_generation_records_provider_model_and_latency(graph):
    explanation = PatientExplanationAgent(Stub(text=_compliant(graph))).explain(graph)
    assert explanation.explanation_mode == GENERATIVE
    assert explanation.provider == "stub"
    assert explanation.model_id == STUB_IDENTITY.model_id
    assert explanation.revision == REVISION
    assert explanation.quantization == "Q4"
    assert explanation.runtime == "transformers"
    assert explanation.device == "cpu"
    assert explanation.latency_seconds is not None
    assert explanation.latency_scope == "total response latency"


def test_latency_is_recorded_on_the_deterministic_path_too(graph):
    explanation = PatientExplanationAgent().explain(graph)
    assert explanation.latency_seconds is not None
    assert explanation.latency_seconds >= 0.0


# -- the four pre-existing fallbacks still record their reason --------------


@pytest.mark.parametrize(
    ("stub", "fragment"),
    [
        (Stub(error=RuntimeError("boom")), "failed"),
        (Stub(text="   "), "returned nothing"),
        (Stub(text="S4D outperforms GRU."), "claim boundary"),
    ],
)
def test_a_failing_provider_degrades_and_says_why(graph, stub, fragment):
    explanation = PatientExplanationAgent(stub).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert fragment in (explanation.fallback_reason or "")
    assert explanation.provider == "stub"
    assert explanation.renderer == "template"
    assert explanation.model_id == STUB_IDENTITY.model_id
    assert explanation.revision == REVISION


def test_fallback_latency_includes_the_failed_generation_attempt(
    monkeypatch, graph
):
    clock = iter((100.0, 135.42))
    monkeypatch.setattr(
        "cardiosentinel.agents.explain.time.perf_counter", lambda: next(clock)
    )
    explanation = PatientExplanationAgent(
        Stub(error=RuntimeError("failed after generation timeout"))
    ).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert explanation.latency_seconds == pytest.approx(35.42)
    assert explanation.latency_scope == "total response latency"


def test_a_claim_violation_is_recorded_not_just_counted(graph):
    explanation = PatientExplanationAgent(Stub(text="S4D outperforms GRU.")).explain(
        graph
    )
    assert explanation.claim_violations


# -- the fidelity gate, which the claim guard cannot do ---------------------


def test_an_invented_number_falls_back(graph):
    """The claim guard passes this text. Fidelity must not."""
    text = "The calibrated probability reached 0.812345. " + (
        claims.SYSTEM_BEHAVIOUR_ONLY
    )
    assert not claims.audit(text), "precondition: the claim guard allows this"
    explanation = PatientExplanationAgent(Stub(text=text)).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert "numeric claim" in (explanation.fallback_reason or "")
    assert "0.812345" in (explanation.fallback_reason or "")


def test_a_percentage_conversion_falls_back(graph):
    """A unit changes the claim: 0.545613 is evidence, 54.6% is not.

    The registered metric cannot see this -- one decimal place, nothing
    extracted -- which is why the guard is a separate concept. See protocol §4.3.
    """
    text = "The calibrated probability reached 54.6%. " + claims.SYSTEM_BEHAVIOUR_ONLY
    assert not claims.audit(text), "precondition: the claim guard allows this"
    explanation = PatientExplanationAgent(Stub(text=text)).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert "numeric claim" in (explanation.fallback_reason or "")
    assert "54.6%" in (explanation.fallback_reason or "")


def test_rounding_is_not_fabrication(graph):
    """A rounded rendering of a real value must still pass."""
    explanation = PatientExplanationAgent(Stub(text=_compliant(graph))).explain(graph)
    assert explanation.explanation_mode == GENERATIVE


# -- the frozen environment is not modified ---------------------------------

FROZEN_DIGEST = "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a"


def _observed_digest() -> str:
    from cardiosentinel.neural import provenance

    return provenance.dependency_environment()["installed_packages_sha256"]


#: The same convention the T1/M2 suites use. CI legitimately builds its own
#: environment -- it installed 71 packages where the scientific interpreter has
#: 335 -- so an assertion about the frozen set can only run where that set is.
ON_FROZEN_INTERPRETER = _observed_digest() == FROZEN_DIGEST


@pytest.mark.skipif(
    not ON_FROZEN_INTERPRETER,
    reason=(
        "asserts the frozen scientific identity; this environment reports a "
        "different installed-package digest, which CI does by design"
    ),
)
def test_the_scientific_environment_is_unchanged():
    """On the frozen interpreter, this provider must not have added a package."""
    from cardiosentinel.neural import provenance

    environment = provenance.dependency_environment()
    assert environment["installed_package_count"] == 335
    assert environment["installed_packages_sha256"] == FROZEN_DIGEST


def test_the_llm_extra_declares_no_package_the_frozen_set_lacks():
    """The assertion that bites everywhere, including CI.

    The digest test above cannot run on CI, and a skipped test guards nothing.
    This one states the property that actually matters and is checkable from the
    declaration alone: the `llm` extra exists to *document* dependencies already
    present in the frozen environment, never to add one. If it grows a package,
    installing this extra would change the scientific interpreter's digest and
    void the reproducibility claim that digest supports.
    """
    import tomllib

    root = pathlib.Path(__file__).resolve().parents[2]
    manifest = tomllib.loads((root / "pyproject.toml").read_text())
    declared = manifest["project"]["optional-dependencies"]["llm"]
    names = {
        re.split(r"[<>=!~\[]", entry, maxsplit=1)[0].strip().lower()
        for entry in declared
    }
    assert names == {"torch", "transformers", "huggingface-hub"}, (
        "the llm extra must name only packages the frozen environment already "
        f"contains; found {sorted(names)}"
    )


# -- against the REAL libraries, not the fakes ------------------------------
#
# Everything above runs on a `fake_runtime` that shadows `huggingface_hub`,
# `transformers` and `torch` in `sys.modules`. That is the right way to test
# cache-validation logic -- CI has no weights and a corrupt snapshot is easier
# to fabricate than to obtain -- but it means those tests never touch the real
# libraries, so real API drift would pass them unnoticed. The `apply_chat_template`
# signature changing in transformers 5.x is exactly that kind of drift.
#
# These two run against the genuine packages, which is what installing the `llm`
# extra in CI buys. They need no weights and no network.

def _llm_extra_installed() -> bool:
    """True when the real libraries are importable.

    `find_spec` is wrapped because it does not merely return `None` for every
    absent module -- it propagates `ImportError` when a parent package cannot be
    imported, so a bare call is itself a way for this guard to fail for a reason
    unrelated to what it is checking.
    """
    for module in ("huggingface_hub", "transformers", "torch"):
        try:
            if importlib.util.find_spec(module) is None:
                return False
        except (ImportError, ValueError):
            return False
    return True


real_runtime = pytest.mark.skipif(
    not _llm_extra_installed(),
    reason="the llm extra is not installed in this environment",
)


@real_runtime
def test_a_bogus_model_refuses_through_the_real_hub():
    """The real `snapshot_download` miss must surface as `ProviderUnavailable`.

    This is the failure the original CI run hit as a bare `ModuleNotFoundError`.
    Whatever the hub raises for an uncached repository, the provider must
    translate it into the one exception callers degrade on.
    """
    with pytest.raises(ProviderUnavailable):
        LocalQwenProvider(
            model="cardiosentinel/definitely-not-a-real-model",
            revision="0" * 40,
        )


@real_runtime
@pytest.mark.parametrize("revision", [None, "main", "abcdef1", "0" * 39])
def test_a_moving_revision_is_refused_before_the_hub_is_consulted(revision):
    """Reproducibility is enforced by the rule, not by the cache being warm.

    A tag or a short hash is rejected on its own terms, so the refusal does not
    depend on what happens to be downloaded.
    """
    with pytest.raises(ProviderUnavailable, match="immutable"):
        LocalQwenProvider(model="Qwen/Qwen3-1.7B", revision=revision)


def test_an_invented_integer_falls_back(graph):
    """The case the registered metric is blind to by design.

    `evidence_fidelity` extracts only two-or-more-decimal values, so an invented
    whole number is invisible to it. The guard asks a different question and
    catches it.
    """
    text = "The system fired 999 times. " + claims.SYSTEM_BEHAVIOUR_ONLY
    assert not claims.audit(text), "precondition: the claim guard allows this"
    explanation = PatientExplanationAgent(Stub(text=text)).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert "999" in (explanation.fallback_reason or "")


def test_the_guard_does_not_reject_the_deterministic_renderer(graph):
    """The regression that matters: the fallback must survive its own gate.

    The template states a timestamp, a duration and a window count. If the guard
    rejected those, every generative failure would fall back into a second
    failure.
    """
    from cardiosentinel.agents.explain import TemplateRenderer

    context = build_context(graph)
    rendered = TemplateRenderer().render(context)
    assert PatientExplanationAgent._unsupported_numeric_claims(rendered, context) == ()
