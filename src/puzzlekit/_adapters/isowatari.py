"""Isowatari circle clues, holes, and shading."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.codecs import Number3Codec
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 5 or parts[0] != 'isowatari' or not all(v.isdigit() for v in parts[1:4]):
        raise ValueError('invalid Isowatari path')
    w, h, size = map(int, parts[1:4])
    if min(w, h) < 2 or size < 1:
        raise ValueError('invalid Isowatari dimensions or cluster size')
    body = parts[4]
    count, hole_count = (h * w + 2) // 3, (h * w + 4) // 5
    clue_data, hole_data = body[:count], body[count:]
    if len(clue_data) != count or any(c not in '0123456789abcdefghijklmnopq' for c in clue_data):
        raise ValueError('invalid Isowatari circles')
    if hole_data and (len(hole_data) != hole_count or any(c not in '0123456789abcdefghijklmnopqrstuv' for c in hole_data)):
        raise ValueError('invalid Isowatari holes')
    vals = Number3Codec().decode(clue_data)
    holes = [bool(int(c, 32) & (1 << (4 - j))) for c in hole_data for j in range(5)]
    if any(vals[h*w:]) or any(holes[h*w:]):
        raise ValueError('Isowatari data exceeds grid')
    holes = {divmod(i, w): True for i, v in enumerate(holes[:h*w]) if v}
    cells = {divmod(i, w): v for i, v in enumerate(vals[:h*w]) if v}
    if any(pos in holes for pos in cells):
        raise ValueError('circles cannot overlap holes')
    return Puzzle('isowatari', h, w, cells=cells, holes=holes, body=body, rule_flag=str(size))


def encode(p):
    return f'https://puzz.link/p?isowatari/{p.cols}/{p.rows}/{p.rule_flag}/{p.body}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for (r, c), clue in p.cells.items():
            result[r][c] = 'black' if clue == 2 else 'white'
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind not in ('block', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Isowatari answer')
            result[y // 2][x // 2] = 'black' if kind == 'block' else 'white'
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    h, w = p.rows, p.cols
    out = [f'pzprv3\nisowatari\n{h}\n{w}\n{p.rule_flag}\n']
    out.extend(row(['*' if (r,c) in p.holes else p.cells.get((r,c), '.') for c in range(w)]) for r in range(h))
    out.extend(row([p.cells.get((r,c), '.') for c in range(w)]) for r in range(h))
    out.extend(row(['+' if v == 'white' else '.' for v in line]) for line in answers)
    out.extend(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]) for line in answers)
    return ''.join(out)
