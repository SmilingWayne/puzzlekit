"""Cell-number puzzles with room boundaries."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in {'nanro', 'putteria'} or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid room-number puzzle path')
    pid, w, h, body = parts[0], int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz requires at least two rows and columns')
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:count]):
        raise ValueError('invalid room borders')
    border, consumed = BorderCodec().decode(body, h, w)
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body[consumed:]}').cells
    if any(v != '?' and (v == 0 or v >= 4096) for v in cells.values()):
        raise ValueError('cspuz cannot represent this room-number clue')
    return Puzzle(pid, h, w, cells, border)


def encode(p):
    clues = shading.encode_shading(Puzzle('nurikabe', p.rows, p.cols, p.cells)).split('?', 1)[1].split('/', 3)[3].rstrip('/')
    body = BorderCodec().encode(p.borders, p.rows, p.cols) + clues
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{body}' + ('/' if body.endswith('.') else '')


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind == 'dot':
                value = '-' if p.puzzle_type == 'nanro' else '+'
            elif isinstance(kind, dict) and kind.get('kind') == 'text':
                value = kind['data']
            else:
                raise RuntimeError('unexpected room-number answer')
            result[y // 2][x // 2] = value
    return result


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    h, w = p.rows, p.cols
    n = h * (w - 1)
    ver = '.1' if p.puzzle_type == 'nanro' else ''
    out = [f'pzprv3{ver}\n{p.puzzle_type}\n{h}\n{w}\n']
    out.extend(row([int(r * (w - 1) + c in p.borders) for c in range(w - 1)]) for r in range(h))
    out.extend(row([int(n + r * w + c in p.borders) for c in range(w)]) for r in range(h - 1))
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(w)]) for r in range(h))
    out.extend(row([x if x is not None else '.' for x in line]) for line in ans)
    return ''.join(out)
