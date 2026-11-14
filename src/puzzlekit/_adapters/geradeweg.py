"""Geradeweg numbered loop clues and line marks."""
from dataclasses import replace

from puzzlekit._adapters import extended, shading


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    full = len(parts) == 5 and parts[1] == 'f'
    if full:
        parts.pop(1)
    if len(parts) != 4 or parts[0] != 'geradeweg':
        raise ValueError('unsupported Geradeweg path or rule variant')
    p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
    p.puzzle_type = 'geradeweg'
    p.rule_flag = 'f' if full else ''
    if p.rows < 2 or p.cols < 2 or (not p.cells and not full):
        raise ValueError('cspuz Geradeweg requires at least 2x2 and a clue unless the full-loop variant is selected')
    if any(v != '?' and v >= 4096 for v in p.cells.values()):
        raise ValueError('cspuz cannot represent this clue')
    return p


def encode(p):
    from puzzlekit._adapters.model import Puzzle
    flag = p.rule_flag + '/' if p.rule_flag else ''
    return shading.encode_shading(Puzzle('nurikabe', p.rows, p.cols, p.cells)).replace('?nurikabe/', '?geradeweg/' + flag, 1)


def answer(p, board, status):
    # Masyu and Geradeweg have the same inner cell-loop answer marks.
    return extended.answer(replace(p, puzzle_type='mashu'), board, status)


def fileio(p, ans):
    result = extended.fileio(p, ans)
    if p.rule_flag:
        header = f'pzprv3\ngeradeweg\n{p.rows}\n{p.cols}\n'
        result = result.replace(header, header + 'f\n', 1)
    return result
