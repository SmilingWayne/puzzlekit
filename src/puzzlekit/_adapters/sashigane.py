"""Sashigane corner and arrow clues with answer borders."""
from puzzlekit._adapters import partition, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'sashigane' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Sashigane path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Sashigane requires at least two rows and columns')
    cells, pos, i = {}, 0, 0
    while i < len(body):
        ch = body[i]
        if 'k' <= ch <= 'z':
            pos += ord(ch) - ord('k') + 1
        else:
            if pos >= w * h:
                raise ValueError('puzzle data exceeds grid')
            if ch in 'ghij':
                value = str(ord(ch) - ord('g') + 1)
            elif ch == '.':
                value = 'o'
            elif ch in '0123456789abcdef':
                value = 'o' + str(int(ch, 16))
            elif ch == '-' and len(body[i + 1:i + 3]) == 2 and all(x in '0123456789abcdef' for x in body[i + 1:i + 3]):
                value = 'o' + str(int(body[i + 1:i + 3], 16))
                i += 2
            else:
                raise ValueError('unsupported Sashigane clue')
            cells[divmod(pos, w)] = value
            pos += 1
        if pos > w * h:
            raise ValueError('puzzle data exceeds grid')
        i += 1
    return Puzzle('sashigane', h, w, cells, body=body)


def encode(p):
    return f'https://puzz.link/p?sashigane/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    return partition.answer(p, board, status)


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    vertical, horizontal, _ = ans
    out = [f'pzprv3\nsashigane\n{p.rows}\n{p.cols}\n']
    out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
    for lines in (vertical, horizontal):
        out.extend(row([1 if x is True else -1 if x is False else 0 for x in line]) for line in lines)
    return ''.join(out)
