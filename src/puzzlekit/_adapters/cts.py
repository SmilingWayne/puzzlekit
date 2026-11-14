"""Cross the Streams outside clues and shading."""
from puzzlekit._adapters import nonogram
from puzzlekit._adapters.model import Puzzle
from puzzlekit._adapters.shading import puzzle_path


def decode(source):
    parts = puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'cts' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Cross the Streams path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2: raise ValueError('Cross the Streams requires at least two rows and columns')
    count = w * ((h + 1) // 2) + h * ((w + 1) // 2)
    cells, pos, i = {}, 0, 0
    while i < len(body):
        ch = body[i]
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
            i += 1
        else:
            n = 2 if ch == '-' else 0
            digits = body[i+1:i+3] if n else ch
            if ch == '.': value = -2
            elif len(digits) == (n or 1) and all(c in '0123456789abcdef' for c in digits): value = int(digits, 16)
            else: raise ValueError('invalid Cross the Streams clue')
            if pos >= count: raise ValueError('too many outside clues')
            cells[pos] = value
            pos += 1
            i += n + 1
        if pos > count: raise ValueError('too many outside clues')
    if pos != count: raise ValueError('incomplete outside clues')
    return Puzzle('cts', h, w, cells, body=body)


def encode(p):
    end = '/' if p.body.endswith('.') else ''
    return f'https://puzz.link/p?cts/{p.cols}/{p.rows}/{p.body}{end}'


def answer(p, board, status):
    return nonogram.answer(p, board, status)


def fileio(p, answers):
    return nonogram.fileio(p, answers).replace('pzprv3\nnonogram\n', 'pzprv3\ncts\n', 1)
