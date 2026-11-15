"""Pencils clues, pencil boundaries, tips and lines."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle

_DIRS = {'pencilDown': 1, 'pencilUp': 2, 'pencilRight': 3, 'pencilLeft': 4}


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'pencils' or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid Pencils path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('Pencils requires at least two rows and columns')
    body, cells, pos, i = parts[3], {}, 0, 0
    while i < len(body):
        ch = body[i]
        if 'k' <= ch <= 'z':
            pos += ord(ch) - ord('k') + 1
            i += 1
            continue
        if pos >= h*w:
            raise ValueError('Pencils clues exceed grid')
        if 'g' <= ch <= 'j':
            value = 'd' + str(ord(ch) - ord('g') + 1)
            i += 1
        elif ch == '.':
            value = '?'
            i += 1
        elif ch in '0123456789abcdef':
            value = int(ch, 16)
            i += 1
        elif ch == '-' and len(body[i+1:i+3]) == 2 and all(x in '0123456789abcdef' for x in body[i+1:i+3]):
            value = int(body[i+1:i+3], 16)
            i += 3
        else:
            raise ValueError('invalid Pencils clue')
        cells[divmod(pos, w)] = value
        pos += 1
    if pos > h*w or any(v == 0 for v in cells.values()):
        raise ValueError('invalid Pencils clue range')
    return Puzzle('pencils', h, w, cells, body=body)


def encode(p):
    return f'https://puzz.link/p?pencils/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    marks = {}
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] == 'green':
                marks[(item['y'], item['x'])] = item['item']
    return marks


def fileio(p, marks):
    def row(values): return ' '.join(map(str, values)) + ' \n'
    h, w = p.rows, p.cols
    tip_borders = set()
    for (y, x), kind in marks.items():
        direction = _DIRS.get(kind)
        if direction:
            dy, dx = {1: (1, 0), 2: (-1, 0), 3: (0, 1), 4: (0, -1)}[direction]
            tip_borders.add((y+dy, x+dx))
    out = [f'pzprv3\npencils\n{h}\n{w}\n']
    for r in range(h):
        line = []
        for c in range(w):
            clue = p.cells.get((r,c))
            line.append('.' if clue is None else clue[1:] if isinstance(clue, str) and clue.startswith('d') else 'o-2' if clue == '?' else f'o{clue}')
        out.append(row(line))
    coords = ([(2*r+1, 2*c+2) for r in range(h) for c in range(w-1)],
              [(2*r+2, 2*c+1) for r in range(h-1) for c in range(w)])
    for values, width in zip(coords, (w-1, w)):
        for i in range(0, len(values), width):
            out.append(row([1 if marks.get(pos) == 'boldWall' or pos in tip_borders else 0 for pos in values[i:i+width]]))
    for values, width in zip(coords, (w-1, w)):
        for i in range(0, len(values), width):
            out.append(row([1 if marks.get(pos) == 'line' else -1 if marks.get(pos) == 'cross' else 0 for pos in values[i:i+width]]))
    out.extend(row([_DIRS.get(marks.get((2*r+1,2*c+1)), '.') for c in range(w)]) for r in range(h))
    return ''.join(out)
