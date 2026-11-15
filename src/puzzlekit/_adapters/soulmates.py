"""Soul Mates number clues and answer numbers."""
from puzzlekit._adapters import shading


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'soulmates':
        raise ValueError('invalid Soul Mates path')
    p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
    if min(p.rows, p.cols) < 2:
        raise ValueError('cspuz Soul Mates requires at least two rows and columns')
    if any(v == '?' or v == 0 or v >= 4096 for v in p.cells.values()):
        raise ValueError('cspuz Soul Mates requires positive number clues below 4096')
    p.puzzle_type = 'soulmates'
    p.body = parts[3]
    return p


def encode(p):
    return f'https://puzz.link/p?soulmates/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Soul Mates answer coordinate')
            if kind == 'dot':
                value = '-'
            elif isinstance(kind, dict) and kind.get('kind') == 'text' and kind.get('data', '').isdigit():
                value = kind['data']
            else:
                raise RuntimeError('invalid Soul Mates answer')
            result[y // 2][x // 2] = value
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nsoulmates\n{p.rows}\n{p.cols}\n']
    out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    out.extend(row([v if v is not None else '.' for v in line]) for line in answers)
    return ''.join(out)
