"""Internal data needed to validate and export a puzzle."""
from dataclasses import dataclass, field


@dataclass
class Puzzle:
    puzzle_type: str
    rows: int
    cols: int
    cells: dict = field(default_factory=dict)
    borders: dict = field(default_factory=dict)
    display_b: bool = False
    body: str = ""
