"""Narrowfence number clues and partition borders."""
from puzzlekit._adapters import ncells, partition, shading


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'narrow':
        raise ValueError('invalid Narrowfence path')
    p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
    if min(p.rows, p.cols) < 2:
        raise ValueError('cspuz Narrowfence requires at least two rows and columns')
    if not p.cells or any(v == '?' or v == 0 or v >= 4096 for v in p.cells.values()):
        raise ValueError('Narrowfence requires positive clues below 4096')
    p.puzzle_type = 'narrow'
    p.body = parts[3]
    return p


def encode(p):
    return f'https://puzz.link/p?narrow/{p.cols}/{p.rows}/{p.body}'


answer = partition.answer
fileio = ncells.fileio
