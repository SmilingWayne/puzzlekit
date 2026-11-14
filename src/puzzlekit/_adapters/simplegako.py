"""Simple Gako number clues and answers."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'simplegako' or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid Simple Gako path')
    w, h = map(int, parts[1:3])
    if w < 2 or h < 2:
        raise ValueError('cspuz requires at least two rows and columns')
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{parts[3]}').cells
    if any(v == '?' or v == 0 or v >= 4096 for v in cells.values()):
        raise ValueError('cspuz Simple Gako requires positive numeric clues below 4096')
    return Puzzle('simplegako', h, w, cells, body=parts[3])


def encode(p):
    return f'https://puzz.link/p?simplegako/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if not isinstance(kind, dict) or kind.get('kind') != 'text' or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('unexpected Simple Gako answer')
            result[y // 2][x // 2] = kind['data']
    return result


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nsimplegako\n{p.rows}\n{p.cols}\n']
    out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    out.extend(row([v if v is not None else '.' for v in line]) for line in ans)
    return ''.join(out)
