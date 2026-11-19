"""Ripple Effect room boundaries, number clues and optional holes."""
from puzzlekit._adapters import packed, roomnumbers, shading
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'ripple' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Ripple Effect path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Ripple Effect requires at least two rows and columns')
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:count]):
        raise ValueError('invalid room borders')
    border, consumed = BorderCodec().decode(body, h, w)
    rest = body[consumed:]
    pos = i = 0
    while i < len(rest) and pos < w * h:
        ch = rest[i]
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
            i += 1
        else:
            i += {'-': 3, '+': 4, '=': 4, '@': 4, '*': 5, '$': 6}.get(ch, 1)
            pos += 1
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{rest[:i]}').cells
    if any(v != '?' and (v == 0 or v >= 4096) for v in cells.values()):
        raise ValueError('cspuz cannot represent this Ripple Effect clue')
    holes_body = rest[i:]
    holes = packed.decode(f'simpleloop/{w}/{h}/{holes_body}').cells if holes_body else {}
    if set(cells) & set(holes):
        raise ValueError('Ripple Effect holes cannot also contain clues')
    return Puzzle('ripple', h, w, cells, border, body=holes_body, holes=holes)


def encode(p):
    clues = shading.encode_shading(Puzzle('nurikabe', p.rows, p.cols, p.cells)).split('?', 1)[1].split('/', 3)[3].rstrip('/')
    body = BorderCodec().encode(p.borders, p.rows, p.cols) + clues + p.body
    return f'https://puzz.link/p?ripple/{p.cols}/{p.rows}/{body}' + ('/' if body.endswith('.') else '')


def answer(p, board, status):
    return roomnumbers.answer(p, board, status)


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    h, w = p.rows, p.cols
    n = h * (w - 1)
    out = [f'pzprv3\nripple\n{h}\n{w}\n']
    out.extend(row([int(r * (w - 1) + c in p.borders) for c in range(w - 1)]) for r in range(h))
    out.extend(row([int(n + r * w + c in p.borders) for c in range(w)]) for r in range(h - 1))
    out.extend(row(['#' if (r, c) in p.holes else '-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(w)]) for r in range(h))
    out.extend(row([x if x is not None else '.' for x in line]) for line in ans)
    return ''.join(out)
