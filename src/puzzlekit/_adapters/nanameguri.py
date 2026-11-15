"""Nanameguri room boundaries, diagonal clues, and loop."""
from puzzlekit._adapters import packed, shading
from puzzlekit._adapters.codecs import BorderCodec, Number3Codec
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'nanameguri' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid Nanameguri path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Nanameguri requires at least two rows and columns')
    body = parts[3]
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(c not in '0123456789abcdefghijklmnopqrstuv' for c in body[:count]):
        raise ValueError('invalid Nanameguri room borders')
    borders, consumed = BorderCodec().decode(body, h, w)
    clues = body[consumed:]
    if len(clues) != (h * w + 2) // 3 or any(c not in '0123456789abcdefghijklmnopq' for c in clues):
        raise ValueError('invalid Nanameguri diagonal clues')
    values = Number3Codec().decode(clues)
    if any(values[h*w:]):
        raise ValueError('diagonal clues exceed grid')
    cells = {divmod(i, w): v for i, v in enumerate(values[:h*w]) if v}
    if not cells:
        raise ValueError('a diagonal clue is required to exclude an empty loop')
    return Puzzle('nanameguri', h, w, cells=cells, borders=borders, body=body)


def encode(p):
    return f'https://puzz.link/p?nanameguri/{p.cols}/{p.rows}/{p.body}'


answer = packed.answer


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    h, w = p.rows, p.cols
    out = [f'pzprv3\nnanameguri\n{h}\n{w}\n']
    n = h * (w - 1)
    out.extend(row([0] + [int(r * (w - 1) + c in p.borders) for c in range(w - 1)] + [0]) for r in range(h))
    out.append(row([0] * w))
    out.extend(row([int(n + r * w + c in p.borders) for c in range(w)]) for r in range(h - 1))
    out.append(row([0] * w))
    out.extend(row([p.cells.get((r,c), '.') for c in range(w)]) for r in range(h))
    out.extend(row([0] + [1 if v is True else -1 if v is False else 0 for v in line] + [0]) for line in ans[0])
    out.append(row([0] * w))
    out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in ans[1])
    out.append(row([0] * w))
    return ''.join(out)
