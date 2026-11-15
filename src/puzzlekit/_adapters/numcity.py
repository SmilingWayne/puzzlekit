"""Number City clues, rooms and answer numbers."""
from puzzlekit._adapters import shading, roomnumbers
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'numcity' or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid Number City path or rule variant')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('Number City requires at least two rows and columns')
    body = parts[3]
    i = pos = 0
    while i < len(body) and pos < h*w:
        ch = body[i]
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
            i += 1
        else:
            i += 3 if ch == '-' else 4 if ch == '+' else 1
            pos += 1
    if pos != h*w or i > len(body):
        raise ValueError('invalid Number City clues')
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body[:i]}').cells
    if any(v == '?' or v == 0 or v >= 4096 for v in cells.values()):
        raise ValueError('Number City requires positive clues below 4096')
    rest = body[i:]
    count = (h*(w-1)+4)//5 + ((h-1)*w+4)//5
    if len(rest) != count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in rest):
        raise ValueError('invalid Number City room borders')
    borders = BorderCodec().decode(rest, h, w)[0]
    return Puzzle('numcity', h, w, cells, borders, body=body)


def encode(p):
    return f'https://puzz.link/p?numcity/{p.cols}/{p.rows}/{p.body}'


answer = roomnumbers.answer


def fileio(p, ans):
    def row(values): return ' '.join(map(str, values)) + ' \n'
    h, w = p.rows, p.cols
    out = [f'pzprv3\nnumcity\n{h}\n{w}\n']
    out.extend(row([p.cells.get((r, c), '.') for c in range(w)]) for r in range(h))
    out.extend(row([x if x is not None else '.' for x in line]) for line in ans)
    out.extend(row(['X' if r*(w-1)+c in p.borders else 0 for c in range(w-1)]) for r in range(h))
    out.extend(row(['X' if h*(w-1)+r*w+c in p.borders else 0 for c in range(w)]) for r in range(h-1))
    return ''.join(out)
