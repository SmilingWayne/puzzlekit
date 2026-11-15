"""Key West clue numbers, answer degrees, and connecting lines."""
from puzzlekit._adapters import packed, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'keywest' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid Key West path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Key West requires at least two rows and columns')
    cells, pos = {}, 0
    for i, ch in enumerate(parts[3]):
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
        elif ch in '0123456789abcde':
            if pos >= h*w:
                raise ValueError('Key West clues exceed grid')
            n = int(ch, 36)
            cells[divmod(pos, w)] = n % 5
            pos += 1 + n // 5
        else:
            raise ValueError('cspuz Key West requires numbered clues 0–4')
        if pos > h*w and i != len(parts[3]) - 1:
            raise ValueError('Key West clues exceed grid')
    return Puzzle('keywest', h, w, cells=cells, body=parts[3])


def encode(p):
    return f'https://puzz.link/p?keywest/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    values = [[None] * p.cols for _ in range(p.rows)]
    lines = []
    for item in board['data']:
        if item['color'] != 'green':
            continue
        kind = item['item']
        if kind in ('line', 'cross'):
            lines.append(item)
        elif isinstance(kind, dict) and kind.get('kind') == 'text' and kind.get('data') in ('0', '1', '2', '3', '4'):
            values[item['y'] // 2][item['x'] // 2] = kind['data']
        else:
            raise RuntimeError('invalid Key West answer')
    return values, packed.answer(p, {**board, 'data': lines}, status)


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    values, edges = ans
    out = [f'pzprv3\nkeywest\n{p.rows}\n{p.cols}\n']
    out.extend(row([p.cells.get((r,c), '.') for c in range(p.cols)]) for r in range(p.rows))
    for lines in edges:
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    out.extend(row([v if v is not None else '.' for v in line]) for line in values)
    return ''.join(out)
