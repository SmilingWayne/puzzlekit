"""The Longest outer-border clues and partition marks."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'longest' or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid The Longest path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('The Longest requires at least two rows and columns')
    body = parts[3]
    if any(c not in '0123456789abcdefghijklmnopqrstuv' for c in body):
        raise ValueError('invalid border clues')
    inner = h * (w - 1) + (h - 1) * w
    total = inner + 2 * h + 2 * w
    if len(body) * 5 < inner or len(body) > (total + 4) // 5:
        raise ValueError('invalid border clue length')
    bits = [bool(int(c, 32) & (1 << (4 - i))) for c in body for i in range(5)]
    if any(bits[total:]):
        raise ValueError('border clues exceed grid')
    bits += [False] * (total - len(bits))
    coords = ([(2*r+1, 2*c) for r in range(h) for c in range(1, w)] +
              [(2*r, 2*c+1) for r in range(1, h) for c in range(w)] +
              [(0, 2*c+1) for c in range(w)] + [(2*h, 2*c+1) for c in range(w)] +
              [(2*r+1, 0) for r in range(h)] + [(2*r+1, 2*w) for r in range(h)])
    return Puzzle('longest', h, w, borders={pos: True for pos, bit in zip(coords, bits) if bit}, body=body)


def encode(p):
    return f'https://puzz.link/p?longest/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    return {(item['y'], item['x']): 2 if item['item'] == 'wall' else -1
            for item in board['data'] if item['color'] == 'green'}


def fileio(p, marks):
    def row(values): return ' '.join(map(str, values)) + ' \n'
    def value(y, x): return 1 if (y, x) in p.borders else marks.get((y, x), 0)
    out = [f'pzprv3\nlongest\n{p.rows}\n{p.cols}\n']
    out.extend(row([value(2*r+1, 2*c) for c in range(p.cols+1)]) for r in range(p.rows))
    out.extend(row([value(2*r, 2*c+1) for c in range(p.cols)]) for r in range(p.rows+1))
    return ''.join(out)
