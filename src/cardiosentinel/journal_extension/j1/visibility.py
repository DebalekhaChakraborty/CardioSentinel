"""The scientific-visibility latch, implementing frozen protocol section 11.

A failure before any scientific quantity has been seen is an infrastructure
failure. A failure after is not, because the analyst now knows something, and
treating it as a free retry is how a study quietly acquires extra attempts.

The latch is monotonic. It starts FALSE, is raised exactly once before the first
real scientific quantity is materialized, and has no path back. There is no
reset, no context manager that restores it, and no flag that lowers it.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class VisibilityError(RuntimeError):
    """An attempt to lower the latch, or to see science before raising it."""


@dataclass
class ScientificVisibility:
    """Monotonic FALSE -> TRUE. Never TRUE -> FALSE."""

    _visible: bool = field(default=False, init=False)
    _reason: str | None = field(default=None, init=False)

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def reason(self) -> str | None:
        """What first made science visible. `None` while still FALSE."""
        return self._reason

    def mark_visible(self, reason: str) -> None:
        """Raise the latch before the first scientific quantity is materialized.

        Idempotent: raising an already-raised latch keeps the original reason,
        because the first thing seen is what determines the failure class.
        """
        if not reason.strip():
            raise VisibilityError("a visibility transition must name its cause.")
        if self._visible:
            return
        self._visible = True
        self._reason = reason

    def require_not_visible(self, action: str) -> None:
        """Guard an operation that must happen before any science is seen."""
        if self._visible:
            raise VisibilityError(
                f"{action} must occur before scientific visibility. The latch "
                f"was already raised by: {self._reason}."
            )

    def failure_classification(self) -> str:
        """The class a failure would carry right now.

        Neither class is an automatic retry. `INFRASTRUCTURE` may be retried
        only if a later authorization permits it; `APPARATUS_AFTER_VISIBILITY`
        requires named human review because the analyst has seen something.
        """
        return "APPARATUS_AFTER_VISIBILITY" if self._visible else "INFRASTRUCTURE"
