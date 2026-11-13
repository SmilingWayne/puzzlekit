"""Standard Yajilin: arrow clues, shaded cells and loop edges."""
from puzzlekit.formats.base import ArrowClue, CellState, Direction, NumberClue, PuzzleInstance
from puzzlekit.formats.shading import puzzle_path

ALIASES = {'yajilin', 'yajirin'}
_DIR = {1: Direction.N, 2: Direction.S, 3: Direction.W, 4: Direction.E}
_REV = {v: k for k, v in _DIR.items()}
_HEX = '0123456789abcdef'


def decode(source):
    parts = puzzle_path(source).split('/')
    if len(parts) > 4 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    flag = len(parts) == 5 and parts[1] == 'b'
    if flag:
        parts.pop(1)
    if len(parts) != 4 or parts[0] not in ALIASES:
        raise ValueError('unsupported Yajilin rule flag or puzzle path')
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid dimensions')
    w, h = int(parts[1]), int(parts[2])
    if w < 2 or h < 2:
        raise ValueError('cspuz Yajilin requires at least two rows and columns')
    body, cells, i, pos = parts[3], {}, 0, 0
    while i < len(body):
        ch = body[i]
        if 'a' <= ch <= 'z':
            pos += ord(ch) - ord('a') + 1
            i += 1
            if pos > w * h and i < len(body):
                raise ValueError('clue data exceeds grid')
            continue
        if pos >= w * h:
            raise ValueError('clue data exceeds grid')
        long = ch == '-'
        if long:
            i += 1
            if i >= len(body): raise ValueError('invalid arrow clue')
            ch = body[i]
        if ch not in '0123456789':
            raise ValueError('invalid arrow clue')
        if long and ch not in '01234':
            raise ValueError('invalid long arrow direction')
        direction = int(ch) % 5
        length = (3 if long else 1) + int(ch) // 5
        digits = body[i + 1:i + 1 + length]
        if digits == '.' and length == 1:
            value = '?'
        elif len(digits) == length and all(v in _HEX for v in digits):
            value = int(digits, 16)
        else:
            raise ValueError('invalid arrow clue')
        clue = ArrowClue(value=value, direction=_DIR[direction]) if direction else NumberClue(value=value)
        cells[divmod(pos, w)] = CellState(clue=clue)
        pos += 1
        i += length + 1
    return PuzzleInstance(puzzle_type='yajilin', title='yajilin', rows=h, cols=w,
                          margins=[0, 0, 0, 0], cells=cells,
                          metadata={'source': 'puzz.link', 'original_url': source, 'display_b': flag})


def _clue(cell):
    clue = cell.clue
    if isinstance(clue, ArrowClue):
        if clue.direction not in _REV: raise ValueError('unsupported arrow direction')
        direction, value = _REV[clue.direction], clue.value
    elif isinstance(clue, NumberClue):
        direction, value = 0, clue.value
    else:
        raise ValueError('invalid arrow clue')
    if value in ('?', ' ', None): return direction, '?'
    try: value = int(value)
    except (TypeError, ValueError) as exc: raise ValueError('invalid arrow number') from exc
    if not 0 <= value < 4096: raise ValueError('Yajilin arrow number is outside the pzpr URL range')
    return direction, value


def encode(p):
    if p.puzzle_type != 'yajilin' or p.rows < 2 or p.cols < 2 or p.grid_type != 'square' or p.edges:
        raise ValueError('invalid Yajilin puzzle')
    if p.margins not in ([], [0, 0, 0, 0]): raise ValueError('invalid margins')
    if any(not (0 <= r < p.rows and 0 <= c < p.cols) for r, c in p.cells):
        raise ValueError('clue outside grid')
    out, skip = [], 0
    for r in range(p.rows):
        for c in range(p.cols):
            cell = p.cells.get((r, c))
            if cell is None:
                skip += 1
                if skip == 26: out.append('z'); skip = 0
                continue
            if skip: out.append(chr(ord('a') + skip - 1)); skip = 0
            direction, value = _clue(cell)
            if value == '?': out.append(str(direction) + '.')
            elif value < 16: out.append(str(direction) + format(value, 'x'))
            elif value < 256: out.append(str(direction + 5) + format(value, '02x'))
            else: out.append('-' + str(direction) + format(value, '03x'))
    if skip: out.append(chr(ord('a') + skip - 1))
    body = ''.join(out)
    flag = 'b/' if p.metadata.get('display_b') else ''
    end = '/' if body.endswith('.') else ''
    return f'https://puzz.link/p?yajilin/{flag}{p.cols}/{p.rows}/{body}{end}'


def clues(p):
    out = [[None] * p.cols for _ in range(p.rows)]
    for (r, c), cell in p.cells.items():
        direction, value = _clue(cell)
        out[r][c] = {'direction': direction, 'value': value}
    return out


def check_backend_rules(p):
    if any(value != '?' and value >= 256 for _, value in map(_clue, p.cells.values())):
        raise ValueError('cspuz Yajilin supports arrow numbers 0–255')
    # With no loop, every non-clue cell must be black. Adjacent non-clue
    # cells cannot both be black, which rules out that spurious assignment.
    has_adjacent = any(
        (r, c) not in p.cells and
        ((c + 1 < p.cols and (r, c + 1) not in p.cells) or
         (r + 1 < p.rows and (r + 1, c) not in p.cells))
        for r in range(p.rows) for c in range(p.cols)
    )
    if not has_adjacent:
        raise ValueError('cspuz may count an empty Yajilin loop for this clue layout')


def answer(p, board, status):
    h, w = p.rows, p.cols
    cells = [[None] * w for _ in range(h)]
    vertical = [[None] * (w - 1) for _ in range(h)]
    horizontal = [[None] * w for _ in range(h - 1)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green': continue
            kind, y, x = item['item'], item['y'], item['x']
            if y % 2 and x % 2 and kind in ('block', 'dot'):
                r, c = y // 2, x // 2
                if not (0 <= r < h and 0 <= c < w): raise RuntimeError('invalid answer coordinate')
                cells[r][c] = 'black' if kind == 'block' else 'white'
            elif y % 2 and x % 2 == 0 and kind in ('line', 'cross'):
                r, c = y // 2, x // 2 - 1
                if not (0 <= r < h and 0 <= c < w - 1): raise RuntimeError('invalid edge coordinate')
                vertical[r][c] = kind == 'line'
            elif y % 2 == 0 and x % 2 and kind in ('line', 'cross'):
                r, c = y // 2 - 1, x // 2
                if not (0 <= r < h - 1 and 0 <= c < w): raise RuntimeError('invalid edge coordinate')
                horizontal[r][c] = kind == 'line'
            else: raise RuntimeError('unexpected Yajilin answer item')
        # The backend suppresses line facts touching clues or certain black cells.
        # Such edges are forced absent by the rules; derive them explicitly.
        blocked = lambda r, c: (r, c) in p.cells or cells[r][c] == 'black'
        for r in range(h):
            for c in range(w - 1):
                if blocked(r, c) or blocked(r, c + 1): vertical[r][c] = False
        for r in range(h - 1):
            for c in range(w):
                if blocked(r, c) or blocked(r + 1, c): horizontal[r][c] = False
    return {'cells': cells, 'vertical': vertical, 'horizontal': horizontal}


def complete(p, a):
    return all(a['cells'][r][c] is not None for r in range(p.rows) for c in range(p.cols) if (r, c) not in p.cells) and all(v is not None for key in ('vertical', 'horizontal') for row in a[key] for v in row)


def fileio(p, a):
    def row(vals): return ' '.join(str(v) for v in vals) + ' \n'
    h, w = p.rows, p.cols
    out = [f'pzprv3\nyajilin\n{h}\n{w}\n']
    for r in range(h):
        line = []
        for c in range(w):
            cell = p.cells.get((r, c))
            if cell is None: line.append('.')
            else:
                d, v = _clue(cell)
                line.append(f'{d},{"-" if v == "?" else v}')
        out.append(row(line))
    for line in a['cells']:
        out.append(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]))
    for key in ('vertical', 'horizontal'):
        for line in a[key]:
            out.append(row(['1' if v is True else '-1' if v is False else '0' for v in line]))
    return ''.join(out)
