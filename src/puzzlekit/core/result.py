"""Results from the cspuz URL solver."""

from dataclasses import dataclass, field
import json
from typing import Any, Optional

from puzzlekit._adapters.shading import compress_state


@dataclass(frozen=True)
class PuzzleResult:
    """Backend board and status, with optional pzpr exports for adapted puzzles."""

    source: str
    status: str
    board: dict[str, Any]
    normalized_url: str = ''
    _puzzle: Any = field(default=None, repr=False, compare=False)
    _adapter: Any = field(default=None, repr=False, compare=False)

    @property
    def board_json(self) -> str:
        """The cspuz board encoded as JSON for transport."""
        return json.dumps(self.board, ensure_ascii=False)

    def to_pzpr(self) -> str:
        """Return pzpr FileIO with confirmed answers; unknown marks stay empty."""
        if self.status not in ('unique', 'multiple'):
            raise ValueError('cannot export an answer when its existence is unknown or false')
        if self._adapter is None:
            raise ValueError('pzpr output is not supported for this puzzle')
        return self._adapter.fileio(self._puzzle, self.board, self.status)

    def to_state(self) -> str:
        """Return a compressed pzpr-trace FileIO state."""
        return compress_state(self.to_pzpr())

    def to_trace_url(self) -> str:
        return f"https://pzpr-trace.net/p?state={self.to_state()}&{self.normalized_url.split('?', 1)[1]}"

    @property
    def has_solution(self) -> Optional[bool]:
        if self.status == 'no_solution':
            return False
        if self.status in ('unique', 'multiple'):
            return True
        return None

    @property
    def unique(self) -> Optional[bool]:
        if self.status == 'unique':
            return True
        if self.status == 'multiple':
            return False
        return None

    @property
    def is_solved(self) -> bool:
        """True when the backend reports unique answer variables."""
        return self.status == 'unique'
