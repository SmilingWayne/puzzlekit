"""Sendai-Miyagi room clues and answer borders."""
from dataclasses import replace
from puzzlekit._adapters import partition, regions


def decode(source):
    path = regions.puzzle_path(source)
    if not path.startswith('sendai/'):
        raise ValueError('invalid Sendai-Miyagi path')
    p = regions.decode_regions('heyawake/' + path.split('/', 1)[1])
    if any(isinstance(v, int) and v >= 4096 for v in p.cells.values()):
        raise ValueError('Sendai-Miyagi clues must be below 4096 or ?')
    p.puzzle_type = 'sendai'
    return p


def encode(p):
    return regions.encode_regions(replace(p, puzzle_type='heyawake')).replace('?heyawake/', '?sendai/', 1)


answer = partition.answer


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    vertical, horizontal, _ = ans
    h, w = p.rows, p.cols
    out = [f'pzprv3\nsendai\n{h}\n{w}\n']
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(w)]) for r in range(h))
    n = h * (w - 1)
    def mark(clue, value):
        return 1 if clue else 2 if value is True else 4 if value is False else 0
    out.extend(row([mark(r * (w - 1) + c in p.borders, vertical[r][c]) for c in range(w - 1)]) for r in range(h))
    out.extend(row([mark(n + r * w + c in p.borders, horizontal[r][c]) for c in range(w)]) for r in range(h - 1))
    return ''.join(out)
