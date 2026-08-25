"""Categorical state alignment: does the prose agree with the structured fields?

**Registered after Arm B, because running the experiment found what anticipating
it did not.** A fluent, correctly-rounded, claim-compliant explanation asserted
*"The system passed several safety checks, including G1 through G6"* when G4 and
G5 were blocked. Every gate then in force passed it: the claim guard saw no
forbidden pattern, the numeric guard saw no unsupported number (`G1` is not a
numeric claim -- the digit follows a letter), fidelity scored 1.000.

Numeric and lexical guards enforce numeric and lexical properties. **Neither
compares a categorical assertion against the field that records the truth.**

**Deterministic by construction.** No second model judges the first: a generative
judge moves the boundary from something checkable into something that must be
trusted, and this programme's contribution is that its constraints are
executable. There is no semantic inference here -- a fixed vocabulary, range
expansion, and polarity by proximity -- and it **fails closed**: an assertion
that cannot be aligned is a violation, not a pass.

**It is lexical, and therefore insufficient on its own**, exactly as handbook
§53.1 says of the claim guard. A third necessary condition, not a sufficient one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .context import ExplanationContext

#: Gate identifiers as the evidence names them: G1 … G6.
_GATE = re.compile(r"\bG([1-9])\b")

#: `G1 through G6`, `G1-G6`, `G1 to G6`. A range asserts every gate it spans,
#: which is how the observed failure smuggled G4 and G5 into a passing claim.
_GATE_RANGE = re.compile(r"\bG([1-9])\s*(?:-|--|–|through|thru|to)\s*G([1-9])\b", re.I)

#: The four states of the frozen episode protocol.
_LIFECYCLE = ("NORMAL", "WATCH", "EVENT", "RECOVERY")
_LIFECYCLE_TOKEN = re.compile(r"\b(" + "|".join(_LIFECYCLE) + r")\b", re.I)

#: Fixed vocabularies. Deliberately small: a word not listed produces no
#: polarity, and a gate with no polarity is not judged rather than guessed at.
_PASSED = (
    "passed", "passes", "pass", "satisfied", "met", "cleared", "clear",
    "succeeded", "admitted", "allowed", "ok",
)
_BLOCKED = (
    "blocked", "blocks", "block", "refused", "declined", "failed", "fails",
    "prevented", "denied", "withheld", "stopped",
)
_UNIVERSAL = ("all", "every", "each", "both", "any of the")

_PASSED_RE = re.compile(r"\b(" + "|".join(_PASSED) + r")\b", re.I)
_BLOCKED_RE = re.compile(r"\b(" + "|".join(_BLOCKED) + r")\b", re.I)
_UNIVERSAL_RE = re.compile(r"\b(" + "|".join(_UNIVERSAL) + r")\b", re.I)
_SENTENCE = re.compile(r"[^.!?]+[.!?]?")

#: Clause separators. Proximity alone attributes a gate to the nearest polarity
#: marker, which is wrong across a contrast: in "G1, G2, G3 and G6 passed, while
#: G4 and G5 blocked", G4 sits closer to "passed" than to "blocked" and would be
#: read as passing -- flagging the one summary that is correct. Splitting on the
#: contrast first keeps each polarity with the gates it governs.
_CLAUSE = re.compile(
    r"\s*(?:;|\bwhile\b|\bwhereas\b|\bbut\b|\balthough\b|\bhowever\b)\s*",
    re.I,
)

PASSED = "passed"
BLOCKED = "blocked"


@dataclass(frozen=True)
class AlignmentViolation:
    """One categorical assertion the evidence contradicts."""

    kind: str
    asserted: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.detail}"


def _gates_in(fragment: str) -> set[str]:
    """Every gate a fragment names, ranges expanded to the gates they span."""
    gates: set[str] = set()
    for low, high in _GATE_RANGE.findall(fragment):
        start, end = sorted((int(low), int(high)))
        gates.update(f"G{index}" for index in range(start, end + 1))
    gates.update(f"G{digit}" for digit in _GATE.findall(fragment))
    return gates


def _polarity_of(fragment: str, gate_position: int) -> str | None:
    """The nearest polarity marker to a gate, or `None` if there is none.

    Proximity rather than grammar: "passed G1" and "G1 passed" are both common,
    and a clause carrying both polarities -- the correct summary, "G1, G2, G3 and
    G6 passed while G4 and G5 blocked" -- must attribute each gate to the marker
    beside it rather than to the sentence as a whole.
    """
    best: tuple[int, str] | None = None
    for pattern, polarity in ((_PASSED_RE, PASSED), (_BLOCKED_RE, BLOCKED)):
        for match in pattern.finditer(fragment):
            distance = min(
                abs(match.start() - gate_position), abs(match.end() - gate_position)
            )
            if best is None or distance < best[0]:
                best = (distance, polarity)
    return None if best is None else best[1]


def categorical_violations(
    text: str, context: ExplanationContext
) -> tuple[AlignmentViolation, ...]:
    """Categorical assertions in `text` that `context` contradicts.

    Empty when the text asserts nothing categorical. **Silence is not a
    violation** -- an explanation that omits gate state has a completeness
    problem, which the evaluation protocol measures separately, not an alignment
    one.
    """
    safety = context.safety or {}
    passed = {str(item).upper() for item in safety.get("conditions_passed", ())}
    blocked = {str(item).upper() for item in safety.get("blocked_by", ())}
    event = context.event or {}
    licensed_states = {
        str(event[key]).upper()
        for key in ("type", "entered_from", "closed_into")
        if event.get(key)
    }

    violations: list[AlignmentViolation] = []

    for sentence in _SENTENCE.findall(text):
        if not sentence.strip():
            continue

        # -- universal claims: "all gates passed" while any gate is blocked ----
        if blocked and _UNIVERSAL_RE.search(sentence) and _PASSED_RE.search(sentence):
            if _GATE.search(sentence) or re.search(
                r"\b(gate|gates|check|checks|condition|conditions)\b",
                sentence,
                re.I,
            ):
                violations.append(
                    AlignmentViolation(
                        kind="universal_gate_claim",
                        asserted=sentence.strip(),
                        detail=(
                            "asserts that all gates passed, but "
                            f"{', '.join(sorted(blocked))} were blocked"
                        ),
                    )
                )

        for clause in _CLAUSE.split(sentence):
            if not clause.strip():
                continue

            # -- ranges assert every gate they span ---------------------------
            ranged: set[str] = set()
            for low, high in _GATE_RANGE.findall(clause):
                polarity = _polarity_of(clause, clause.upper().find(f"G{low}"))
                spanned = _gates_in(f"G{low} to G{high}")
                ranged |= spanned
                if polarity is None:
                    continue
                expected = passed if polarity == PASSED else blocked
                wrong = sorted(spanned - expected)
                if wrong:
                    violations.append(
                        AlignmentViolation(
                            kind=f"gate_range_{polarity}",
                            asserted=f"G{low}-G{high}",
                            detail=(
                                f"the range asserts {', '.join(wrong)} as "
                                f"{polarity}, which the evidence does not record"
                            ),
                        )
                    )

            # -- per-gate polarity --------------------------------------------
            for match in _GATE.finditer(clause):
                gate = f"G{match.group(1)}"
                if gate in ranged:
                    continue  # already judged as part of its range
                polarity = _polarity_of(clause, match.start())
                if polarity is None:
                    continue
                expected = passed if polarity == PASSED else blocked
                if gate not in expected:
                    violations.append(
                        AlignmentViolation(
                            kind=f"gate_{polarity}",
                            asserted=gate,
                            detail=(
                                f"{gate} is asserted as {polarity}, but the "
                                f"evidence records passed="
                                f"{sorted(passed) or 'none'} and blocked="
                                f"{sorted(blocked) or 'none'}"
                            ),
                        )
                    )

    # -- lifecycle states ------------------------------------------------------
    if licensed_states:
        for token in {item.upper() for item in _LIFECYCLE_TOKEN.findall(text)}:
            if token not in licensed_states:
                violations.append(
                    AlignmentViolation(
                        kind="lifecycle_state",
                        asserted=token,
                        detail=(
                            f"{token} is named, but the event records only "
                            f"{', '.join(sorted(licensed_states))}"
                        ),
                    )
                )

    return tuple(dict.fromkeys(violations))
