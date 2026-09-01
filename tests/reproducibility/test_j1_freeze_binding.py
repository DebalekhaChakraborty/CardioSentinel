"""The J1 freeze receipt binds two documents by digest. This proves it still does.

Governance only. Nothing here reads physiological data, runs a model, or computes
a scientific quantity: it recomputes two SHA-256 digests over raw committed bytes
and fails if either bound document has drifted from what the receipt records.

A scientific amendment is supposed to produce a new versioned protocol and a new
human freeze review. Without this check, an edit to a frozen document would leave
the receipt quietly describing bytes that no longer exist.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
J1 = ROOT / "docs" / "journal-extension" / "j1"
RECEIPT = J1 / "J1_FREEZE_RECEIPT_V1.md"

#: Path -> the receipt heading under which its digest row appears.
BOUND_DOCUMENTS = {
    "J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md": "Frozen protocol",
    "J1_PRE_REGISTRATION_V1.md": "Frozen pre-registration",
}

_SHA256_ROW = re.compile(r"\|\s*\*\*SHA-256\*\*\s*\|\s*`([0-9a-f]{64})`\s*\|")


def _recorded_digests() -> dict[str, str]:
    """Read each bound document's digest out of its own receipt section."""
    text = RECEIPT.read_text(encoding="utf-8")
    digests: dict[str, str] = {}
    for filename, heading in BOUND_DOCUMENTS.items():
        start = text.index(f"## {heading}")
        end = text.find("\n## ", start + 1)
        section = text[start : end if end != -1 else len(text)]
        assert filename in section, f"{heading} does not name {filename}"
        match = _SHA256_ROW.search(section)
        assert match is not None, f"no SHA-256 row under {heading}"
        digests[filename] = match.group(1)
    return digests


def test_the_receipt_binds_both_scientific_documents() -> None:
    assert RECEIPT.is_file()
    assert set(_recorded_digests()) == set(BOUND_DOCUMENTS)


def test_bound_documents_match_their_recorded_digests() -> None:
    """Raw bytes, no canonicalisation -- the receipt's own stated method."""
    for filename, recorded in _recorded_digests().items():
        actual = hashlib.sha256((J1 / filename).read_bytes()).hexdigest()
        assert actual == recorded, (
            f"{filename} has drifted from the J1 freeze receipt.\n"
            f"  recorded: {recorded}\n"
            f"  actual:   {actual}\n"
            "A scientific amendment requires a new versioned protocol and "
            "pre-registration, new digests and a new human freeze review -- not an "
            "edit in place."
        )


def test_the_freeze_grants_no_authority() -> None:
    """Pre-registration is not authorization, and the receipt must keep saying so."""
    text = RECEIPT.read_text(encoding="utf-8")
    for claim in (
        "`real_data_authority` | **NONE**",
        "`attempt_budget` | **NOT ESTABLISHED**",
        "`execution_authorized` | **FALSE**",
        "`fold_manifest` | **NOT GENERATED**",
        "`results` | **NONE**",
    ):
        assert claim in text, claim
    assert not (J1 / "J1_AUTHORIZATION_V1.md").exists()
