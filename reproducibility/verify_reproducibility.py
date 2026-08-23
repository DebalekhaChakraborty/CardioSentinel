"""Check the demo bundle against the selection manifest. Exits non-zero on drift.

A `CHECKSUM_MANIFEST.md` plus "trust me" would be the one artifact in this
repository that nothing verifies, which is inconsistent with the project's own
argument that a boundary a human must remember is weaker than one a function
enforces (Handbook §53).

Run from the repository root:

    python reproducibility/verify_reproducibility.py

Checks, in order: every selected file is present; every digest matches; no
unexpected file has appeared in the bundle; and the manifest's own totals are
consistent. It verifies the **demo tier only** and says so.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reproducibility" / "DEMO_BUNDLE_SELECTION.json"
BUNDLE = ROOT / "reproducibility" / "demo_bundle"


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> list[str]:
    problems: list[str] = []
    if not MANIFEST.is_file():
        return [f"selection manifest missing: {MANIFEST}"]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    expected: dict[str, dict] = {}
    for entry in manifest["files"]:
        expected[entry["path"]] = entry
        path = BUNDLE / entry["path"]
        if not path.is_file():
            problems.append(f"missing from bundle: {entry['path']}")
            continue
        actual = digest(path)
        if actual != entry["sha256"]:
            problems.append(
                f"digest drift: {entry['path']}\n"
                f"    manifest {entry['sha256']}\n"
                f"    bundle   {actual}"
            )
        if path.stat().st_size != entry["bytes"]:
            problems.append(f"size drift: {entry['path']}")

    if BUNDLE.is_dir():
        for path in sorted(p for p in BUNDLE.rglob("*") if p.is_file()):
            relative = str(path.relative_to(BUNDLE))
            if relative not in expected:
                problems.append(
                    f"unselected file present in bundle: {relative}. The bundle "
                    "is curated; anything not in the manifest was not chosen."
                )

    if manifest["file_count"] != len(manifest["files"]):
        problems.append("manifest file_count disagrees with its own file list")
    total = sum(entry["bytes"] for entry in manifest["files"])
    if manifest["total_bytes"] != total:
        problems.append("manifest total_bytes disagrees with its own file list")
    return problems


def main() -> int:
    problems = verify()
    if problems:
        print(f"reproducibility bundle FAILED verification ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(
        f"demo bundle verified: {manifest['file_count']} files, "
        f"{manifest['total_bytes'] / 1_048_576:.2f} MiB, all digests match."
    )
    print("  scope: demo tier only. Research-tier claims are not re-verified here.")
    print("  external mirror: not required and not checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
