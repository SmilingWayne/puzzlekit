"""Herugolf ponds, balls, holes, and paths."""
from puzzlekit._adapters import packed, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'herugolf' or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid Herugolf path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Herugolf requires at least two rows and columns')
    body = parts[3]
    count = (w * h + 4) // 5
    bits = body[:count]
    if len(bits) != count or any(c not in '0123456789abcdefghijklmnopqrstuv' for c in bits):
        raise ValueError('invalid pond data')
    pond = [bool(int(c, 32) & (1 << (4 - j))) for c in bits for j in range(5)]
    if any(pond[h * w:]):
        raise ValueError('pond data exceeds grid')
    cells, pos, i = {}, 0, count
    while i < len(body):
        ch = body[i]
        if 'i' <= ch <= 'z':
            pos += ord(ch) - ord('i') + 1
            i += 1
            continue
        if pos >= h * w:
            raise ValueError('clues exceed grid')
        if ch == 'h':
            value = 'H'
            i += 1
        elif ch in '123456789abcdef':
            value = int(ch, 16)
            i += 1
        elif ch == '-' and i + 2 < len(body) and all(c in '0123456789abcdef' for c in body[i + 1:i + 3]):
            value = int(body[i + 1:i + 3], 16)
            i += 3
            if value == 0:
                raise ValueError('ball number must be positive')
        else:
            raise ValueError('invalid Herugolf clue')
        cells[divmod(pos, w)] = value
        pos += 1
    if pos > h * w or any(pond[r * w + c] for r, c in cells):
        raise ValueError('invalid Herugolf pond or clue data')
    if not any(isinstance(v, int) for v in cells.values()):
        raise ValueError('Herugolf requires a numbered ball')
    return Puzzle('herugolf', h, w, cells=cells, body=body,
                  holes={divmod(i, w): True for i, v in enumerate(pond[:h * w]) if v})


def encode(p):
    return f'https://puzz.link/p?herugolf/{p.cols}/{p.rows}/{p.body}'


answer = packed.answer


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nherugolf\n{p.rows}\n{p.cols}\n']
    out.extend(row(['i' if (r, c) in p.holes else p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    for lines in ans:
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    return ''.join(out)
