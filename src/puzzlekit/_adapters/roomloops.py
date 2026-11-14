"""Numbered room clues with cell-loop answers."""
from dataclasses import replace
from puzzlekit._adapters import extended, regions, shading
from puzzlekit._adapters.grid import border_to_region_grid


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    empty = len(parts) == 5 and parts[0] == 'country' and parts[1] == 'e'
    if empty:
        parts.pop(1)
    if len(parts) != 4 or parts[0] not in {'country', 'nagenawa'}:
        raise ValueError('unsupported room-loop path or variant')
    p = regions.decode_regions('/'.join(['heyawake', *parts[1:]]))
    p.puzzle_type = parts[0]
    p.rule_flag = 'e' if empty else ''
    _, last = border_to_region_grid(p.borders, p.rows, p.cols)
    if not any(isinstance(v, int) and v > 0 for v in p.cells.values()) and (p.puzzle_type == 'nagenawa' or (last == 0 and not p.borders)):
        raise ValueError('cspuz may count an empty loop')
    if any(isinstance(v, int) and v >= 4096 for v in p.cells.values()):
        raise ValueError('cspuz cannot represent this room clue')
    return p


def encode(p):
    flag = p.rule_flag + '/' if p.rule_flag else ''
    return regions.encode_regions(replace(p, puzzle_type='heyawake')).replace('?heyawake/', '?' + p.puzzle_type + '/' + flag, 1)


def answer(p, board, status):
    return extended.answer(replace(p, puzzle_type='mashu'), board, status)


def fileio(p, answer_grid):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    h, w = p.rows, p.cols
    grid, last = border_to_region_grid(p.borders, h, w)
    ver = '.2' if p.puzzle_type == 'country' else ''
    out = [f'pzprv3{ver}\n{p.puzzle_type}\n{h}\n{w}\n']
    if p.puzzle_type == 'country':
        out.append('country_empty\n' if p.rule_flag else '\n')
        n = h * (w - 1)
        out.extend(row([int(r * (w - 1) + c in p.borders) for c in range(w - 1)]) for r in range(h))
        out.extend(row([int(n + r * w + c in p.borders) for c in range(w)]) for r in range(h - 1))
    else:
        out.append(f'{last + 1}\n')
        out.extend(row(line) for line in grid)
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(w)]) for r in range(h))
    for lines in (answer_grid['vertical'], answer_grid['horizontal']):
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    out.extend(row([0] * w) for _ in range(h))
    return ''.join(out)
