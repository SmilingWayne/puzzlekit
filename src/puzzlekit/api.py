"""Public URL-solving entry points."""
import json
import re

from puzzlekit._adapters.shading import puzzle_path
from puzzlekit.core.result import PuzzleResult
from puzzlekit.registry import BY_TOKEN


def solve(source: str, puzzle_type=None, solver_options=None, **kwargs) -> PuzzleResult:
    """Solve a supported URL with cspuz and return its board and status."""
    if puzzle_type is not None or solver_options is not None or kwargs:
        raise ValueError('v0.4 solves puzzle URLs; dataset text and legacy solver options are not accepted')
    if not isinstance(source, str) or not source.strip():
        raise ValueError('source must be a non-empty puzzle URL')
    from puzzlekit._cspuz import solve_url as solve_backend

    source = source.strip()
    try:
        path = puzzle_path(source)
    except ValueError:
        tokens = '|'.join(re.escape(token) for token in sorted(BY_TOKEN))
        if re.search(r'(?:^|[?&](?:p=)?)(?:' + tokens + r')/', source):
            raise
        path = ''
    adapter = BY_TOKEN.get(path.split('/', 1)[0])
    puzzle, normalized, backend_input = adapter.parse(source) if adapter else (None, source, source)
    board_json, status = solve_backend(backend_input)
    try:
        board = json.loads(board_json)
    except (TypeError, ValueError) as exc:
        raise RuntimeError('cspuz returned an invalid board representation') from exc
    return PuzzleResult(source=source, status=status, board=board, normalized_url=normalized,
                        _puzzle=puzzle, _adapter=adapter)


def solve_url(source: str) -> PuzzleResult:
    """Alias for solve."""
    return solve(source)


def supported_puzzles() -> list[tuple[str, str]]:
    """List upstream puzzle names; this does not guarantee FileIO support."""
    from puzzlekit._cspuz import supported_puzzles as list_backend
    return list_backend()
