"""Guide Arrow goal, arrows, and shading."""
from puzzlekit._adapters.model import Puzzle
from puzzlekit._adapters.shading import puzzle_path


def decode(source):
    parts = puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'guidearrow' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Guide Arrow path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2: raise ValueError('Guide Arrow requires at least two rows and columns')
    def number(i):
        if i >= len(body): raise ValueError('missing Guide Arrow goal')
        n = 2 if body[i] == '-' else 3 if body[i] == '+' else 0
        digits = body[i + 1:i + 1 + n] if n else body[i]
        if len(digits) != (n or 1) or any(ch not in '0123456789abcdef' for ch in digits):
            raise ValueError('invalid Guide Arrow goal')
        return int(digits, 16), i + n + 1
    x, i = number(0)
    y, i = number(i)
    if not 1 <= x <= w or not 1 <= y <= h:
        raise ValueError('Guide Arrow goal is outside the grid')
    cells, pos = {}, 0
    while i < len(body):
        ch = body[i]
        if ch == '.':
            value, advance = '?', 1
        elif ch in '123456789abcde':
            value = int(ch, 16) % 5
            advance = int(ch, 16) // 5 + 1
            if value == 0: raise ValueError('cspuz cannot represent direction zero')
        elif 'g' <= ch <= 'z':
            value, advance = None, ord(ch) - ord('g') + 1
        else:
            raise ValueError('invalid Guide Arrow clue')
        if value is not None:
            if pos >= w * h: raise ValueError('Guide Arrow clues exceed grid')
            cells[divmod(pos, w)] = value
        pos += advance
        if pos > w * h and i + 1 < len(body): raise ValueError('Guide Arrow clues exceed grid')
        i += 1
    if (y-1, x-1) in cells:
        raise ValueError('Guide Arrow goal cannot contain an arrow clue')
    return Puzzle('guidearrow', h, w, cells, body=body, holes={'goal': (y-1, x-1)})


def encode(p):
    return f'https://puzz.link/p?guidearrow/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green': continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind not in ('fill', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y//2 < p.rows and 0 <= x//2 < p.cols):
                raise RuntimeError('invalid Guide Arrow answer')
            result[y//2][x//2] = '#' if kind == 'fill' else '+'
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(x) for x in values) + ' \n'
    y, x = p.holes['goal']
    out = [f'pzprv3\nguidearrow\n{p.rows}\n{p.cols}\n{2*x+1} {2*y+1}\n']
    for r in range(p.rows):
        out.append(row(['-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(p.cols)]))
    for line in answers: out.append(row([x or '.' for x in line]))
    return ''.join(out)
