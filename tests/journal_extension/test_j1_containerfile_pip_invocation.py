"""The executable boundary the apparatus review never crossed: pip's own parser.

**No image is built, no package is installed, no index is contacted, and no
builder is authorized.** Every check here runs `python -m pip install` as a
subprocess against an empty requirements file with `--no-index`, so pip parses
arguments and then has nothing to do.

Qualification `J1-ENV-BUILDER-AUTH-002` was spent on discovering that this
boundary was untested. Run `33902875021` admitted at its gate, recorded the
canonical claim, and then failed in both builds at the same instruction:

```text
--require-hashes option does not take a value
```

`--require-hashes` is a boolean flag. The Containerfile passed
`--require-hashes=false`, so pip exited 2 during argument parsing, before
installing anything. Every check that existed proved things *about* the
Containerfile -- its SHA-256, its membership in the build configuration, its
presence at the authorized source commit -- and not one of them proved that the
command inside it was a command pip would accept.

**The commands are derived from the committed Containerfile bytes**, never
retyped here. A hand-written copy would drift from the file it claims to guard
and would then pass while the real build failed, which is the failure mode this
module exists to close.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
CONTAINERFILE = REPOSITORY_ROOT / "containers/j1-environment/Containerfile"

#: The historical defect, quoted from run 33902875021's logs.
HISTORICAL_BROKEN_OPTION = "--require-hashes=false"
HISTORICAL_PIP_ERROR = "--require-hashes option does not take a value"

#: pip options that consume the following token. Their values are paths, URLs
#: and indexes -- exactly what must NOT reach a parser-level test, because a
#: real requirements file or a real index would turn parsing into resolution.
VALUE_TAKING_OPTIONS = frozenset(
    {
        "-r",
        "--requirement",
        "-c",
        "--constraint",
        "--index-url",
        "-i",
        "--extra-index-url",
        "--find-links",
        "-f",
        "--target",
        "-t",
        "--prefix",
        "--root",
        "--python-version",
        "--platform",
        "--abi",
        "--implementation",
    }
)

#: Boolean options this repository's Containerfile is permitted to use. An
#: option in neither set fails the extraction loudly rather than being guessed
#: at: a misparse would silently test a command nobody wrote.
KNOWN_BOOLEAN_OPTIONS = frozenset(
    {
        "--no-deps",
        "--no-build-isolation",
        "--no-index",
        "--no-cache-dir",
        "--dry-run",
        "--require-hashes",
        "--upgrade",
        "--force-reinstall",
        "--pre",
        "--user",
        "--quiet",
        "-q",
        "--verbose",
        "-v",
    }
)


def _containerfile_text() -> str:
    return CONTAINERFILE.read_text(encoding="utf-8")


def pip_commands_in_containerfile() -> list[str]:
    """Every `python -m pip install ...` the Containerfile actually runs.

    Backslash continuations are joined first, so a command split across five
    physical lines is read as the one command the shell would see. Then each
    `RUN` instruction is split on `&&`, because a single `RUN` here carries two
    independent pip invocations against two different indexes.
    """
    joined = re.sub(r"\\\n\s*", " ", _containerfile_text())
    run_bodies = [
        line[len("RUN ") :].strip()
        for line in joined.splitlines()
        if line.startswith("RUN ")
    ]
    commands: list[str] = []
    for body in run_bodies:
        for part in body.split("&&"):
            part = part.strip()
            if "python -m pip install" in part:
                commands.append(part)
    return commands


def parser_argv(command: str, *, requirements: Path) -> list[str]:
    """The command's own options, pointed at an empty requirements file.

    Values are dropped rather than passed through: a real `--index-url` would
    invite a network call and a real `-r` would invite resolution, and neither
    is what is being tested. What survives is the option sequence the
    Containerfile actually wrote -- which is where the defect lived.

    An option in neither known set raises. Failing closed matters here: silently
    treating an unrecognised option as a boolean would drop the token after it
    and test a command that was never in the file.
    """
    tokens = shlex.split(command)
    if tokens[:4] != ["python", "-m", "pip", "install"]:
        raise AssertionError(f"not a pip install invocation: {tokens[:4]}")

    options: list[str] = []
    rest = tokens[4:]
    index = 0
    while index < len(rest):
        token = rest[index]
        if token in VALUE_TAKING_OPTIONS:
            index += 2  # drop the option together with its value
            continue
        if token.startswith("-"):
            base = token.split("=", 1)[0]
            if base not in KNOWN_BOOLEAN_OPTIONS and base not in VALUE_TAKING_OPTIONS:
                raise AssertionError(
                    f"{token!r} is neither a known boolean nor a known "
                    "value-taking pip option. Extend this module's tables "
                    "deliberately rather than letting the extraction guess."
                )
            options.append(token)
            index += 1
            continue
        index += 1  # a bare requirement source (path or spec): dropped
    return [
        sys.executable,
        "-m",
        "pip",
        "install",
        *options,
        "-r",
        str(requirements),
        "--no-index",
        *_dry_run_flag(),
    ]


def _dry_run_flag() -> list[str]:
    """`--dry-run` when this pip has it, nothing when it does not.

    Probed rather than assumed: `--dry-run` arrived in pip 22.2, and CI resolves
    its own pip. An empty requirements file installs nothing either way, so this
    is belt-and-braces -- but passing an unsupported option would fail the
    corrected command for a reason that has nothing to do with the Containerfile.
    """
    helped = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    return ["--dry-run"] if "--dry-run" in helped.stdout else []


@pytest.fixture
def empty_requirements(tmp_path: Path) -> Path:
    path = tmp_path / "empty-requirements.txt"
    path.write_text("", encoding="utf-8")
    return path


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, check=False)


# -- the file really does contain pip invocations to guard ------------------


def test_the_containerfile_carries_pip_invocations_to_check() -> None:
    """If the extraction found nothing, every test below would pass vacuously."""
    commands = pip_commands_in_containerfile()
    assert len(commands) >= 2, commands
    for command in commands:
        assert shlex.split(command)[:4] == ["python", "-m", "pip", "install"]


# -- 6.3 the historical defect is detected ----------------------------------


def test_the_historical_broken_option_is_rejected_by_pip(
    empty_requirements: Path,
) -> None:
    """The guard must fail on the thing that actually happened.

    A guard that only confirms the current file is fine cannot tell you whether
    it would have caught the defect. This runs the exact option form that broke
    run 33902875021 and requires pip to reject it.
    """
    completed = _run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            HISTORICAL_BROKEN_OPTION,
            "-r",
            str(empty_requirements),
            "--no-index",
            *_dry_run_flag(),
        ]
    )
    assert completed.returncode != 0
    combined = completed.stdout + completed.stderr
    assert HISTORICAL_PIP_ERROR in combined, combined[-500:]


# -- 6.4 every command in the file parses -----------------------------------


@pytest.mark.parametrize(
    "command", pip_commands_in_containerfile(), ids=lambda c: c[:40]
)
def test_every_containerfile_pip_command_is_accepted_by_pip(
    command: str, empty_requirements: Path
) -> None:
    """pip accepts the option sequence the Containerfile actually writes.

    This is the check that did not exist when 002 was authorized.
    """
    completed = _run(parser_argv(command, requirements=empty_requirements))
    combined = completed.stdout + completed.stderr
    assert completed.returncode == 0, combined[-800:]
    assert "does not take a value" not in combined
    assert "no such option" not in combined.lower()


# -- 6.2 the harness installs nothing and contacts nothing ------------------


def test_the_preflight_neither_installs_nor_reaches_an_index(
    empty_requirements: Path,
) -> None:
    """`--no-index` is always passed and the requirements file is empty.

    Proven from the constructed argv rather than asserted in prose, so a future
    edit that drops `--no-index` fails here instead of quietly going online.
    """
    for command in pip_commands_in_containerfile():
        argv = parser_argv(command, requirements=empty_requirements)
        assert "--no-index" in argv
        assert "--index-url" not in argv
        assert "--extra-index-url" not in argv
        requirement = Path(argv[argv.index("-r") + 1])
        assert requirement.read_text(encoding="utf-8") == ""
        # No Docker, no buildx, no image: this is pip and nothing else.
        assert argv[:4] == [sys.executable, "-m", "pip", "install"]


def test_the_commands_are_derived_from_the_committed_bytes(
    empty_requirements: Path,
) -> None:
    """No second copy of the command exists to drift out of step.

    Every option checked above is present in the Containerfile's own text. If
    this module ever grew a hand-written invocation, that option would not be
    found here.
    """
    text = _containerfile_text()
    for command in pip_commands_in_containerfile():
        for option in parser_argv(command, requirements=empty_requirements):
            if option.startswith("--") and option not in {"--no-index", "--dry-run"}:
                assert option in text, option


# -- 7. structural regression guard, secondary to the executable one --------


def test_no_pip_boolean_option_is_written_in_the_invalid_equals_form() -> None:
    """`--require-hashes=` is the shape of the historical defect.

    Secondary defence only. The executable checks above are what actually prove
    the command works; this catches the specific written form at a glance and
    would have failed on the Containerfile as authorized for 002.
    """
    for command in pip_commands_in_containerfile():
        for token in shlex.split(command):
            if not token.startswith("-") or "=" not in token:
                continue
            base = token.split("=", 1)[0]
            assert base not in KNOWN_BOOLEAN_OPTIONS, (
                f"{token!r} gives a value to the boolean option {base!r}; pip "
                "refuses this at argument-parsing time. This is the defect that "
                "spent J1-ENV-BUILDER-AUTH-002."
            )


def test_the_specific_historical_form_is_gone() -> None:
    assert HISTORICAL_BROKEN_OPTION not in _containerfile_text()


# -- the repair did not smuggle in a different meaning ----------------------


def test_hash_checking_was_omitted_rather_than_disabled_by_another_spelling(
) -> None:
    """The fix is to omit the flag, not to spell "off" a second way.

    `--no-require-hashes` does not exist, and adding `--require-hashes` would
    demand a hash for every pin -- a different guarantee than the one the
    frozen mapping currently provides, and not something to change while
    repairing a syntax defect.
    """
    text = _containerfile_text()
    assert "--no-require-hashes" not in text
    assert "--require-hashes" not in text
