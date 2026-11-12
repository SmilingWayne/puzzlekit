"""Nurikabe adapter for the bundled cspuz Rust solver."""

from time import perf_counter, process_time

from puzzlekit.core.grid import Grid
from puzzlekit.core.result import PuzzleResult
from puzzlekit.legacy.nurikabe import NurikabeSolver as LegacyNurikabeSolver


class NurikabeSolver(LegacyNurikabeSolver):
    def __init__(self, num_rows, num_cols, grid):
        if num_rows < 1 or num_cols < 1:
            raise ValueError("grid dimensions must be positive")
        if len(grid) != num_rows or any(len(row) != num_cols for row in grid):
            raise ValueError("grid dimensions do not match the provided clues")
        self.num_rows, self.num_cols = num_rows, num_cols
        self.grid = Grid(grid)
        self.clues = []
        for row in grid:
            clue_row = []
            for value in row:
                if value == "-":
                    clue_row.append(None)
                elif value == "?":
                    clue_row.append(-1)
                elif isinstance(value, (str, int)) and str(value).isascii() and str(value).isdigit() and 0 < int(value) <= 2147483647:
                    clue_row.append(int(value))
                else:
                    raise ValueError(f"invalid Nurikabe clue: {value!r}")
            self.clues.append(clue_row)

    def solve(self, solver_options=None):
        options = dict(solver_options or {})
        check_unique = options.pop("check_unique", False)
        if not isinstance(check_unique, bool):
            raise ValueError("check_unique must be a boolean")
        if options:
            raise ValueError(f"cspuz Nurikabe does not support solver options: {', '.join(sorted(options))}")

        from puzzlekit._cspuz import solve_nurikabe

        start = perf_counter()
        cpu_start = process_time()
        answers = solve_nurikabe(self.clues, 2 if check_unique else 1)
        elapsed = perf_counter() - start
        cpu_time = process_time() - cpu_start
        # cspuz's Rust model uses True for black. Dataset solutions use 'x'.
        solution = Grid([["x" if cell else "-" for cell in row] for row in answers[0]]) if answers else Grid.empty()
        data = {
            "status": "Feasible" if answers else "Infeasible",
            "solution_grid": solution,
            "cpu_time": cpu_time,
            "wall_time": elapsed,
            # cspuz builds and solves in one call; separate build timing is unavailable.
            "build_time": 0.0,
            "backend": "cspuz",
            "unique": (len(answers) == 1 if answers else None) if check_unique else None,
        }
        return PuzzleResult("nurikabe", {"num_rows": self.num_rows, "num_cols": self.num_cols, "grid": self.grid}, data)
