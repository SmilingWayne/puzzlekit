"""Aquarium room borders, outside clues, and water marks."""
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.model import Puzzle
from puzzlekit._adapters.shading import puzzle_path


def decode(source):
    parts = puzzle_path(source).split('/')
    flag = len(parts) == 6 and parts[1] == 'r'
    if flag:
        parts.pop(1)
    if len(parts) != 5 or parts[0] != 'aquarium' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Aquarium path or rule flag')
    w, h = int(parts[1]), int(parts[2])
    if w < 2 or h < 2:
        raise ValueError('cspuz Aquarium requires at least two rows and columns')
    border_text, body = parts[3:]
    length = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
    if len(border_text) != length or any(c not in '0123456789abcdefghijklmnopqrstuv' for c in border_text):
        raise ValueError('invalid Aquarium borders')
    borders, _ = BorderCodec().decode(border_text, h, w)
    values, pos, i = {}, 0, 0
    while i < len(body):
        ch = body[i]
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
            i += 1
        else:
            n = 2 if ch == '-' else 0
            digits = body[i + 1:i + 1 + n] if n else ch
            if len(digits) != (n or 1) or any(c not in '0123456789abcdef' for c in digits):
                raise ValueError('invalid Aquarium outside clue')
            if pos >= w + h:
                raise ValueError('too many Aquarium outside clues')
            values[pos] = int(digits, 16)
            pos += 1
            i += n + 1
        if pos > w + h:
            raise ValueError('too many Aquarium outside clues')
    if pos != w + h:
        raise ValueError('incomplete Aquarium outside clues')
    if not any(n > 0 for n in values.values()):
        raise ValueError('Aquarium needs a positive outside clue to exclude empty water')
    return Puzzle('aquarium', h, w, values, borders, rule_flag='r' if flag else '', body=body)


def encode(p):
    flag = 'r/' if p.rule_flag == 'r' else ''
    borders = BorderCodec().encode(p.borders, p.rows, p.cols)
    return f'https://puzz.link/p?aquarium/{flag}{p.cols}/{p.rows}/{borders}/{p.body}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green': continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind not in ('fill', 'dot') or y % 2 != 1 or x % 2 != 1 or not (3 <= y < 2*p.rows+3 and 3 <= x < 2*p.cols+3):
                raise RuntimeError('invalid Aquarium answer')
            result[(y - 3)//2][(x - 3)//2] = '#' if kind == 'fill' else '+'
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(x) for x in values) + ' \n'
    h, w = p.rows, p.cols
    out = [f'pzprv3\naquarium\n{h}\n{w}\n']
    if p.rule_flag == 'r': out.append('r\n')
    out.extend(row([int(r * (w - 1) + c in p.borders) for c in range(w - 1)]) for r in range(h))
    n = h * (w - 1)
    out.extend(row([int(n + r * w + c in p.borders) for c in range(w)]) for r in range(h - 1))
    out.append(row(['.'] + [p.cells.get(c, '.') for c in range(w)]))
    for r in range(h):
        out.append(row([p.cells.get(w+r, '.')] + [x or '.' for x in answers[r]]))
    return ''.join(out)
