"""Yajisan-Kazusan arrow clues and shading."""
from dataclasses import replace

from puzzlekit._adapters import regions, yajilin
from puzzlekit._adapters.shading import puzzle_path


def decode(source):
    path = puzzle_path(source)
    if not path.startswith('yajikazu/'):
        raise ValueError('unsupported Yajisan-Kazusan puzzle path')
    p = yajilin.decode('yajilin/' + path[len('yajikazu/'):])
    p.puzzle_type = 'yajikazu'
    forces_shading = False
    for (r, c), (direction, value) in p.cells.items():
        if value != '?' and value >= 256:
            raise ValueError('cspuz Yajisan-Kazusan supports arrow numbers 0–255')
        if direction and value != '?' and value > 0:
            has_target = (direction == 1 and r > 0 or direction == 2 and r < p.rows - 1 or
                          direction == 3 and c > 0 or direction == 4 and c < p.cols - 1)
            if not has_target:
                raise ValueError('cspuz does not constrain arrows pointing outside the grid')
            forces_shading = True
    if not forces_shading:
        raise ValueError('a positive directional clue is required to exclude empty shading')
    return p


def encode(p):
    return yajilin.encode(replace(p, puzzle_type='yajilin')).replace('?yajilin/', '?yajikazu/', 1)


def answer(p, board, status):
    return regions.answer(p, board, status)


def fileio(p, answers):
    def row(values): return ' '.join(str(x) for x in values) + ' \n'
    out = [f'pzprv3\nyajikazu\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        line = []
        for c in range(p.cols):
            clue = p.cells.get((r, c))
            line.append('.' if clue is None else f'{clue[0]},{"-" if clue[1] == "?" else clue[1]}')
        out.append(row(line))
    for line in answers:
        out.append(row(['#' if x == 'black' else '+' if x == 'white' else '.' for x in line]))
    return ''.join(out)
