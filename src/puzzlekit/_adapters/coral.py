"""Coral outside clues and shading."""
from puzzlekit._adapters import nonogram
from puzzlekit._adapters.shading import puzzle_path


def decode(source):
    path = puzzle_path(source)
    if not path.startswith('coral/'):
        raise ValueError('invalid Coral path')
    p = nonogram.decode('nonogram/' + path[len('coral/'):])
    p.puzzle_type = 'coral'
    if p.rows < 2 or p.cols < 2:
        raise ValueError('cspuz Coral requires at least two rows and columns')
    return p


def encode(p):
    return f'https://pzprxs.vercel.app/p?coral/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    return nonogram.answer(p, board, status)


def fileio(p, answers):
    return nonogram.fileio(p, answers).replace('pzprv3\nnonogram\n', 'pzprv3\ncoral\n', 1)
