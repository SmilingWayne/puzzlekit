"""Tents outside clues, trees, tents and confirmed pairings."""
from puzzlekit._adapters import packed, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    from puzzlekit._adapters.outside_numbers import _numbers
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'tents' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid Tents path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Tents requires at least two rows and columns')
    outside, body = _numbers(parts[3], w + h)
    trees, pos = {}, 0
    for ch in body:
        if ch in '0123456789abcdefgh':
            if pos >= w*h:
                raise ValueError('trees exceed grid')
            trees[divmod(pos, w)] = 1
            pos += int(ch, 36) + 1
        elif 'i' <= ch <= 'z':
            pos += ord(ch) - ord('i') + 1
        else:
            raise ValueError('invalid Tents trees')
        if pos > w*h:
            raise ValueError('trees exceed grid')
    return Puzzle('tents', h, w, cells=trees, borders=outside, body=parts[3])


def encode(p):
    return f'https://puzz.link/p?tents/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    cells = [[None] * p.cols for _ in range(p.rows)]
    edges = []
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'] - 2, item['x'] - 2, item['item']
            if kind in ('line', 'cross'):
                edges.append({**item, 'y': y, 'x': x})
            elif kind in ('triangle', 'dot') and y % 2 == 1 and x % 2 == 1 and 0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols:
                cells[y // 2][x // 2] = 'A' if kind == 'triangle' else '-'
            else:
                raise RuntimeError('invalid Tents answer')
    return cells, packed.answer(p, {**board, 'data': edges}, status)


def fileio(p, ans):
    def row(values): return ' '.join(str(v) if v is not None else '.' for v in values) + ' \n'
    cells, edges = ans
    out = [f'pzprv3\ntents\n{p.rows}\n{p.cols}\n']
    out.append(row([None] + p.borders[:p.cols]))
    for r in range(p.rows):
        out.append(row([p.borders[p.cols+r]] + [1 if (r,c) in p.cells else cells[r][c] for c in range(p.cols)]))
    for lines in edges:
        out.extend(row([-1 if v is True else 0 for v in line]) for line in lines)
    return ''.join(out)
