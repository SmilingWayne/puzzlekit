"""Results from the cspuz URL solver."""

from dataclasses import dataclass
from typing import Any, Dict, Optional
import json

from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.formats.shading import compress_state, fileio
from puzzlekit.formats import extended, regions, yajilin


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
    puzzle: Optional[PuzzleInstance] = None
    normalized_url: str = ""

    def _shading_answers(self):
        if self.puzzle is None:
            raise ValueError("pzpr output is not supported for this puzzle")
        p = self.puzzle
        answers = [[None for _ in range(p.cols)] for _ in range(p.rows)]
        if self.status == "no_solution":
            return answers
        if p.puzzle_type != "hitori":
            for r, c in p.cells:
                answers[r][c] = "white"
        black_item = "fill" if p.puzzle_type in ("hitori", "kurodoko", "nurimisaki", "kurotto") else "block"
        for item in self.board["data"]:
            if item["color"] != "green":
                continue
            kind = item["item"]
            if kind != black_item and kind != "dot":
                raise RuntimeError("unexpected cspuz answer item")
            y, x = item["y"], item["x"]
            if y % 2 != 1 or x % 2 != 1:
                raise RuntimeError("unexpected cspuz answer coordinates")
            r, c = y // 2, x // 2
            if not (0 <= r < p.rows and 0 <= c < p.cols):
                raise RuntimeError("cspuz answer is outside the puzzle")
            answers[r][c] = "black" if kind == black_item else "white"
        return answers

    def to_dict(self):
        """Return a versioned semantic result; the original board remains available."""
        if self.puzzle is None:
            raise ValueError("semantic output is not supported for this puzzle")
        p = self.puzzle
        if p.puzzle_type == 'yajilin':
            answers = yajilin.answer(p, self.board, self.status)
            return {"schema_version": 1, "puzzle_type": p.puzzle_type,
                    "width": p.cols, "height": p.rows, "clues": yajilin.clues(p),
                    "status": self.status, "answers": answers,
                    "complete": self.has_solution is True and yajilin.complete(p, answers),
                    "source": self.source, "normalized_url": self.normalized_url,
                    "board": self.board}
        if p.puzzle_type in regions.TYPES:
            answers = regions.answer(p, self.board, self.status)
            _, room_grid, _ = regions.room_data(p)
            return {"schema_version": 1, "puzzle_type": p.puzzle_type,
                    "width": p.cols, "height": p.rows, "clues": regions.clues(p),
                    "regions": room_grid, "status": self.status, "answers": answers,
                    "complete": self.has_solution is True and all(v is not None for row in answers for v in row),
                    "source": self.source, "normalized_url": self.normalized_url,
                    "board": self.board}
        if p.puzzle_type in extended.TYPES:
            clues = extended.clues(p)
            answers = extended.answer(p, self.board, self.status)
            return {"schema_version": 1, "puzzle_type": p.puzzle_type,
                    "width": p.cols, "height": p.rows, "clues": clues,
                    "status": self.status, "answers": answers,
                    "complete": self.has_solution is True and extended.complete(p, answers),
                    "source": self.source, "normalized_url": self.normalized_url,
                    "board": self.board}
        clues = [[None for _ in range(p.cols)] for _ in range(p.rows)]
        for (r, c), cell in p.cells.items():
            clues[r][c] = cell.clue.value
        answers = self._shading_answers()
        return {"schema_version": 1, "puzzle_type": p.puzzle_type,
                "width": p.cols, "height": p.rows, "clues": clues,
                "status": self.status, "answers": answers,
                "complete": self.has_solution is True and all(
                    value is not None for row in answers for value in row),
                "source": self.source, "normalized_url": self.normalized_url,
                "board": self.board}

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), **kwargs)

    def to_pzpr(self):
        """Return native pzpr FileIO text; partial facts are left partial."""
        if self.status not in ("unique", "multiple"):
            raise ValueError("cannot export an answer when its existence is unknown or false")
        if self.puzzle is not None and self.puzzle.puzzle_type == 'yajilin':
            return yajilin.fileio(self.puzzle, yajilin.answer(self.puzzle, self.board, self.status))
        if self.puzzle is not None and self.puzzle.puzzle_type in regions.TYPES:
            return regions.fileio(self.puzzle, regions.answer(self.puzzle, self.board, self.status))
        if self.puzzle is not None and self.puzzle.puzzle_type in extended.TYPES:
            return extended.fileio(self.puzzle, extended.answer(self.puzzle, self.board, self.status))
        return fileio(self.puzzle, self._shading_answers())

    def to_state(self):
        """Return a raw-DEFLATE, unpadded URL-safe Base64 pzpr-trace state."""
        return compress_state(self.to_pzpr())

    def to_trace_url(self):
        return f"https://pzpr-trace.net/p?state={self.to_state()}&{self.normalized_url.split('?', 1)[1]}"

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
