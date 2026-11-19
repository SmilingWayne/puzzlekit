"""Slash Pack number clues and diagonal segments."""
from puzzlekit._adapters import shading


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'slashpack':
        raise ValueError('invalid Slash Pack path')
    p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
    if min(p.rows, p.cols) < 2:
        raise ValueError('cspuz Slash Pack requires at least two rows and columns')
    if any(v == 0 or isinstance(v, int) and v >= 4096 for v in p.cells.values()):
        raise ValueError('Slash Pack clues must be positive, below 4096 or ?')
    if not any(isinstance(v, int) and v > 0 for v in p.cells.values()):
        raise ValueError('Slash Pack requires a positive clue')
    p.puzzle_type = 'slashpack'
    p.body = parts[3]
    return p


def encode(p):
    return f'https://puzz.link/p?slashpack/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        mapping = {'backslash': '1', 'slash': '2', 'dot': 'o'}
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind not in mapping or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Slash Pack answer')
            result[y // 2][x // 2] = mapping[kind]
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nslashpack\n{p.rows}\n{p.cols}\n']
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    out.extend(row([v if v is not None else '.' for v in line]) for line in answers)
    return ''.join(out)
