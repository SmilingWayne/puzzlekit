"""Statue Park circle clues and preset piece banks."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.codecs import Number3Codec
from puzzlekit._adapters.model import Puzzle

BANKS = {'t': 5, 'd': 10, 'p': 12}


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 6 or parts[0] != 'statuepark' or parts[4] != '' or parts[5] not in BANKS or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('Statue Park supports the standard t, d, and p piece banks')
    w, h = map(int, parts[1:3])
    body = parts[3]
    if min(w, h) < 2 or len(body) != (h * w + 2) // 3 or any(c not in '0123456789abcdefghijklmnopq' for c in body):
        raise ValueError('invalid Statue Park circle data')
    vals = Number3Codec().decode(body)
    if any(vals[h*w:]):
        raise ValueError('circle data exceeds grid')
    cells = {divmod(i, w): v for i, v in enumerate(vals[:h*w]) if v}
    return Puzzle('statuepark', h, w, cells=cells, body=body, rule_flag=parts[5])


def encode(p):
    return f'https://puzz.link/p?statuepark/{p.cols}/{p.rows}/{p.body}//{p.rule_flag}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for (r, c), clue in p.cells.items():
            result[r][c] = 'black' if clue == 2 else 'white'
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind not in ('block', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Statue Park answer')
            result[y // 2][x // 2] = 'black' if kind == 'block' else 'white'
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nstatuepark\n{p.rows}\n{p.cols}\n{p.rule_flag}\n']
    out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    out.extend(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]) for line in answers)
    out.append(row([0] * BANKS[p.rule_flag]))
    return ''.join(out)
