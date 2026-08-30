from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_readme_has_research_only_disclaimer() -> None:
    readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

    assert "not a medical device" in readme
    assert "does not provide diagnosis" in readme


def test_legacy_archive_receipt_has_non_diagnostic_warning() -> None:
    archive_receipt = (
        REPOSITORY_ROOT / "docs" / "provenance" / "LEGACY_V0_ARCHIVE_V1.md"
    ).read_text(encoding="utf-8")

    assert "not part of the modern CardioSentinel pipeline" in archive_receipt
    assert "outputs are not clinical evidence" in archive_receipt
    assert "3e4936137d1bb102011ee3a81cd5d36e668fbd6d" in archive_receipt
    assert not (REPOSITORY_ROOT / "legacy").exists()
