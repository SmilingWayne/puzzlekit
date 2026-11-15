"""Bosanowa playable cells, number clues, and answers."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'bosanowa' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid Bosanowa path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Bosanowa requires at least two rows and columns')
    body = parts[3]
    count = (h * w + 4) // 5
    bits = body[:count]
    if len(bits) != count or any(c not in '0123456789abcdefghijklmnopqrstuv' for c in bits):
        raise ValueError('invalid Bosanowa board')
    blocked = [bool(int(c, 32) & (1 << (4 - j))) for c in bits for j in range(5)]
    if any(blocked[h * w:]):
        raise ValueError('Bosanowa board exceeds grid')
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body[count:]}').cells
    if not cells or any(v == '?' or v == 0 or v >= 4096 for v in cells.values()):
        raise ValueError('Bosanowa requires positive clues below 4096')
    if any(blocked[r * w + c] for r, c in cells):
        raise ValueError('Bosanowa clues must be on playable cells')
    return Puzzle('bosanowa', h, w, cells=cells, body=body,
                  holes={divmod(i, w): True for i, v in enumerate(blocked[:h * w]) if v})


def encode(p):
    return f'https://puzz.link/p?bosanowa/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Bosanowa answer coordinate')
            if not isinstance(kind, dict) or kind.get('kind') != 'text' or not kind.get('data', '').isdigit():
                raise RuntimeError('invalid Bosanowa answer')
            result[y // 2][x // 2] = kind['data']
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    h, w = p.rows, p.cols
    out = [f'pzprv3\nbosanowa\n{h}\n{w}\n']
    out.extend(row(['.' if (r, c) in p.holes else p.cells.get((r, c), '0') for c in range(w)]) for r in range(h))
    out.extend(row(['.' if (r, c) in p.holes or (r, c) in p.cells else answers[r][c] or '0' for c in range(w)]) for r in range(h))
    out.extend(row(['.'] * (w - 1)) for _ in range(h))
    out.extend(row(['.'] * w) for _ in range(h - 1))
    return ''.join(out)
