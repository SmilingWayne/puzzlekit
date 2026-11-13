"""Adapters for standard loop, partition, and light-bulb puzzles."""
from puzzlekit.formats.base import CellState, NumberClue, PuzzleInstance, SymbolState
from puzzlekit.formats.puzzlink.codecs import Number3Codec
from puzzlekit.formats.shading import puzzle_path

ALIASES = {'slitherlink': 'slither', 'slither': 'slither', 'masyu': 'mashu',
           'mashu': 'mashu', 'pearl': 'mashu', 'akari': 'lightup',
           'lightup': 'lightup', 'shikaku': 'shikaku'}
TYPES = frozenset(ALIASES.values())
_DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz'


def _header(source):
    parts = puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in ALIASES:
        raise ValueError('unsupported puzzle path or rule variant')
    pid = ALIASES[parts[0]]
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid puzzle dimensions')
    w, h = int(parts[1]), int(parts[2])
    if w < 1 or h < 1:
        raise ValueError('puzzle dimensions must be positive')
    if pid == 'mashu' and (w < 2 or h < 2):
        raise ValueError('cspuz Masyu requires width and height of at least 2')
    return pid, w, h, parts[3]


def decode_extended(source):
    pid, w, h, body = _header(source)
    if pid == 'shikaku':
        from puzzlekit.formats.shading import decode_shading
        return decode_shading(source)
    cells = {}
    if pid == 'mashu':
        if len(body) != (w * h + 2) // 3 or any(ch not in _DIGITS[:27] for ch in body):
            raise ValueError('invalid Masyu clue data')
        vals = Number3Codec().decode(body)
        if any(vals[w * h:]):
            raise ValueError('nonempty Masyu padding')
        for i, value in enumerate(vals[:w * h]):
            if value:
                cells[divmod(i, w)] = CellState(symbol=SymbolState(symbol_type='circle_L', symbol_index=value))
    else:
        pos = 0
        for index, ch in enumerate(body):
            if ch == '.':
                value, advance = '?', 1
            elif ch in '01234':
                value, advance = int(ch), 1
            elif ch in '56789':
                value, advance = int(ch) - 5, 2
            elif ch in 'abcde':
                value, advance = ord(ch) - ord('a'), 3
            elif 'g' <= ch <= 'z':
                value, advance = None, ord(ch) - ord('g') + 1
            else:
                raise ValueError('invalid number4 clue data')
            if value is not None:
                if pos >= w * h:
                    raise ValueError('puzzle data exceeds grid')
                cells[divmod(pos, w)] = CellState(clue=NumberClue(value=value))
            pos += advance
            if pos > w * h and index != len(body) - 1:
                raise ValueError('puzzle data exceeds grid')
    return PuzzleInstance(puzzle_type=pid, title=pid, rows=h, cols=w,
                          margins=[0, 0, 0, 0], cells=cells,
                          metadata={'source': 'puzz.link', 'original_url': source})


def clue_value(p, r, c):
    cell = p.cells.get((r, c))
    if cell is None:
        return None
    if p.puzzle_type == 'mashu':
        if cell.symbol is not None and cell.symbol.symbol_type in ('circle_L', 'circle'):
            if cell.symbol.symbol_index in (0, 1):
                return 1
            if cell.symbol.symbol_index == 2:
                return 2
        if cell.clue is not None and str(cell.clue.value) in ('1', '2'):
            return int(cell.clue.value)
        raise ValueError('invalid Masyu pearl')
    if cell.clue is None or not isinstance(cell.clue, NumberClue):
        raise ValueError('invalid clue')
    v = cell.clue.value
    if v in ('?', ' '):
        return '?'
    try:
        n = int(v)
    except (ValueError, TypeError) as exc:
        raise ValueError('invalid clue') from exc
    if n not in range(5):
        raise ValueError('number4 clue must be 0–4 or ?')
    return n


def encode_extended(p):
    if p.puzzle_type == 'shikaku':
        from puzzlekit.formats.shading import encode_shading
        return encode_shading(p)
    if p.puzzle_type not in ('slither', 'mashu', 'lightup') or p.rows < 1 or p.cols < 1:
        raise ValueError('invalid puzzle')
    if p.grid_type != 'square' or p.margins not in ([], [0, 0, 0, 0]) or p.edges:
        raise ValueError('unsupported puzzle geometry')
    if any(not (0 <= r < p.rows and 0 <= c < p.cols) for r, c in p.cells):
        raise ValueError('clue outside grid')
    values = [clue_value(p, r, c) for r in range(p.rows) for c in range(p.cols)]
    if p.puzzle_type == 'mashu':
        body = Number3Codec().encode([v or 0 for v in values])
    else:
        out, skip = [], 0
        for v in values:
            if v is None:
                skip += 1
                if skip == 20:
                    out.append('z')
                    skip = 0
            else:
                if skip:
                    out.append(chr(ord('g') + skip - 1))
                    skip = 0
                out.append('.' if v == '?' else str(v))
        if skip:
            out.append(chr(ord('g') + skip - 1))
        body = ''.join(out)
    end = '/' if body.endswith('.') else ''
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{body}{end}'


def backend_url(url):
    return url.replace('/p?mashu/', '/p?masyu/', 1).replace('/p?lightup/', '/p?akari/', 1)


def check_backend_rules(p):
    # The upstream cycle constraint also accepts an empty edge set. A positive
    # Slitherlink clue or a Masyu pearl forces a real loop; otherwise its status
    # and common facts may include a board rejected by pzpr's no-line check.
    if p.puzzle_type == 'slither' and not any(
        isinstance(cell.clue, NumberClue) and str(cell.clue.value) in ('1', '2', '3', '4')
        for cell in p.cells.values()
    ):
        raise ValueError('cspuz may count an empty Slitherlink loop; a positive clue is required')
    if p.puzzle_type == 'mashu' and not p.cells:
        raise ValueError('cspuz may count an empty Masyu loop; at least one pearl is required')


def clues(p):
    if p.puzzle_type == 'shikaku':
        return [[p.cells[(r, c)].clue.value if (r, c) in p.cells else None
                 for c in range(p.cols)] for r in range(p.rows)]
    return [[clue_value(p, r, c) for c in range(p.cols)] for r in range(p.rows)]


def answer(p, board, status):
    h, w = p.rows, p.cols
    if p.puzzle_type == 'lightup':
        a = [[None for _ in range(w)] for _ in range(h)]
        if status != 'no_solution':
            for item in board['data']:
                if item['color'] != 'green':
                    continue
                kind = item['item']
                if kind not in ('circle', 'dot'):
                    raise RuntimeError('unexpected Akari answer item')
                y, x = item['y'], item['x']
                if y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < h and 0 <= x // 2 < w):
                    raise RuntimeError('invalid Akari answer coordinate')
                a[y // 2][x // 2] = 'bulb' if kind == 'circle' else 'empty'
        return a
    outer = p.puzzle_type == 'slither'
    vertical = [[None for _ in range(w + 1 if outer else w - 1)] for _ in range(h)]
    horizontal = [[None for _ in range(w)] for _ in range(h + 1 if outer else h - 1)]
    if status != 'no_solution':
        positive = {'slither': 'wall', 'mashu': 'line', 'shikaku': 'boldWall'}[p.puzzle_type]
        for item in board['data']:
            if item['color'] != 'green':
                continue
            kind, y, x = item['item'], item['y'], item['x']
            if kind not in (positive, 'cross'):
                raise RuntimeError('unexpected border answer item')
            if y % 2 == 1 and x % 2 == 0:
                r, c = y // 2, x // 2 if outer else x // 2 - 1
                target = vertical
            elif y % 2 == 0 and x % 2 == 1:
                r, c = y // 2 if outer else y // 2 - 1, x // 2
                target = horizontal
            else:
                raise RuntimeError('invalid border answer coordinate')
            if r < 0 or c < 0 or r >= len(target) or c >= len(target[r]):
                raise RuntimeError('border answer outside puzzle')
            target[r][c] = kind == positive
    return {'vertical': vertical, 'horizontal': horizontal}


def complete(p, a):
    if p.puzzle_type == 'lightup':
        return all(a[r][c] is not None for r in range(p.rows) for c in range(p.cols)
                   if (r, c) not in p.cells)
    return all(value is not None for rows in a.values() for row in rows for value in row)


def fileio(p, a):
    def row(values):
        return ' '.join(str(x) for x in values) + ' \n'
    h, w = p.rows, p.cols
    vals = clues(p)
    header = f'pzprv3{ ".1" if p.puzzle_type == "slither" else ""}\n{p.puzzle_type}\n{h}\n{w}\n'
    clue_lines = []
    for r in range(h):
        out = []
        for c in range(w):
            v = vals[r][c]
            if p.puzzle_type == 'lightup' and v is None:
                v = '#' if a[r][c] == 'bulb' else '+' if a[r][c] == 'empty' else '.'
            elif v is None:
                v = '.'
            elif v == '?':
                v = '-'
            out.append(v)
        clue_lines.append(row(out))
    if p.puzzle_type == 'lightup':
        return header + ''.join(clue_lines)
    if p.puzzle_type == 'slither':
        clue_lines.extend(row(['0'] * w) for _ in range(h))
    for rows in (a['vertical'], a['horizontal']):
        for line in rows:
            clue_lines.append(row(['1' if v is True else '-1' if v is False else '0' for v in line]))
    return header + ''.join(clue_lines)
