"""Native Tapa clue lists and cell shading."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'tapa':
        raise ValueError('unsupported Tapa path or variant')
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Tapa dimensions')
    w, h = int(parts[1]), int(parts[2])
    if w < 2 or h < 2:
        raise ValueError('cspuz Tapa requires at least two rows and columns')
    body = parts[3]
    cells, pos, i = {}, 0, 0
    while i < len(body):
        c = body[i]
        if 'g' <= c <= 'z':
            pos += ord(c) - ord('g') + 1
            i += 1
            if pos > w * h:
                raise ValueError('Tapa data exceeds grid')
            continue
        if pos >= w * h:
            raise ValueError('Tapa data exceeds grid')
        if c == '.':
            values = ('?',)
        elif c in '012345678':
            values = (int(c),)
        elif c == '9':
            values = (1, 1, 1, 1)
        elif 'a' <= c <= 'd' and i + 1 < len(body) and body[i + 1] in '0123456789abcdefghijklmnopqrstuvwxyz':
            v = int(body[i:i + 2], 36)
            if 360 <= v < 396:
                v -= 360; values = (v // 6, v % 6)
            elif 396 <= v < 460:
                v -= 396; values = (v // 16, v // 4 % 4, v % 4)
            elif 460 <= v < 476:
                v -= 460; values = (v // 8, v // 4 % 2, v // 2 % 2, v % 2)
            else:
                raise ValueError('invalid Tapa clue')
            values = tuple(x if x else '?' for x in values)
            i += 1
        else:
            raise ValueError('invalid Tapa clue')
        cells[divmod(pos, w)] = values
        pos += 1
        i += 1
    if not any(values != (0,) for values in cells.values()):
        raise ValueError('cspuz Tapa requires a clue that forces shaded cells')
    return Puzzle('tapa', h, w, cells, body=body)


def encode(p):
    return f'https://puzz.link/p?tapa/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    ans = [[None] * p.cols for _ in range(p.rows)]
    if status == 'no_solution':
        return ans
    for item in board['data']:
        if item['color'] != 'green':
            continue
        y, x, kind = item['y'], item['x'], item['item']
        if kind not in ('block', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
            raise RuntimeError('invalid Tapa answer')
        ans[y // 2][x // 2] = '#' if kind == 'block' else '+'
    return ans


def fileio(p, ans):
    out = [f'pzprv3\ntapa\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        row = []
        for c in range(p.cols):
            clue = p.cells.get((r, c))
            row.append(','.join('-' if x == '?' else str(x) for x in clue) if clue is not None else ans[r][c] or '.')
        out.append(' '.join(row) + ' \n')
    return ''.join(out)
