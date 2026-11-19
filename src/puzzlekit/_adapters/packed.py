"""Packed cell clues for Simple Loop and Yin-Yang."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] not in {'simpleloop', 'yinyang'}:
        raise ValueError('unsupported packed puzzle or variant')
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid puzzle dimensions')
    pid, w, h, body = parts[0], int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz requires at least two rows and columns')
    base, group = (2, 5) if pid == 'simpleloop' else (3, 3)
    if len(body) != (w * h + group - 1) // group:
        raise ValueError('invalid packed clue data length')
    digits = []
    for ch in body:
        if ch not in '0123456789abcdefghijklmnopqrstuvwxyz' or int(ch, 36) >= base ** group:
            raise ValueError('invalid packed clue data')
        n = int(ch, 36)
        digits.extend((n // base ** i) % base for i in range(group - 1, -1, -1))
    if any(digits[w * h:]):
        raise ValueError('nonempty packed clue padding')
    cells = {divmod(i, w): x for i, x in enumerate(digits[:w * h]) if x}
    if pid == 'simpleloop' and len(cells) == w * h:
        raise ValueError('cspuz Simple Loop may count an empty loop')
    return Puzzle(pid, h, w, cells, body=body)


def encode(p):
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    if p.puzzle_type == 'yinyang':
        result = [[None] * p.cols for _ in range(p.rows)]
        if status == 'no_solution':
            return result
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind not in ('circle', 'filledCircle') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Yin-Yang answer')
            if (y // 2, x // 2) not in p.cells:
                result[y // 2][x // 2] = 1 if kind == 'circle' else 2
        return result
    vertical = [[None] * (p.cols - 1) for _ in range(p.rows)]
    horizontal = [[None] * p.cols for _ in range(p.rows - 1)]
    if status == 'no_solution':
        return vertical, horizontal
    for item in board['data']:
        if item['color'] != 'green':
            continue
        y, x, kind = item['y'], item['x'], item['item']
        if kind not in ('line', 'cross'):
            raise RuntimeError('invalid Simple Loop answer')
        if y % 2 == 1 and x % 2 == 0:
            r, c, target = y // 2, x // 2 - 1, vertical
        elif y % 2 == 0 and x % 2 == 1:
            r, c, target = y // 2 - 1, x // 2, horizontal
        else:
            raise RuntimeError('invalid Simple Loop answer coordinate')
        if not (0 <= r < len(target) and 0 <= c < len(target[r])):
            raise RuntimeError('Simple Loop answer outside grid')
        target[r][c] = kind == 'line'
    return vertical, horizontal


def fileio(p, ans):
    def row(values): return ' '.join(str(x) for x in values) + ' \n'
    out = [f'pzprv3\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        out.append(row([('*' if (r, c) in p.cells else '.') if p.puzzle_type == 'simpleloop' else p.cells.get((r, c), '.') for c in range(p.cols)]))
    if p.puzzle_type == 'yinyang':
        out.extend(row([v if v is not None else '.' for v in line]) for line in ans)
    else:
        for rows in ans:
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in rows)
    return ''.join(out)
