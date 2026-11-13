"""Standard room-shading puzzle adapters."""
from puzzlekit.formats.base import CellState, EdgeState, NumberClue, PuzzleInstance
from puzzlekit.formats.puzzlink.codecs import BorderCodec
from puzzlekit.formats.puzzlink.utils import border_to_region_grid, region_grid_to_borders
from puzzlekit.formats.shading import decode_shading, encode_shading, puzzle_path

TYPES = frozenset({'heyawake', 'aqre', 'lits', 'norinori'})
NUMBERED = frozenset({'heyawake', 'aqre'})


def _parts(source):
    parts = puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in TYPES:
        raise ValueError('unsupported room puzzle path or variant')
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid dimensions')
    w, h = int(parts[1]), int(parts[2])
    # cspuz room backends index horizontal[0], so single-row boards panic.
    if w < 2 or h < 2:
        raise ValueError('cspuz room puzzles require at least two rows and columns')
    return parts[0], w, h, parts[3]


def _edges(borders, h, w):
    out = {}
    n = h * (w - 1)
    for i in borders:
        if i < n:
            r, c = divmod(i, w - 1)
            key = ((r, c + 1), (r + 1, c + 1))
        else:
            r, c = divmod(i - n, w)
            key = ((r + 1, c), (r + 1, c + 1))
        out[key] = EdgeState(connected=True, edge_type=2)
    return out


def _anchors(grid):
    result = {}
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            rid = int(value)
            if rid not in result or (c, r) < (result[rid][1], result[rid][0]):
                result[rid] = (r, c)
    return result


def decode_regions(source):
    pid, w, h, body = _parts(source)
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:count]):
        raise ValueError('invalid room borders')
    border, consumed = BorderCodec().decode(body, h, w)
    grid, max_id = border_to_region_grid(border, h, w)
    anchors = _anchors(grid)
    clues = {}
    rest = body[consumed:]
    if pid in NUMBERED:
        tmp = decode_shading(f'nurikabe/{max_id + 1}/1/{rest}')
        for (_, i), cell in tmp.cells.items():
            clues[anchors[i]] = cell
    elif rest:
        raise ValueError('unexpected room puzzle data')
    return PuzzleInstance(puzzle_type=pid, title=pid, rows=h, cols=w,
                          margins=[0, 0, 0, 0], cells=clues,
                          edges=_edges(border, h, w),
                          metadata={'source': 'puzz.link', 'original_url': source})


def room_data(p):
    if p.puzzle_type not in TYPES or p.rows < 2 or p.cols < 2 or p.grid_type != 'square':
        raise ValueError('invalid room puzzle')
    if p.margins not in ([], [0, 0, 0, 0]):
        raise ValueError('unsupported margins')
    border = region_grid_to_borders(p.edges, p.rows, p.cols)
    if len(border) != len(p.edges):
        raise ValueError('invalid room borders')
    grid, max_id = border_to_region_grid(border, p.rows, p.cols)
    anchors = _anchors(grid)
    if p.puzzle_type not in NUMBERED and p.cells:
        raise ValueError('this puzzle has no room clues')
    if any(pos not in anchors.values() for pos in p.cells):
        raise ValueError('room clue must be at its first cell')
    values = []
    for i in range(max_id + 1):
        cell = p.cells.get(anchors[i])
        if cell is None:
            values.append(None)
        elif not isinstance(cell.clue, NumberClue):
            raise ValueError('invalid room clue')
        else:
            v = cell.clue.value
            if v in ('?', ' '):
                v = '?'
            else:
                try: v = int(v)
                except (ValueError, TypeError) as exc: raise ValueError('invalid room clue') from exc
                if not 0 <= v <= 1126351:
                    raise ValueError('room clue is outside the pzpr URL range')
            values.append(v)
    return border, grid, values


def check_backend_clues(p):
    _, _, values = room_data(p)
    if any(isinstance(v, int) and v >= 4096 for v in values):
        raise ValueError('cspuz room clues must be 0–4095 or ?')


def encode_regions(p):
    border, grid, values = room_data(p)
    body = BorderCodec().encode(border, p.rows, p.cols)
    if p.puzzle_type in NUMBERED:
        cells = {(0, i): CellState(clue=NumberClue(value=v)) for i, v in enumerate(values) if v is not None}
        tmp = PuzzleInstance(puzzle_type='nurikabe', rows=1, cols=len(values), margins=[0, 0, 0, 0], cells=cells)
        body += encode_shading(tmp).split('?', 1)[1].split('/', 3)[3]
    end = '/' if body.endswith('.') else ''
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{body}{end}'


def clues(p):
    return [[p.cells[(r, c)].clue.value if (r, c) in p.cells else None
             for c in range(p.cols)] for r in range(p.rows)]


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status == 'no_solution':
        return result
    for item in board['data']:
        if item['color'] != 'green':
            continue
        kind, y, x = item['item'], item['y'], item['x']
        if kind not in ('block', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
            raise RuntimeError('unexpected room shading answer')
        result[y // 2][x // 2] = 'black' if kind == 'block' else 'white'
    return result


def fileio(p, answer_grid):
    def row(values): return ' '.join(str(x) for x in values) + ' \n'
    border, _, _ = room_data(p)
    h, w = p.rows, p.cols
    n = h * (w - 1)
    out = [f'pzprv3.1\n{p.puzzle_type}\n{h}\n{w}\n']
    out.extend(row([int(r * (w - 1) + c in border) for c in range(w - 1)]) for r in range(h))
    out.extend(row([int(n + r * w + c in border) for c in range(w)]) for r in range(h - 1))
    if p.puzzle_type in NUMBERED:
        for line in clues(p):
            out.append(row(['.' if x is None else '-' if x in ('?', ' ') else x for x in line]))
    for line in answer_grid:
        out.append(row(['#' if x == 'black' else '+' if x == 'white' else '.' for x in line]))
    return ''.join(out)
