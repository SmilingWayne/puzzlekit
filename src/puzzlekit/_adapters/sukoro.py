"""Sukoro number clues and confirmed number/empty marks."""
from puzzlekit._adapters import number10, shading
from puzzlekit._adapters.model import Puzzle

TOKENS = {str(i): i for i in range(1, 5)} | {'.': '?'}


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'sukoro' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Sukoro path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Sukoro requires at least two rows and columns')
    cells = number10.decode(body, h, w, TOKENS)
    if not cells:
        raise ValueError('cspuz Sukoro may count an empty answer')
    return Puzzle('sukoro', h, w, cells)


def encode(p):
    body = number10.encode(p.cells, p.rows, p.cols, {v: k for k, v in TOKENS.items()})
    return f'https://puzz.link/p?sukoro/{p.cols}/{p.rows}/{body}' + ('/' if body.endswith('.') else '')


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind == 'dot':
                value = '-'
            elif isinstance(kind, dict) and kind.get('kind') == 'text' and kind.get('data') in ('1', '2', '3', '4'):
                value = kind['data']
            else:
                raise RuntimeError('unexpected Sukoro answer')
            result[y // 2][x // 2] = value
    return result


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nsukoro\n{p.rows}\n{p.cols}\n']
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    out.extend(row([x if x is not None else '.' for x in line]) for line in ans)
    return ''.join(out)
