"""Castle Wall colored arrow clues and loop edges."""
from puzzlekit._adapters import packed, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'castle' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid Castle Wall path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Castle Wall requires at least two rows and columns')
    body, cells, i, pos = parts[3], {}, 0, 0
    while i < len(body):
        ch = body[i]
        if 'a' <= ch <= 'z':
            pos += ord(ch) - ord('a') + 1
            i += 1
            continue
        if ch not in '012' or pos >= w * h or i + 2 >= len(body):
            raise ValueError('invalid Castle Wall clue')
        side = int(ch)
        digit = body[i + 1]
        if digit not in '0123456789':
            raise ValueError('invalid Castle Wall arrow')
        d = int(digit)
        length = 1 if d < 5 else 2
        digits = body[i + 2:i + 2 + length]
        if digits == '.' and length == 1:
            value = '?'
        elif len(digits) == length and all(x in '0123456789abcdef' for x in digits):
            value = int(digits, 16)
        else:
            raise ValueError('invalid Castle Wall arrow number')
        if d % 5 == 0 and value != '?':
            raise ValueError('numbered Castle Wall clues require an arrow')
        cells[divmod(pos, w)] = (side, d % 5, value)
        pos += 1
        i += 2 + length
    if pos > h * w:
        raise ValueError('clues exceed grid')
    if not any(side == 1 or direction and isinstance(value, int) and value > 0
               for side, direction, value in cells.values()):
        raise ValueError('Castle Wall requires an inside clue or positive arrow to exclude an empty loop')
    return Puzzle('castle', h, w, cells=cells, body=body)


def encode(p):
    return f'https://puzz.link/p?castle/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


answer = packed.answer


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\ncastle\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        line = []
        for c in range(p.cols):
            clue = p.cells.get((r, c))
            if clue is None:
                line.append('0,-1,0')
            else:
                side, direction, value = clue
                line.append(f'{direction},{"-" if value == "?" else value},{side}')
        out.append(row(line))
    for lines in ans:
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    return ''.join(out)
