"""Cell clues and connecting lines for Coffee Milk and Mintonette."""
from puzzlekit._adapters import number10, packed, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in ('coffeemilk', 'mintonette') or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid connection puzzle path')
    pid, w, h, body = parts[0], int(parts[1]), int(parts[2]), parts[3]
    if min(w, h) < 2:
        raise ValueError('cspuz requires at least two rows and columns')
    if pid == 'coffeemilk':
        cells = number10.decode(body, h, w, {'1': 1, '2': 2, '.': '?'})
        if not any(v in (1, 2) for v in cells.values()):
            raise ValueError('Coffee Milk needs a black or white clue to require lines')
    else:
        cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body}').cells
        if any(isinstance(v, int) and v >= 4096 for v in cells.values()):
            raise ValueError('cspuz Mintonette clues must be below 4096')
        if not cells:
            raise ValueError('Mintonette needs endpoint clues')
    return Puzzle(pid, h, w, cells, body=body)


def encode(p):
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


answer = packed.answer


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        values = []
        for c in range(p.cols):
            v = p.cells.get((r, c))
            if p.puzzle_type == 'mintonette':
                values.append('.' if v is None else '0,-' if v == '?' else f'0,{v}')
            else:
                values.append('.' if v is None else '-' if v == '?' else v)
        out.append(row(values))
    for lines in ans:
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    return ''.join(out)
