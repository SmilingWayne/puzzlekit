"""Moon or Sun room boundaries, paired clues, and loop marks."""
from puzzlekit._adapters import doubleback, packed, shading
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'moonsun' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Moon or Sun path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Moon or Sun requires at least two rows and columns')
    count = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(body) < count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:count]):
        raise ValueError('invalid room borders')
    border, consumed = BorderCodec().decode(body, h, w)
    cells = packed.decode(f'yinyang/{w}/{h}/{body[consumed:]}').cells
    return Puzzle('moonsun', h, w, cells, border, body=body[consumed:])


def encode(p):
    body = BorderCodec().encode(p.borders, p.rows, p.cols) + p.body
    return f'https://puzz.link/p?moonsun/{p.cols}/{p.rows}/{body}'


def answer(p, board, status):
    return doubleback.answer(p, board, status)


def fileio(p, ans):
    return doubleback.fileio(p, ans)
