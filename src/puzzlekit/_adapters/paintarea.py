"""Paintarea room borders and number10 cell clues."""
from puzzlekit._adapters import number10, shading
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.grid import border_to_region_grid
from puzzlekit._adapters.model import Puzzle

TOKENS = {str(i): i for i in range(5)} | {'.': '?'}
TILECITY_TOKENS = {str(i): i for i in range(1, 10)} | {'.': '?'}
TONTON_TOKENS = {str(i): i for i in range(1, 4)}


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in ('paintarea', 'tilecity', 'tontonbeya') or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid room shading path')
    pid = parts[0]
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Paintarea requires at least two rows and columns')
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:count]):
        raise ValueError('invalid room borders')
    border, consumed = BorderCodec().decode(body, h, w)
    tokens = {'tilecity': TILECITY_TOKENS, 'tontonbeya': TONTON_TOKENS}.get(pid, TOKENS)
    cells = number10.decode(body[consumed:], h, w, tokens)
    return Puzzle(pid, h, w, cells, border)


def encode(p):
    body = BorderCodec().encode(p.borders, p.rows, p.cols)
    tokens = {'tilecity': TILECITY_TOKENS, 'tontonbeya': TONTON_TOKENS}.get(p.puzzle_type, TOKENS)
    body += number10.encode(p.cells, p.rows, p.cols, {v: k for k, v in tokens.items()})
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{body}' + ('/' if body.endswith('.') else '')


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] == 'green':
                y, x, kind = item['y'], item['x'], item['item']
                if p.puzzle_type == 'tontonbeya' and kind in ('circle', 'triangle', 'square'):
                    result[y // 2][x // 2] = {'circle': 1, 'triangle': 2, 'square': 3}[kind]
                    continue
                if kind not in ('fill', 'dot') or y % 2 != 1 or x % 2 != 1:
                    raise RuntimeError('unexpected Paintarea answer')
                result[y // 2][x // 2] = 'black' if kind == 'fill' else 'white'
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    grid, max_id = border_to_region_grid(p.borders, p.rows, p.cols)
    out = [f'pzprv3\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n{max_id + 1}\n']
    out.extend(row(line) for line in grid)
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    if p.puzzle_type == 'tontonbeya':
        out.extend(row([x if x is not None else '.' for x in line]) for line in answers)
    else:
        out.extend(row(['#' if x == 'black' else '+' if x == 'white' else '.' for x in line]) for line in answers)
    return ''.join(out)
