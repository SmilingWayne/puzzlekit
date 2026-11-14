"""Circles and Squares color clues and shading marks."""
from puzzlekit._adapters import packed, shading


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'circlesquare':
        raise ValueError('invalid Circles and Squares path')
    p = packed.decode('/'.join(['yinyang', *parts[1:]]))
    p.puzzle_type = 'circlesquare'
    if 2 not in p.cells.values() and p.rows == p.cols:
        raise ValueError('cspuz may count an all-white answer')
    return p


def encode(p):
    return f'https://puzz.link/p?circlesquare/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    result = shading.answer(p, board, status)
    if status != 'no_solution':
        for (r, c), clue in p.cells.items():
            result[r][c] = 'white' if clue == 1 else 'black'
    return result


def fileio(p, ans):
    return shading.fileio(p, ans)
