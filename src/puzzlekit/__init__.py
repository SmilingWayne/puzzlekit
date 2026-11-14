"""Solve puzzle URLs with cspuz and export verified pzpr states."""
from importlib.metadata import PackageNotFoundError, version

from puzzlekit.api import solve, solve_url, supported_puzzles
from puzzlekit.core.result import PuzzleResult

__all__ = ['solve', 'solve_url', 'supported_puzzles', 'PuzzleResult']

try:
    __version__ = version('puzzlekit')
except PackageNotFoundError:
    __version__ = '0+unknown'
