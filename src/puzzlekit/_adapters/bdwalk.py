"""Building Walk start/goal, floor clues, and path."""
from puzzlekit._adapters import packed, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 6 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 5 or parts[:2] != ['bdwalk', 'm'] or not all(v.isdigit() for v in parts[2:4]):
        raise ValueError('cspuz Building Walk requires the m rule variant')
    w, h = map(int, parts[2:4])
    body = parts[4]
    if min(w, h) < 2 or len(body) < 4 or any(ch not in '123456789abcdef' for ch in body[:4]):
        raise ValueError('invalid Building Walk dimensions or endpoints')
    x1, y1, x2, y2 = (int(ch, 16) for ch in body[:4])
    if not (x1 <= w and x2 <= w and y1 <= h and y2 <= h) or (x1, y1) == (x2, y2):
        raise ValueError('invalid Building Walk endpoints')
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body[4:]}').cells
    if any(isinstance(v, int) and v >= 4096 for v in cells.values()):
        raise ValueError('Building Walk clues must be below 4095')
    cells = {k: 'U' if v == 0 else 'D' if v == 1 else '-' if v == '?' else v - 1 for k, v in cells.items()}
    if not any(isinstance(v, int) for v in cells.values()):
        raise ValueError('Building Walk requires a numbered floor')
    return Puzzle('bdwalk', h, w, cells=cells, body=body, holes={'start': (x1, y1), 'goal': (x2, y2)})


def encode(p):
    return f'https://puzz.link/p?bdwalk/m/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


answer = packed.answer


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    x1, y1 = p.holes['start']
    x2, y2 = p.holes['goal']
    out = [f'pzprv3\nbdwalk\n{p.rows}\n{p.cols}\nm\n{2*x1-1} {2*y1-1} {2*x2-1} {2*y2-1}\n']
    out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    for lines in ans:
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    return ''.join(out)
