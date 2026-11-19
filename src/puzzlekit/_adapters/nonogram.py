"""Nonogram outside clues and shading in native pzpr FileIO."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'nonogram':
        raise ValueError('unsupported Nonogram path or variant')
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Nonogram dimensions')
    w, h = int(parts[1]), int(parts[2])
    if w < 1 or h < 1:
        raise ValueError('invalid Nonogram dimensions')
    top, left = (h + 1) // 2, (w + 1) // 2
    length = w * top + h * left
    body = parts[3]
    pos = i = 0
    values = {}
    while i < len(body):
        ch = body[i]
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
            i += 1
        else:
            if ch in '0123456789abcdef':
                n, size = int(ch, 16), 1
            elif ch == '-' and len(body[i + 1:i + 3]) == 2 and all(d in '0123456789abcdef' for d in body[i + 1:i + 3]):
                n, size = int(body[i + 1:i + 3], 16), 3
            else:
                raise ValueError('cspuz Nonogram requires numeric outside clues 1–255')
            if n == 0 or pos >= length:
                raise ValueError('cspuz Nonogram requires numeric outside clues 1–255')
            values[pos] = n
            pos += 1
            i += size
        if pos > length:
            raise ValueError('Nonogram data exceeds outside clues')
    if pos != length:
        raise ValueError('incomplete Nonogram clue data')
    return Puzzle('nonogram', h, w, values, body=body)


def encode(p):
    return f'https://puzz.link/p?nonogram/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    ans = [[None] * p.cols for _ in range(p.rows)]
    if status == 'no_solution':
        return ans
    for item in board['data']:
        if item['color'] != 'green':
            continue
        y, x, kind = item['y'], item['x'], item['item']
        if kind not in ('block', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
            raise RuntimeError('invalid Nonogram answer')
        ans[y // 2][x // 2] = '#' if kind == 'block' else '+'
    return ans


def fileio(p, ans):
    def row(items): return ' '.join(str(x) for x in items) + ' \n'
    top, left = (p.rows + 1) // 2, (p.cols + 1) // 2
    out = [f'pzprv3\nnonogram\n{p.rows}\n{p.cols}\n']
    for r in range(top - 1, -1, -1):
        out.append(row(['.'] * left + [p.cells.get(c * top + r, '.') for c in range(p.cols)]))
    start = p.cols * top
    for r in range(p.rows):
        out.append(row([p.cells.get(start + r * left + c, '.') for c in range(left - 1, -1, -1)] + [v or '.' for v in ans[r]]))
    return ''.join(out)
