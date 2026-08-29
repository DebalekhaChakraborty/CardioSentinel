"""Create and verify the byte-level receipt for document hierarchy migration V2."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

MOVE_ROOTS = ("paper", "handbook", "handoffs")
FIELDNAMES = (
    "old_path",
    "new_path",
    "byte_size",
    "sha256",
    "content_frozen",
    "role",
    "tracked",
)

_FROZEN_PAPER_FILES = frozenset(
    {
        "paper/ABSTRACT_CLAIM_AUDIT_V1.md",
        "paper/CARDIOSENTIN_TACTICS_MANUSCRIPT_V1.md",
        "paper/CARDIOSENTIN_TACTICS_MANUSCRIPT_V2_BODY_FROZEN.md",
        "paper/CARDIOSENTIN_TACTICS_MANUSCRIPT_V3_FINAL_CANDIDATE.md",
        "paper/CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md",
        "paper/LITERATURE_SEARCH_V1.md",
        "paper/MANUSCRIPT_V2_ASSEMBLY_PROVENANCE.md",
    }
)


@dataclass(frozen=True)
class ReceiptRow:
    old_path: str
    new_path: str
    byte_size: int
    sha256: str
    content_frozen: str
    role: str
    tracked: str

    def as_dict(self) -> dict[str, str | int]:
        return {name: getattr(self, name) for name in FIELDNAMES}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tracked_paths(root: Path) -> frozenset[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *MOVE_ROOTS],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return frozenset(
        value.decode("utf-8") for value in result.stdout.split(b"\0") if value
    )


def _policy(old_path: str) -> tuple[str, str]:
    path = PurePosixPath(old_path)
    if path.parts[0] == "handbook":
        return "Y", "FROZEN_HANDBOOK"
    if path.parts[0] == "handoffs":
        return "Y", "HISTORICAL_HANDOFF"
    if old_path in _FROZEN_PAPER_FILES:
        return "Y", "FROZEN_OR_HISTORICAL_PAPER"
    if (
        len(path.parts) >= 3
        and path.parts[:2] == ("paper", "figures")
        and path.suffix in {".pdf", ".png"}
    ):
        return "Y", "FROZEN_PUBLICATION_ASSET"
    if path.parts[:2] == ("paper", "drafts"):
        return "N", "IGNORED_OWNER_DRAFT"
    return "N", "LIVE_PAPER_SOURCE"


def inventory(root: Path) -> list[ReceiptRow]:
    tracked = _tracked_paths(root)
    rows: list[ReceiptRow] = []
    for directory in MOVE_ROOTS:
        for path in sorted((root / directory).rglob("*")):
            if not path.is_file():
                continue
            old_path = path.relative_to(root).as_posix()
            frozen, role = _policy(old_path)
            rows.append(
                ReceiptRow(
                    old_path=old_path,
                    new_path=(PurePosixPath("docs") / old_path).as_posix(),
                    byte_size=path.stat().st_size,
                    sha256=_sha256(path),
                    content_frozen=frozen,
                    role=role,
                    tracked="Y" if old_path in tracked else "N",
                )
            )
    return rows


def write_rows(rows: Iterable[ReceiptRow]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDNAMES, dialect="excel-tab")
    writer.writeheader()
    writer.writerows(row.as_dict() for row in rows)


def verify(root: Path, receipt: Path) -> int:
    failures: list[str] = []
    checked = 0
    with receipt.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, dialect="excel-tab"):
            checked += 1
            current = root / row["new_path"]
            if not current.is_file():
                failures.append(f"missing: {row['new_path']}")
                continue
            if current.stat().st_size != int(row["byte_size"]):
                failures.append(f"size: {row['new_path']}")
            if _sha256(current) != row["sha256"]:
                failures.append(f"sha256: {row['new_path']}")
    for failure in failures:
        print(failure, file=sys.stderr)
    print(f"checked={checked} failures={len(failures)}")
    return int(bool(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.verify is not None:
        return verify(root, args.verify.resolve())
    write_rows(inventory(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
