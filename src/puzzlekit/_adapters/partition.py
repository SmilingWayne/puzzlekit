"""Number-clued partitions with pzpr answer borders."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle

TYPES = {'araf', 'squarejam', 'fillomino', 'sudoku'}


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in TYPES:
        raise ValueError('unsupported partition puzzle or variant')
    pid = parts[0]
    p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
    p.puzzle_type = pid
    if p.rows < 2 or p.cols < 2:
        raise ValueError('cspuz partition puzzles require at least two rows and columns')
    if any((v == '?' and pid != 'squarejam') or
           (v != '?' and (v == 0 or v >= 4096)) for v in p.cells.values()):
        raise ValueError('cspuz partition adapter cannot represent this clue')
    if pid == 'sudoku' and (p.rows != p.cols or p.rows not in {4, 6, 9, 16, 25} or any(v > p.rows for v in p.cells.values())):
        raise ValueError('cspuz Sudoku requires a supported square size and clues within that size')
    return p


def encode(p):
    tmp = Puzzle('nurikabe', p.rows, p.cols, p.cells)
    return shading.encode_shading(tmp).replace('?nurikabe/', '?' + p.puzzle_type + '/', 1)


def answer(p, board, status):
    vertical = [[None] * (p.cols - 1) for _ in range(p.rows)]
    horizontal = [[None] * p.cols for _ in range(p.rows - 1)]
    numbers = [[None] * p.cols for _ in range(p.rows)]
    if status == 'no_solution':
        return vertical, horizontal, numbers
    for item in board['data']:
        if item['color'] != 'green':
            continue
        y, x, kind = item['y'], item['x'], item['item']
        if isinstance(kind, dict) and p.puzzle_type == 'sudoku' and kind.get('kind') == 'sudokuCandidateSet':
            continue
        if isinstance(kind, dict) and kind.get('kind') == 'text' and p.puzzle_type in {'fillomino', 'sudoku'}:
            if y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid answer number coordinate')
            try:
                value = int(kind['data'])
            except (KeyError, ValueError, TypeError) as exc:
                raise RuntimeError('invalid answer number') from exc
            if value < 1 or (y // 2, x // 2) in p.cells:
                raise RuntimeError('invalid answer number')
            numbers[y // 2][x // 2] = value
            continue
        if kind not in ('boldWall', 'cross'):
            raise RuntimeError('unexpected partition answer')
        if y % 2 == 1 and x % 2 == 0:
            r, c, target = y // 2, x // 2 - 1, vertical
        elif y % 2 == 0 and x % 2 == 1:
            r, c, target = y // 2 - 1, x // 2, horizontal
        else:
            raise RuntimeError('invalid partition answer coordinate')
        if not (0 <= r < len(target) and 0 <= c < len(target[r])):
            raise RuntimeError('partition answer outside grid')
        target[r][c] = kind == 'boldWall'
    return vertical, horizontal, numbers


def fileio(p, ans):
    def row(values):
        return ' '.join(str(x) for x in values) + ' \n'
    vertical, horizontal, numbers = ans
    dimensions = f'{p.rows}\n' if p.puzzle_type == 'sudoku' else f'{p.rows}\n{p.cols}\n'
    out = [f'pzprv3\n{p.puzzle_type}\n{dimensions}']
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.')
                    for c in range(p.cols)]) for r in range(p.rows))
    if p.puzzle_type in {'fillomino', 'sudoku'}:
        out.extend(row([v if v is not None else '.' for v in line]) for line in numbers)
    if p.puzzle_type != 'sudoku':
        for rows in (vertical, horizontal):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in rows)
    return ''.join(out)
