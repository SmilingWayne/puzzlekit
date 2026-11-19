"""Ring-ring blocked cells and rectangular-loop answer lines."""
from dataclasses import replace
from puzzlekit._adapters import extended, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'ringring' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Ring-ring path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Ring-ring requires at least two rows and columns')
    cells, pos = {}, 0
    for ch in body:
        if ch == '.':
            pos += 36
        elif ch in '0123456789abcdefghijklmnopqrstuvwxyz':
            pos += int(ch, 36)
            if pos >= w * h:
                raise ValueError('puzzle data exceeds grid')
            cells[divmod(pos, w)] = 1
            pos += 1
        else:
            raise ValueError('invalid Ring-ring clue')
    if len(cells) == w * h:
        raise ValueError('cspuz Ring-ring may count an empty answer')
    return Puzzle('ringring', h, w, cells, body=body)


def encode(p):
    return f'https://puzz.link/p?ringring/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    return extended.answer(replace(p, puzzle_type='mashu'), board, status)


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nringring\n{p.rows}\n{p.cols}\n']
    out.extend(row([int((r, c) in p.cells) for c in range(p.cols)]) for r in range(p.rows))
    for lines in (ans['vertical'], ans['horizontal']):
        out.extend(row([1 if x is True else -1 if x is False else 0 for x in line]) for line in lines)
    return ''.join(out)
