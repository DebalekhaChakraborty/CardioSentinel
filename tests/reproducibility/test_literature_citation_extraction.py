"""Adversarial tests for the §2 citation verifier's key extraction.

`scripts/literature_search.py` is the gate that makes an invented citation
impossible: `verify` fails if a draft cites anything the recorded search did
not return. **For its whole working life that gate had a false negative.**

Extraction was a single regex, ``\\[((?:doi|arxiv|pmid):[^\\]\\s]+)\\]``, which
requires the closing bracket to follow the identifier immediately. A bracket
holding two keys matched nothing, so *neither* key was checked. Seven such
brackets in `PAPER_S2_RELATED_WORK_DRAFT.md` hid sixteen keys, and the check
reported 71 citations against 87 while printing a clean result.

The consequence is the one that matters: **an invented citation written second
in a shared bracket escaped the gate entirely.** `test_invented_second_key_*`
below is that case, and it is the reason this file exists.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_SCRIPT = (
    pathlib.Path(__file__).resolve().parents[2] / "scripts" / "literature_search.py"
)
_SPEC = importlib.util.spec_from_file_location("literature_search", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
literature_search = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(literature_search)

citation_keys = literature_search.citation_keys


# -- A: the case that always worked ----------------------------------------


def test_a_single_key_is_found() -> None:
    assert citation_keys("text [doi:10.1234/abc] more") == ["doi:10.1234/abc"]


@pytest.mark.parametrize(
    "text,expected",
    [
        ("[arxiv:1234.56789]", ["arxiv:1234.56789"]),
        ("[pmid:12345678]", ["pmid:12345678"]),
        ("[arxiv:2005.11401v4]", ["arxiv:2005.11401v4"]),
    ],
)
def test_a_every_supported_scheme_is_found(text: str, expected: list[str]) -> None:
    assert citation_keys(text) == expected


# -- B and C: the case that did not ----------------------------------------


def test_b_two_keys_in_one_bracket_are_both_found() -> None:
    assert citation_keys("[doi:10.1234/abc, arxiv:1234.56789]") == [
        "doi:10.1234/abc",
        "arxiv:1234.56789",
    ]


def test_c_three_mixed_key_types_are_all_found() -> None:
    assert citation_keys("[doi:10.1234/abc, arxiv:1234.56789, pmid:12345678]") == [
        "doi:10.1234/abc",
        "arxiv:1234.56789",
        "pmid:12345678",
    ]


# -- D: the regression this file exists for --------------------------------


def test_d_invented_second_key_in_shared_bracket_is_extracted() -> None:
    """The old extractor returned nothing here, so the invention was invisible."""
    keys = citation_keys("[doi:10.1234/real, arxiv:9999.99999]")
    assert "arxiv:9999.99999" in keys


def test_d_invented_second_key_makes_verify_fail(tmp_path: pathlib.Path) -> None:
    """End to end: a bad key hidden behind a good one must exit non-zero."""
    record = tmp_path / "record.json"
    record.write_text(
        '{"results": [{"hits": [{"identifier": "doi:10.1234/real"}]}]}',
        encoding="utf-8",
    )
    draft = tmp_path / "draft.md"
    draft.write_text("A claim [doi:10.1234/real, arxiv:9999.99999].", encoding="utf-8")

    assert literature_search.verify(draft, record) == 1


def test_d_shared_bracket_of_known_keys_still_passes(tmp_path: pathlib.Path) -> None:
    """The fix must not turn every shared bracket into a failure."""
    record = tmp_path / "record.json"
    record.write_text(
        '{"results": [{"hits": ['
        '{"identifier": "doi:10.1234/real"}, {"identifier": "arxiv:1234.56789"}'
        "]}]}",
        encoding="utf-8",
    )
    draft = tmp_path / "draft.md"
    draft.write_text("A claim [doi:10.1234/real, arxiv:1234.56789].", encoding="utf-8")

    assert literature_search.verify(draft, record) == 0


# -- E: counting ------------------------------------------------------------


def test_e_duplicates_do_not_inflate_the_unique_count() -> None:
    text = "[doi:10.1234/abc] and again [doi:10.1234/abc] and [arxiv:1234.56789]"
    keys = citation_keys(text)
    assert len(keys) == 3
    assert len(set(keys)) == 2


# -- F: separator and whitespace variation ---------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "[doi:10.1234/abc, arxiv:1234.56789]",
        "[doi:10.1234/abc; arxiv:1234.56789]",
        "[doi:10.1234/abc,arxiv:1234.56789]",
        "[doi:10.1234/abc ,  arxiv:1234.56789 ]",
        "[ doi:10.1234/abc , arxiv:1234.56789 ]",
    ],
)
def test_f_separator_variation_does_not_change_extraction(text: str) -> None:
    assert citation_keys(text) == ["doi:10.1234/abc", "arxiv:1234.56789"]


def test_f_a_bracket_straddling_a_line_break_is_still_read() -> None:
    """The manuscript wraps at 79 columns; a shared bracket can span lines."""
    text = "leakage [doi:10.1016/j.patter.2023.100804,\narxiv:2207.07048] is common"
    assert citation_keys(text) == [
        "doi:10.1016/j.patter.2023.100804",
        "arxiv:2207.07048",
    ]


def test_f_trailing_sentence_punctuation_is_not_part_of_the_identifier() -> None:
    assert citation_keys("[doi:10.1234/abc.]") == ["doi:10.1234/abc"]


# -- G: malformed input fails closed ---------------------------------------


def test_g_a_scheme_with_no_identifier_is_surfaced_not_dropped() -> None:
    """`[doi:]` must become a reported key, not silently vanish."""
    assert citation_keys("[doi:]") == ["doi:"]


def test_g_malformed_key_makes_verify_fail(tmp_path: pathlib.Path) -> None:
    record = tmp_path / "record.json"
    record.write_text('{"results": [{"hits": []}]}', encoding="utf-8")
    draft = tmp_path / "draft.md"
    draft.write_text("A claim [doi:].", encoding="utf-8")

    assert literature_search.verify(draft, record) == 1


def test_g_text_that_is_not_a_citation_is_not_extracted() -> None:
    assert citation_keys("see [Table 1] and [Figure 2]") == []
    assert citation_keys("a bare doi:10.1234/abc outside a bracket") == []


# -- the live section -------------------------------------------------------


#: The three shared brackets that carried the defect, copied verbatim from
#: `PAPER_S2_RELATED_WORK_DRAFT.md` before the V1 publication workspace was
#: retired, plus the single-bracket keys the guard also names. The defect was in
#: `citation_keys`, not in the document, so the guard is kept and its dependency
#: on a retired file removed -- reading that file passed only where the gitignored
#: directory survived on disk.
_SHARED_BRACKET_SECTION = """
Calibration is discussed in [arxiv:1706.04599, arxiv:2106.07998].
Episode reasoning draws on [doi:10.1109/cic.2008.4749058, pmid:20130344].
Representation work spans [arxiv:2006.01862, arxiv:2202.03673, arxiv:2310.14774].
Reporting guidance is in [doi:10.1016/j.patter.2023.100804] and [arxiv:2207.07048].
Provenance practice follows [doi:10.2172/826602].
Calibration again, reusing a key: [arxiv:1706.04599].
"""


def test_the_live_section_has_no_hidden_keys() -> None:
    """Regression against the exact defect: a shared bracket hiding keys."""
    keys = citation_keys(_SHARED_BRACKET_SECTION)
    shared_bracket_keys = {
        "doi:10.1109/cic.2008.4749058",
        "pmid:20130344",
        "doi:10.1016/j.patter.2023.100804",
        "arxiv:2207.07048",
        "doi:10.2172/826602",
        "arxiv:1706.04599",
        "arxiv:2106.07998",
        "arxiv:2310.14774",
    }
    assert shared_bracket_keys <= set(keys)
    assert len(keys) > len(set(keys)), "the section does reuse keys"
    assert len(keys) == 11, "every key in every bracket is extracted"


# -- resolution across more than one harvest --------------------------------


def test_resolution_is_the_union_of_the_supplied_records(
    tmp_path: pathlib.Path,
) -> None:
    """A re-harvest is not idempotent, so V1 and V2 are both authoritative.

    Relevance ranking moves between sessions. A key that only V1 returned is
    still a key a registered search returned, and pasting it into V2 to make
    one record look complete would be the back-filling the V1 digest exists to
    prevent.
    """
    v1 = tmp_path / "v1.json"
    v1.write_text(
        '{"results": [{"hits": [{"identifier": "arxiv:1706.04599"}]}]}',
        encoding="utf-8",
    )
    v2 = tmp_path / "v2.json"
    v2.write_text(
        '{"results": [{"hits": [{"identifier": "arxiv:2509.06902"}]}]}',
        encoding="utf-8",
    )
    draft = tmp_path / "draft.md"
    draft.write_text("Both [arxiv:1706.04599, arxiv:2509.06902].", encoding="utf-8")

    assert literature_search.verify(draft, v1) == 1
    assert literature_search.verify(draft, v2) == 1
    assert literature_search.verify(draft, v1, v2) == 0
