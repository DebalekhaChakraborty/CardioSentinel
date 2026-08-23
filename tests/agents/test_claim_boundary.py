"""The claim boundary guard, including the limitation it cannot fix."""

from __future__ import annotations

import pytest

from cardiosentinel.agents import claims


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("The model outperforms the GRU baseline on validation.", {6, 22}),
        ("CardioSentinel is deployment-ready for clinical use.", {2}),
        ("This provides early detection with useful warning time.", {17}),
        ("Results generalize to other hospitals.", {3}),
        ("The difference is statistically significant (p < 0.05).", {13}),
        ("Selective routing is implemented and active.", {14}),
        ("The temporal calibrated probability was 0.82.", {9}),
        ("Externally validated on a second cohort.", {24}),
        ("We report false alarms per hour for T1.", {21}),
        ("Conformal prediction provides the intervals.", {16}),
    ],
)
def test_realistic_overclaims_are_caught(text, expected):
    found = {v.claim_number for v in claims.find_violations(text)}
    assert expected <= found, f"missed {expected - found} in {text!r}"


@pytest.mark.parametrize(
    "text",
    [
        "The predefined selection rule selected S4D based on the observed "
        "validation contrast.",
        "Episode reasoning improves episode-level agreement relative to a "
        "memoryless window rule, on identical rows, at the promoted operating "
        "point.",
        "The window entered EVENT after two consecutive confirming windows.",
        "Provenance digests are recorded for every artifact read.",
        "Improved ECE alone is not a success criterion.",
    ],
)
def test_legitimate_phrasings_are_not_flagged(text):
    """Including the one permitted improvement sentence, which is the subtle case."""
    assert claims.find_violations(text) == ()


def test_enforce_raises_and_names_the_claim():
    with pytest.raises(claims.ClaimBoundaryError) as caught:
        claims.enforce("The system is deployment-ready.")
    assert "claim 2" in str(caught.value)
    assert "serving path" in str(caught.value)


def test_enforce_returns_clean_text_unchanged():
    text = "The window entered EVENT after two confirming windows."
    assert claims.enforce(text) == text


def test_patterns_are_word_anchored_not_substring():
    """A substring check for 'proved' matches 'improved' and 'Provenance'."""
    assert claims.find_violations("Provenance is recorded.") == ()
    assert claims.find_violations("The improvement is bounded.") == ()


def test_the_guard_cannot_tell_a_disclaimer_from_an_assertion():
    """The limitation, pinned so nobody mistakes this for a semantic checker.

    Found in practice: the Evidence Agent's own "does not establish a
    diagnosis" block tripped claim 4. Regex negation detection would be a worse
    failure mode than the one it fixes, so curated disclaimers are exempted
    architecturally instead.
    """
    assertion = "This yields a diagnosis."
    disclaimer = "This does not establish a diagnosis."
    assert claims.find_violations(assertion)
    assert claims.find_violations(disclaimer), (
        "the guard is lexical; if it ever distinguishes these, this test and "
        "the disclaimer exemption should both be revisited"
    )


def test_approved_disclaimers_are_exempt_from_enforce():
    """Curated constants pass; the same claim in generated prose does not."""
    for disclaimer in claims.APPROVED_DISCLAIMERS:
        claims.enforce(f"This alert does not establish: {disclaimer}")
    with pytest.raises(claims.ClaimBoundaryError):
        claims.enforce("The alert supports a diagnosis of ischemia.")


def test_the_exemption_cannot_be_used_to_smuggle_a_claim():
    """Stripping a disclaimer must not blind the guard to the rest of the text."""
    text = (
        "a diagnosis -- this is detection, and the programme's scope is "
        "detection. Also, S4D outperforms GRU."
    )
    violations = {v.claim_number for v in claims.find_violations(text)}
    assert 22 in violations
