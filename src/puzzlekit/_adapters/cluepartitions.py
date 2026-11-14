"""Number-clued partition puzzles using shared pzpr border marks."""
from puzzlekit._adapters import number10, partition, shading
from puzzlekit._adapters.model import Puzzle

TOKENS = {str(i): i for i in range(1, 5)} | {'.': '?'}


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in {'fillmat', 'nikoji'} or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid partition puzzle path')
    pid, w, h, body = parts[0], int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz requires at least two rows and columns')
    if pid == 'fillmat':
        cells = number10.decode(body, h, w, TOKENS)
    else:
        cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body}').cells
        if not cells or any(v == '?' or v == 0 or v >= 4096 for v in cells.values()):
            raise ValueError('cspuz NIKOJI requires positive clues up to 4095')
    return Puzzle(pid, h, w, cells)


def encode(p):
    if p.puzzle_type == 'fillmat':
        body = number10.encode(p.cells, p.rows, p.cols, {v: k for k, v in TOKENS.items()})
    else:
        body = shading.encode_shading(Puzzle('nurikabe', p.rows, p.cols, p.cells)).split('?', 1)[1].split('/', 3)[3].rstrip('/')
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{body}' + ('/' if body.endswith('.') else '')


def answer(p, board, status):
    return partition.answer(p, board, status)


def fileio(p, ans):
    return partition.fileio(p, ans)
