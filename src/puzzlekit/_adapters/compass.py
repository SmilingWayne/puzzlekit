"""Compass directional clues and partition borders."""
from puzzlekit._adapters import partition, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'compass' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid Compass path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Compass requires at least two rows and columns')
    body, cells, pos, i = parts[3], {}, 0, 0
    while i < len(body):
        ch = body[i]
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
            i += 1
            continue
        if pos >= h * w:
            raise ValueError('Compass clues exceed grid')
        values = []
        for _ in range(4):
            if i >= len(body):
                raise ValueError('incomplete Compass clue')
            ch = body[i]
            if ch == '.':
                values.append(-1)
                i += 1
            elif ch in '0123456789abcdef':
                values.append(int(ch, 16))
                i += 1
            elif ch in '-+':
                n = 2 if ch == '-' else 3
                digits = body[i+1:i+1+n]
                if len(digits) != n or any(c not in '0123456789abcdef' for c in digits):
                    raise ValueError('invalid Compass clue')
                values.append(int(digits, 16))
                i += n + 1
            else:
                raise ValueError('invalid Compass clue')
        cells[divmod(pos, w)] = values
        pos += 1
    if pos > h * w or not cells:
        raise ValueError('Compass requires at least one clue')
    return Puzzle('compass', h, w, cells=cells, body=body)


def encode(p):
    return f'https://puzz.link/p?compass/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


answer = partition.answer


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    vertical, horizontal, _ = ans
    out = [f'pzprv3\ncompass\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        line = []
        for c in range(p.cols):
            clue = p.cells.get((r,c))
            line.append('.' if clue is None else ','.join(str(clue[i]) for i in (3, 1, 2, 0)))
        out.append(row(line))
    for lines in (vertical, horizontal):
        out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
    return ''.join(out)
