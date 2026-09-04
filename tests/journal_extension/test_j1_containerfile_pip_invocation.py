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
and would then pass while the real build failed.

## What sanitization means here, and what it must never do

An earlier version of this module dropped value-taking options *together with*
their values -- `--index-url https://pypi.org/simple` vanished entirely before
pip saw the command. That erased the very grammar under test: a malformed
`--index-url` would have disappeared instead of being rejected, and the
"derived from the committed bytes" check was circular, because an option the
sanitizer dropped was also absent from the set it compared against.

**Options are preserved. Only values are replaced.** A requirement path becomes
a controlled empty file; an index location becomes a `file://` URI of an empty
directory. A recognised value-taking option with no explicitly defined safe
value raises rather than being guessed at, and a value-taking option whose value
is missing or is itself an option raises before pip is invoked at all.

The proof that this does not launder defects is
`test_the_sanitizer_preserves_the_historical_defect`: the *historical* broken
command, passed through the same sanitizer, must still be rejected by pip.
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

#: The PyPI install exactly as the Containerfile carried it when 002 was
#: authorized. A literal, because it is a historical fact and reading it from
#: git would make this check skip on the shallow checkout CI uses.
HISTORICAL_BROKEN_COMMAND = (
    "python -m pip install --no-deps --require-hashes=false "
    "--index-url https://pypi.org/simple -r requirements.pypi.txt"
)

#: Options that consume the following token.
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

#: How each value-taking option's value is made safe. An option in
#: `VALUE_TAKING_OPTIONS` but absent here has no defined safe representation and
#: raises: guessing would either leak a real location into the executed command
#: or silently change what is being parsed.
VALUE_SANITIZERS = {
    "-r": "requirements",
    "--requirement": "requirements",
    "-c": "requirements",
    "--constraint": "requirements",
    "--index-url": "location",
    "-i": "location",
    "--extra-index-url": "location",
    "--find-links": "location",
    "-f": "location",
}

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

#: Controls this module adds that are not in the production command.
TEST_ONLY_ADDITIONS = frozenset({"--no-index", "--dry-run"})

#: Substrings that must never reach an executed argv.
FORBIDDEN_IN_ARGV = ("pypi.org", "download.pytorch.org", "https://", "http://")


class MalformedPipInvocation(AssertionError):
    """The Containerfile's command is not structurally a pip command.

    Raised *before* pip runs. A missing or option-shaped value must fail here
    rather than be normalised into something valid, which is exactly how the
    earlier `index += 2` sanitizer could have hidden a defect.
    """


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


def _safe_value(option: str, *, requirements: Path, index_dir: Path) -> str:
    family = VALUE_SANITIZERS.get(option)
    if family is None:
        raise MalformedPipInvocation(
            f"{option!r} takes a value but this module defines no safe test "
            "value for it. Add one deliberately -- a generic fallback would "
            "either leak a real location into the executed command or change "
            "what is being parsed."
        )
    if family == "requirements":
        return str(requirements)
    return index_dir.resolve().as_uri()


def production_option_names(command: str) -> set[str]:
    """Every option the Containerfile's command names, by its base spelling.

    Read straight from the command text, independently of the sanitizer, so
    that comparing the two cannot be circular.
    """
    names: set[str] = set()
    for token in shlex.split(command)[4:]:
        if token.startswith("-"):
            names.add(token.split("=", 1)[0])
    return names


def parser_argv(
    command: str, *, requirements: Path, index_dir: Path
) -> list[str]:
    """The command's own option grammar, with only its values made safe.

    Every option the Containerfile writes survives into the returned argv. A
    real `-r` path becomes the controlled empty file and a real `--index-url`
    becomes a local `file://` URI, so nothing is installed and nothing is
    fetched -- but pip still parses the same options in the same order, which is
    where the defect that spent 002 lived.

    Raises `MalformedPipInvocation` rather than repairing anything: a
    value-taking option with no value, or whose value is itself an option, is a
    finding, not something to normalise away.
    """
    tokens = shlex.split(command)
    if tokens[:4] != ["python", "-m", "pip", "install"]:
        raise MalformedPipInvocation(f"not a pip install invocation: {tokens[:4]}")

    options: list[str] = []
    saw_requirement_option = False
    rest = tokens[4:]
    index = 0
    while index < len(rest):
        token = rest[index]

        if token.startswith("-") and "=" in token:
            base, _, _value = token.partition("=")
            if base in VALUE_TAKING_OPTIONS:
                # Equals-form value option: keep the option, replace the value.
                options.extend(
                    [
                        base,
                        _safe_value(
                            base, requirements=requirements, index_dir=index_dir
                        ),
                    ]
                )
                if VALUE_SANITIZERS.get(base) == "requirements":
                    saw_requirement_option = True
                index += 1
                continue
            if base in KNOWN_BOOLEAN_OPTIONS:
                # Kept verbatim. `--require-hashes=false` is exactly this shape,
                # and pip must be the thing that rejects it -- not this module.
                options.append(token)
                index += 1
                continue
            raise MalformedPipInvocation(
                f"{token!r} is neither a known boolean nor a known "
                "value-taking pip option. Extend this module's tables "
                "deliberately rather than letting the extraction guess."
            )

        if token in VALUE_TAKING_OPTIONS:
            if index + 1 >= len(rest):
                raise MalformedPipInvocation(
                    f"{token!r} takes a value but the command ends after it."
                )
            value = rest[index + 1]
            if value.startswith("-"):
                raise MalformedPipInvocation(
                    f"{token!r} takes a value but is followed by {value!r}, "
                    "which is another option. The value is structurally missing."
                )
            options.extend(
                [
                    token,
                    _safe_value(token, requirements=requirements, index_dir=index_dir),
                ]
            )
            if VALUE_SANITIZERS.get(token) == "requirements":
                saw_requirement_option = True
            index += 2
            continue

        if token.startswith("-"):
            if token not in KNOWN_BOOLEAN_OPTIONS:
                raise MalformedPipInvocation(
                    f"{token!r} is neither a known boolean nor a known "
                    "value-taking pip option. Extend this module's tables "
                    "deliberately rather than letting the extraction guess."
                )
            options.append(token)
            index += 1
            continue

        # A bare requirement source -- a path or a specifier. Dropped: installing
        # the real source tree is a build, which this module must never do.
        index += 1

    argv = [sys.executable, "-m", "pip", "install", *options]
    if not saw_requirement_option:
        # The command installed from a positional source. Give pip an empty
        # requirements file so it has something to parse and nothing to do.
        argv += ["-r", str(requirements)]
    argv.append("--no-index")
    argv += _dry_run_flag()
    return argv


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
def sandbox(tmp_path: Path) -> tuple[Path, Path]:
    """An empty requirements file and an empty local index directory."""
    requirements = tmp_path / "empty-requirements.txt"
    requirements.write_text("", encoding="utf-8")
    index_dir = tmp_path / "empty-index"
    index_dir.mkdir()
    return requirements, index_dir


def _argv(command: str, sandbox: tuple[Path, Path]) -> list[str]:
    requirements, index_dir = sandbox
    return parser_argv(command, requirements=requirements, index_dir=index_dir)


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, check=False)


# -- the file really does contain pip invocations to guard ------------------


def test_the_containerfile_carries_pip_invocations_to_check() -> None:
    """If the extraction found nothing, every test below would pass vacuously."""
    commands = pip_commands_in_containerfile()
    assert len(commands) == 3, commands
    for command in commands:
        assert shlex.split(command)[:4] == ["python", "-m", "pip", "install"]


# -- the historical defect is detected, and the sanitizer does not hide it --


def test_the_historical_broken_option_is_rejected_by_pip(
    sandbox: tuple[Path, Path],
) -> None:
    """The guard must fail on the thing that actually happened."""
    requirements, _ = sandbox
    completed = _run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            HISTORICAL_BROKEN_OPTION,
            "-r",
            str(requirements),
            "--no-index",
            *_dry_run_flag(),
        ]
    )
    assert completed.returncode != 0
    combined = completed.stdout + completed.stderr
    assert HISTORICAL_PIP_ERROR in combined, combined[-500:]


def test_the_sanitizer_preserves_the_historical_defect(
    sandbox: tuple[Path, Path],
) -> None:
    """The whole point: sanitizing must not launder a broken command.

    The Containerfile's *historical* PyPI install -- the one that spent
    `J1-ENV-BUILDER-AUTH-002` -- is passed through the same `parser_argv` the
    live commands go through. If sanitization erased option grammar, this would
    come back valid and the guard would be worthless.
    """
    argv = _argv(HISTORICAL_BROKEN_COMMAND, sandbox)
    assert HISTORICAL_BROKEN_OPTION in argv
    assert "--index-url" in argv  # preserved, with a safe value
    assert "-r" in argv

    completed = _run(argv)
    assert completed.returncode != 0
    combined = completed.stdout + completed.stderr
    assert HISTORICAL_PIP_ERROR in combined, combined[-500:]


# -- every command in the file parses ---------------------------------------


@pytest.mark.parametrize(
    "command", pip_commands_in_containerfile(), ids=lambda c: c[:40]
)
def test_every_containerfile_pip_command_is_accepted_by_pip(
    command: str, sandbox: tuple[Path, Path]
) -> None:
    """pip accepts the option sequence the Containerfile actually writes.

    This is the check that did not exist when 002 was authorized.
    """
    completed = _run(_argv(command, sandbox))
    combined = completed.stdout + completed.stderr
    assert completed.returncode == 0, combined[-800:]
    assert "does not take a value" not in combined
    assert "no such option" not in combined.lower()


# -- options survive; only values are replaced ------------------------------


@pytest.mark.parametrize(
    "command", pip_commands_in_containerfile(), ids=lambda c: c[:40]
)
def test_every_production_option_survives_sanitization(
    command: str, sandbox: tuple[Path, Path]
) -> None:
    """No option may disappear between the Containerfile and the executed argv.

    The production options are read straight from the command text rather than
    from the sanitizer's output, so this cannot be satisfied by an option the
    sanitizer silently dropped -- which is exactly what the earlier version of
    this module did.
    """
    argv = _argv(command, sandbox)
    # argv[:4] is the interpreter prefix `<python> -m pip install`; its `-m`
    # belongs to Python, not to the command being compared.
    produced = {
        token.split("=", 1)[0] for token in argv[4:] if token.startswith("-")
    }
    for option in production_option_names(command):
        assert option in produced, (
            f"{option} is written in the Containerfile but does not reach pip"
        )
    # Anything extra is a declared test-only control, or `-r` standing in for a
    # positional requirement source the sanitizer must not install.
    extra = produced - production_option_names(command)
    assert extra <= TEST_ONLY_ADDITIONS | {"-r"}, extra


def test_the_requirement_and_index_options_are_kept_with_safe_values(
    sandbox: tuple[Path, Path],
) -> None:
    """`-r` and `--index-url` remain; their values are the sandbox's."""
    requirements, index_dir = sandbox
    pypi_command = next(
        c for c in pip_commands_in_containerfile() if "requirements.pypi.txt" in c
    )
    argv = _argv(pypi_command, sandbox)

    assert argv[argv.index("-r") + 1] == str(requirements)
    assert argv[argv.index("--index-url") + 1] == index_dir.resolve().as_uri()
    assert "requirements.pypi.txt" not in argv


# -- structurally malformed commands fail before pip is invoked -------------


def test_a_value_taking_option_with_no_value_is_refused(
    sandbox: tuple[Path, Path],
) -> None:
    with pytest.raises(MalformedPipInvocation, match="command ends after it"):
        _argv("python -m pip install --no-deps --index-url", sandbox)


def test_a_value_taking_option_followed_by_another_option_is_refused(
    sandbox: tuple[Path, Path],
) -> None:
    """`--index-url -r requirements.txt` must not consume `-r` as the URL.

    The dangerous shape: a sanitizer that blindly takes the next token would
    swallow `-r`, produce a command missing its requirements option, and report
    success for something nobody wrote.
    """
    with pytest.raises(MalformedPipInvocation, match="structurally missing"):
        _argv("python -m pip install --index-url -r requirements.txt", sandbox)


def test_a_value_taking_option_without_a_defined_safe_value_is_refused(
    sandbox: tuple[Path, Path],
) -> None:
    """Fail closed rather than guess at a safe substitute."""
    assert "--target" in VALUE_TAKING_OPTIONS
    assert "--target" not in VALUE_SANITIZERS
    with pytest.raises(MalformedPipInvocation, match="no safe test value"):
        _argv("python -m pip install --target /opt/somewhere", sandbox)


def test_an_unknown_option_is_refused(sandbox: tuple[Path, Path]) -> None:
    with pytest.raises(MalformedPipInvocation, match="neither a known boolean"):
        _argv("python -m pip install --invented-option", sandbox)


# -- equals-form handling ---------------------------------------------------


def test_an_equals_form_value_option_is_rewritten_not_treated_as_boolean(
    sandbox: tuple[Path, Path],
) -> None:
    """`--index-url=https://...` is a value option, and its value is replaced."""
    _, index_dir = sandbox
    argv = _argv(
        "python -m pip install --no-deps --index-url=https://pypi.org/simple",
        sandbox,
    )
    assert "--index-url" in argv
    assert argv[argv.index("--index-url") + 1] == index_dir.resolve().as_uri()
    assert not any("pypi.org" in token for token in argv)
    assert _run(argv).returncode == 0


def test_an_equals_form_boolean_survives_so_pip_can_reject_it(
    sandbox: tuple[Path, Path],
) -> None:
    """The historical defect's shape must reach pip, not be normalised away."""
    argv = _argv(
        f"python -m pip install --no-deps {HISTORICAL_BROKEN_OPTION}", sandbox
    )
    assert HISTORICAL_BROKEN_OPTION in argv
    completed = _run(argv)
    assert completed.returncode != 0
    assert HISTORICAL_PIP_ERROR in completed.stdout + completed.stderr


# -- the harness installs nothing and contacts nothing ----------------------


@pytest.mark.parametrize(
    "command", pip_commands_in_containerfile(), ids=lambda c: c[:40]
)
def test_the_preflight_neither_installs_nor_reaches_an_index(
    command: str, sandbox: tuple[Path, Path]
) -> None:
    """Proven from the constructed argv, so a regression fails here.

    Every external location is gone and `--no-index` is always present, so pip
    has no index to consult even if an option named one.
    """
    requirements, _ = sandbox
    argv = _argv(command, sandbox)
    assert "--no-index" in argv
    for token in argv:
        for forbidden in FORBIDDEN_IN_ARGV:
            assert forbidden not in token, f"{forbidden} survived into {token}"
    assert requirements.read_text(encoding="utf-8") == ""
    # No Docker, no buildx, no image: this is pip and nothing else.
    assert argv[:4] == [sys.executable, "-m", "pip", "install"]


def test_the_commands_are_derived_from_the_committed_bytes(
    sandbox: tuple[Path, Path],
) -> None:
    """No second copy of the command exists to drift out of step."""
    text = _containerfile_text()
    for command in pip_commands_in_containerfile():
        assert command.split()[0] == "python"
        for option in production_option_names(command):
            assert option in text, option


# -- structural regression guard, secondary to the executable one -----------


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
