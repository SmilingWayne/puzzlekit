"""Double Back room boundaries, optional holes, and cell-loop answers."""
from dataclasses import replace
from puzzlekit._adapters import extended, packed, shading
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'doubleback' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Double Back path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Double Back requires at least two rows and columns')
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:count]):
        raise ValueError('invalid room borders')
    border, consumed = BorderCodec().decode(body, h, w)
    rest = body[consumed:]
    cells = packed.decode(f'simpleloop/{w}/{h}/{rest}').cells if rest else {}
    return Puzzle('doubleback', h, w, cells, border, body=rest)


def encode(p):
    body = BorderCodec().encode(p.borders, p.rows, p.cols) + p.body
    return f'https://puzz.link/p?doubleback/{p.cols}/{p.rows}/{body}'


def answer(p, board, status):
    return extended.answer(replace(p, puzzle_type='mashu'), board, status)


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    h, w = p.rows, p.cols
    n = h * (w - 1)
    out = [f'pzprv3.2\n{p.puzzle_type}\n{h}\n{w}\n']
    out.extend(row([int(r * (w - 1) + c in p.borders) for c in range(w - 1)]) for r in range(h))
    out.extend(row([int(n + r * w + c in p.borders) for c in range(w)]) for r in range(h - 1))
    if p.puzzle_type == 'moonsun':
        out.extend(row([p.cells.get((r, c), '.') for c in range(w)]) for r in range(h))
    else:
        out.extend(row(['*' if (r, c) in p.cells else '.' for c in range(w)]) for r in range(h))
    for lines in (ans['vertical'], ans['horizontal']):
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    out.extend(row([0] * w) for _ in range(h))
    return ''.join(out)
