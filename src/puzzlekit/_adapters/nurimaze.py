"""Nuri-Maze room boundaries, route clues, and shading."""
from puzzlekit._adapters import paintarea, shading
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.grid import border_to_region_grid
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'nurimaze' or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid Nuri-Maze path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Nuri-Maze requires at least two rows and columns')
    body = parts[3]
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:count]):
        raise ValueError('invalid room borders')
    border, consumed = BorderCodec().decode(body, h, w)
    cells, pos = {}, 0
    for ch in body[consumed:]:
        if ch in '1234':
            if pos >= h * w:
                raise ValueError('clues exceed grid')
            cells[divmod(pos, w)] = int(ch)
            pos += 1
        elif ch in '56789abcdefghijklmnopqrstuvwxyz':
            pos += int(ch, 36) - 4
        else:
            raise ValueError('invalid Nuri-Maze clue')
        if pos > h * w:
            raise ValueError('clues exceed grid')
    if list(cells.values()).count(1) != 1 or list(cells.values()).count(2) != 1:
        raise ValueError('Nuri-Maze requires exactly one start and one goal')
    return Puzzle('nurimaze', h, w, cells, border)


def encode(p):
    body = BorderCodec().encode(p.borders, p.rows, p.cols)
    skip = 0
    for i in range(p.rows * p.cols):
        clue = p.cells.get(divmod(i, p.cols))
        if clue is None:
            skip += 1
            if skip == 31:
                body += 'z'
                skip = 0
        else:
            if skip:
                body += '0123456789abcdefghijklmnopqrstuvwxyz'[skip + 4]
                skip = 0
            body += str(clue)
    if skip:
        body += '0123456789abcdefghijklmnopqrstuvwxyz'[skip + 4]
    return f'https://puzz.link/p?nurimaze/{p.cols}/{p.rows}/{body}'


answer = paintarea.answer


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    grid, max_id = border_to_region_grid(p.borders, p.rows, p.cols)
    out = [f'pzprv3\nnurimaze\n{p.rows}\n{p.cols}\n{max_id + 1}\n']
    out.extend(row(line) for line in grid)
    symbols = {1: 's', 2: 'g', 3: 'o', 4: 't'}
    out.extend(row([symbols.get(p.cells.get((r, c)), '.') for c in range(p.cols)]) for r in range(p.rows))
    out.extend(row(['#' if x == 'black' else '+' if x == 'white' else '.' for x in line]) for line in answers)
    return ''.join(out)
