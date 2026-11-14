"""Room boundary helpers."""
from typing import Any, Dict, List, Tuple

def border_to_region_grid(
    border_list: Dict[int, int],
    num_rows: int,
    num_cols: int
) -> Tuple[List[List[int]], int]:
    """Convert border dict to region grid using BFS flood fill.

    Args:
        border_list: Dict mapping border ID to 1 (present border)
        num_rows: Number of rows in the grid
        num_cols: Number of columns in the grid

    Returns:
        Tuple of (region_grid, max_region_id)
        - region_grid: 2D grid where each cell contains its region ID
        - max_region_id: Maximum region ID (total regions - 1)
    """
    num_vert = (num_cols - 1) * num_rows
    region_grid = [["x" for _ in range(num_cols)] for _ in range(num_rows)]
    current_region_id = 0

    for r in range(num_rows):
        for c in range(num_cols):
            if region_grid[r][c] == "x":
                _bfs_flood_fill(
                    r, c,
                    str(current_region_id),
                    region_grid,
                    border_list,
                    num_vert,
                    num_rows,
                    num_cols
                )
                current_region_id += 1

    return region_grid, current_region_id - 1


def _bfs_flood_fill(
    start_r: int,
    start_c: int,
    region_id: str,
    region_grid: List[List[str]],
    border_list: Dict[int, int],
    num_vert_borders: int,
    num_rows: int,
    num_cols: int
) -> None:
    """BFS flood fill to assign region ID to connected cells.

    Args:
        start_r, start_c: Starting cell coordinates
        region_id: Region ID to assign
        region_grid: Grid to fill (modified in place)
        border_list: Dict of present borders
        num_vert_borders: Count of vertical borders
        num_rows, num_cols: Grid dimensions
    """
    queue = [(start_r, start_c)]
    region_grid[start_r][start_c] = region_id

    while queue:
        r, c = queue.pop(0)

        # Check left
        if c > 0:
            border_id = r * (num_cols - 1) + (c - 1)
            if border_id not in border_list and region_grid[r][c - 1] == "x":
                region_grid[r][c - 1] = region_id
                queue.append((r, c - 1))

        # Check right
        if c < num_cols - 1:
            border_id = r * (num_cols - 1) + c
            if border_id not in border_list and region_grid[r][c + 1] == "x":
                region_grid[r][c + 1] = region_id
                queue.append((r, c + 1))

        # Check up
        if r > 0:
            border_id = num_vert_borders + (r - 1) * num_cols + c
            if border_id not in border_list and region_grid[r - 1][c] == "x":
                region_grid[r - 1][c] = region_id
                queue.append((r - 1, c))

        # Check down
        if r < num_rows - 1:
            border_id = num_vert_borders + r * num_cols + c
            if border_id not in border_list and region_grid[r + 1][c] == "x":
                region_grid[r + 1][c] = region_id
                queue.append((r + 1, c))


