"""Hashiwokakero islands and single/double bridges."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in {'hashi', 'hashikake', 'bridges'}:
        raise ValueError('unsupported Hashiwokakero path or variant')
    p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
    p.puzzle_type = 'hashikake'
    if p.rows < 2 or p.cols < 2:
        raise ValueError('cspuz Hashiwokakero requires at least two rows and columns')
    if len(p.cells) < 2 or any(v != '?' and not 1 <= v <= 8 for v in p.cells.values()):
        raise ValueError('cspuz Hashiwokakero requires at least two islands with clues 1–8 or ?')
    return p


def encode(p):
    tmp = Puzzle('nurikabe', p.rows, p.cols, p.cells)
    return shading.encode_shading(tmp).replace('?nurikabe/', '?hashikake/', 1)


def backend_url(url):
    return url.replace('?hashikake/', '?hashi/', 1)


def answer(p, board, status):
    vertical = [[None] * (p.cols - 1) for _ in range(p.rows)]
    horizontal = [[None] * p.cols for _ in range(p.rows - 1)]
    if status == 'no_solution':
        return vertical, horizontal
    for item in board['data']:
        if item['color'] != 'green':
            continue
        y, x, kind = item['y'], item['x'], item['item']
        if kind not in ('cross', 'line', 'doubleLine'):
            raise RuntimeError('unexpected Hashiwokakero answer')
        if y % 2 == 1 and x % 2 == 0:
            r, c, target = y // 2, x // 2 - 1, vertical
        elif y % 2 == 0 and x % 2 == 1:
            r, c, target = y // 2 - 1, x // 2, horizontal
        else:
            raise RuntimeError('invalid Hashiwokakero answer coordinate')
        if not (0 <= r < len(target) and 0 <= c < len(target[r])):
            raise RuntimeError('Hashiwokakero answer outside grid')
        target[r][c] = {'cross': -1, 'line': 1, 'doubleLine': 2}[kind]
    return vertical, horizontal


def fileio(p, ans):
    def row(values): return ' '.join(str(x) for x in values) + ' \n'
    out = [f'pzprv3\nhashikake\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        out.append(row(['.' if (r, c) not in p.cells else '-' if p.cells[r, c] == '?' else p.cells[r, c] for c in range(p.cols)]))
    for rows in ans:
        out.extend(row([v if v is not None else 0 for v in line]) for line in rows)
    return ''.join(out)
