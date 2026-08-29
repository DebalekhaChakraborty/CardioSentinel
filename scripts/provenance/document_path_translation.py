"""Resolve recorded document paths through translations V1 and V2.

The recorded value is never mutated. Resolution returns a separate current
path and fails closed when no explicit translation leads to an existing file.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
V1_TRANSLATION = REPOSITORY_ROOT / "docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md"
V2_TRANSLATION = REPOSITORY_ROOT / "docs/provenance/DOCUMENT_PATH_TRANSLATION_V2.md"

_TABLE_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*$")
_V1_PREFIXES = (
    ("docs/handbook/", "handbook/"),
    (
        "docs/CardioSentinel_Research_Execution_Handbook_",
        "handbook/CardioSentinel_Research_Execution_Handbook_",
    ),
    ("docs/PAPER_", "paper/PAPER_"),
    ("docs/LITERATURE_SEARCH_V1.md", "paper/LITERATURE_SEARCH_V1.md"),
)
_V2_PREFIXES = (
    ("paper/", "docs/paper/"),
    ("handbook/", "docs/handbook/"),
    ("handoffs/", "docs/handoffs/"),
)


class UnknownDocumentPathError(LookupError):
    """Raised when an explicit translation cannot resolve a recorded path."""


def _normalise(recorded_path: str | PurePosixPath) -> str:
    value = PurePosixPath(recorded_path).as_posix()
    if value.startswith("/") or value == "." or ".." in PurePosixPath(value).parts:
        raise UnknownDocumentPathError(f"unsafe document path: {recorded_path}")
    return value


def _v1_exact_translations() -> dict[str, str]:
    translations: dict[str, str] = {}
    for line in V1_TRANSLATION.read_text(encoding="utf-8").splitlines():
        match = _TABLE_ROW.match(line)
        if match and "*" not in match.group(1) and "..." not in match.group(1):
            translations[match.group(1)] = match.group(2)
    return translations


def _replace_prefix(value: str, translations: tuple[tuple[str, str], ...]) -> str:
    for old, new in translations:
        if value == old.rstrip("/"):
            return new.rstrip("/")
        if value.startswith(old):
            return new + value[len(old) :]
    return value


def translate_v1(recorded_path: str | PurePosixPath) -> PurePosixPath:
    """Apply only the explicit V1 table and its recorded directory rules."""

    value = _normalise(recorded_path)
    value = _v1_exact_translations().get(value, value)
    value = _replace_prefix(value, _V1_PREFIXES)
    return PurePosixPath(value)


def translate_v2(v1_current_path: str | PurePosixPath) -> PurePosixPath:
    """Apply the three explicit V2 directory translations."""

    return PurePosixPath(_replace_prefix(_normalise(v1_current_path), _V2_PREFIXES))


def resolve_current_path(
    recorded_path: str | PurePosixPath,
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> Path:
    """Return the current file without changing the recorded path value."""

    current = translate_v2(translate_v1(recorded_path))
    resolved = repository_root / current
    if not resolved.is_file():
        raise UnknownDocumentPathError(
            f"no explicit document translation resolves {recorded_path!s}"
        )
    return resolved
