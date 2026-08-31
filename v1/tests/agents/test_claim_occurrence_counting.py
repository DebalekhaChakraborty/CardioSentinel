"""Every occurrence of a forbidden claim must be reported, not the first.

`find_violations` used `re.search`, which returns at most one match per
pattern. A document that broke the same boundary five times therefore reported
one violation, and anyone counting the output under-counted by four. The
assembled manuscript made the gap concrete: **fifteen occurrences reported as
nine.**

The pass/fail decision was never wrong -- `enforce` raises on a non-empty
tuple, and one violation is as non-empty as five. What was wrong is that an
audit could not classify occurrences it could not see, and classification is
the whole of the manuscript claim-guard pass: genuine overclaim, declared
quotation, or lexical collision are three different outcomes and only the first
requires an edit.
"""

from __future__ import annotations

import re

from cardiosentinel.agents import claims


def _numbers(text: str) -> list[int]:
    return [v.claim_number for v in claims.find_violations(text)]


# -- A, B, C: counting ------------------------------------------------------


def test_a_one_occurrence_yields_one_finding() -> None:
    found = claims.find_violations("The system is deployment-ready.")
    assert len(found) == 1
    assert found[0].claim_number == 2


def test_b_three_occurrences_of_one_pattern_yield_three_findings() -> None:
    text = (
        "It is deployment-ready. We repeat that it is deployment-ready. "
        "A third time: deployment-ready."
    )
    found = claims.find_violations(text)
    assert len(found) == 3
    assert {v.claim_number for v in found} == {2}
    assert [v.matched for v in found] == ["deployment-ready"] * 3


def test_c_multiple_patterns_multiple_times_all_returned() -> None:
    text = (
        "It is deployment-ready and externally validated. "
        "Again: deployment-ready, and again externally validated. "
        "It also shows early detection."
    )
    found = claims.find_violations(text)
    counts: dict[int, int] = {}
    for v in found:
        counts[v.claim_number] = counts.get(v.claim_number, 0) + 1
    assert counts[2] == 2, "both 'deployment-ready' occurrences"
    assert counts[24] == 2, "both 'externally validated' occurrences"
    assert counts[17] == 1, "the single 'early detection'"
    assert len(found) == 5


def test_c_the_old_search_semantics_would_have_missed_these() -> None:
    """Pin the defect, so a revert to `re.search` fails here rather than quietly."""
    text = "deployment-ready ... deployment-ready ... deployment-ready"
    pattern = next(p for n, p, _, _ in claims.FORBIDDEN_CLAIMS if n == 2)
    assert len(re.findall(pattern, text, re.I)) == 3
    assert len(claims.find_violations(text)) == 3


# -- D, E: quotation handling remains caller-declared ----------------------


def test_d_a_declared_quotation_is_removed_and_others_still_fire() -> None:
    text = (
        "The boundary forbids the phrase 'deployment-ready'. "
        "Separately, this system is externally validated."
    )
    assert claims.audit(text, quoting=["deployment-ready"]) != ()
    remaining = claims.audit(text, quoting=["deployment-ready"])
    assert {v.claim_number for v in remaining} == {24}, (
        "declaring one quotation must not suppress a different boundary"
    )


def test_e_a_quotation_is_not_a_document_wide_exemption() -> None:
    text = (
        "We quote 'early detection' to prohibit it. "
        "But the system is also deployment-ready and externally validated."
    )
    remaining = claims.audit(text, quoting=["early detection"])
    assert {v.claim_number for v in remaining} == {2, 24}
    assert 17 not in {v.claim_number for v in remaining}


def test_e_declaring_a_quotation_exempts_every_identical_occurrence() -> None:
    """Recorded because it is a real limit, not because it is desirable.

    `strip_approved_disclaimers` removes the declared string wherever it
    appears. A phrase quoted once and asserted once elsewhere is exempted in
    both places. The alternative -- exempting only the first occurrence --
    would be worse: it would depend on document order, so moving a paragraph
    would change the verdict. **The caller declaring a quotation is asserting
    something about that phrase in that document, and the audit must say so
    rather than imply per-site precision it does not have.**
    """
    text = "We forbid 'deployment-ready'. This system is deployment-ready."
    assert claims.audit(text, quoting=["deployment-ready"]) == ()


def test_d_quotation_matching_stays_whitespace_insensitive() -> None:
    wrapped = "The boundary forbids\nthe phrase deployment-ready today."
    assert claims.audit(wrapped, quoting=["the phrase deployment-ready"]) == ()


# -- F: determinism ---------------------------------------------------------


def test_f_ordering_is_deterministic_and_by_pattern_then_position() -> None:
    text = (
        "externally validated first, then deployment-ready, "
        "then externally validated again."
    )
    found = claims.find_violations(text)
    assert [v.claim_number for v in found] == sorted([v.claim_number for v in found]), (
        "patterns are emitted in FORBIDDEN_CLAIMS order"
    )
    by_claim: dict[int, list[int]] = {}
    for v in found:
        by_claim.setdefault(v.claim_number, []).append(v.start)
    for offsets in by_claim.values():
        assert offsets == sorted(offsets), "occurrences in text order"


def test_f_repeated_calls_return_identical_results() -> None:
    text = "deployment-ready, externally validated, deployment-ready"
    assert claims.find_violations(text) == claims.find_violations(text)


def test_f_every_violation_carries_a_real_offset() -> None:
    text = "deployment-ready and again deployment-ready"
    for v in claims.find_violations(text):
        assert v.start >= 0
        assert text[v.start : v.start + len(v.matched)].lower() == v.matched.lower()


# -- semantics preserved ----------------------------------------------------


def test_enforce_still_raises_and_clean_text_still_passes() -> None:
    assert claims.enforce("The window score is bounded.") is not None
    try:
        claims.enforce("This system is deployment-ready.")
    except claims.ClaimBoundaryError:
        pass
    else:  # pragma: no cover
        raise AssertionError("enforce must still raise")


def test_clean_text_reports_nothing() -> None:
    assert claims.find_violations("Provenance is recorded.") == ()
    assert _numbers("The improvement is bounded.") == []
