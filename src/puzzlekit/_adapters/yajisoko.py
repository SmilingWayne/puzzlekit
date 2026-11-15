"""Yajisan-Sokoban clues and box movement lines."""
from puzzlekit._adapters import packed, shading


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'yajisoko':
        raise ValueError('invalid Yajisan-Sokoban path')
    p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
    if min(p.rows, p.cols) < 2:
        raise ValueError('cspuz Yajisan-Sokoban requires at least two rows and columns')
    if any(v != '?' and (v < 10 or v >= 4096) for v in p.cells.values()):
        raise ValueError('unsupported Yajisan-Sokoban arrow')
    p.puzzle_type = 'yajisoko'
    p.body = parts[3]
    return p


def encode(p):
    return f'https://puzz.link/p?yajisoko/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


answer = packed.answer


def fileio(p, edges):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nyajisoko\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        line = []
        for c in range(p.cols):
            v = p.cells.get((r, c))
            line.append('.' if v is None else '#' if v == '?' else f'{(v-10)%5},{(v-10)//5}')
        out.append(row(line))
    for lines in edges:
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    out.extend(row([0] * p.cols) for _ in range(p.rows))
    return ''.join(out)
