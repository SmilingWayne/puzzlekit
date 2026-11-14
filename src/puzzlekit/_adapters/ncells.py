"""FourCells and FiveCells number clues and answer borders."""
from puzzlekit._adapters import number10, partition, shading
from puzzlekit._adapters.model import Puzzle

TYPES = {'fourcells', 'fivecells', 'heteromino'}
TOKENS = {str(i): i for i in range(5)} | {'.': '?', '7': '*'}


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in TYPES or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid FourCells or FiveCells path')
    pid, w, h, body = parts[0], int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz requires at least two rows and columns')
    tokens = {'7': '*'} if pid == 'heteromino' else TOKENS
    return Puzzle(pid, h, w, number10.decode(body, h, w, tokens))


def encode(p):
    body = number10.encode(p.cells, p.rows, p.cols, {v: k for k, v in TOKENS.items()})
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{body}' + ('/' if body.endswith('.') else '')


def answer(p, board, status):
    return partition.answer(p, board, status)


def fileio(p, ans):
    vertical, horizontal, _ = ans
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    ver = '.1' if p.puzzle_type == 'fourcells' else ''
    out = [f'pzprv3{ver}\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n']
    out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    def mark(x): return 1 if x is True else -1 if x is False else 0
    out.extend(row([0, *[mark(x) for x in line], 0]) for line in vertical)
    out.append(row([0] * p.cols))
    out.extend(row([mark(x) for x in line]) for line in horizontal)
    out.append(row([0] * p.cols))
    return ''.join(out)
