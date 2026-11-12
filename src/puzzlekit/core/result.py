"""Results from the cspuz URL solver."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class PuzzleResult:
    """The backend's board and its status over the puzzle's answer variables.

    Board elements use the upstream cspuz solver backend's coordinate and
    rendering schema. For Nurikabe, a multiple-solution board contains facts
    common to its solutions, not an arbitrarily selected complete solution.
    """

    source: str
    status: str
    board: Dict[str, Any]

    @property
    def has_solution(self) -> Optional[bool]:
        if self.status == "no_solution":
            return False
        if self.status in ("unique", "multiple"):
            return True
        return None

    @property
    def unique(self) -> Optional[bool]:
        if self.status == "unique":
            return True
        if self.status == "multiple":
            return False
        return None

    @property
    def is_solved(self) -> bool:
        """True when the backend reports the answer variables are unique."""
        return self.status == "unique"
