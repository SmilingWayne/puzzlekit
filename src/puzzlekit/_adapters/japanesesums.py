"""Japanese Sums outside clue sequences and number/shading answers."""
from puzzlekit._adapters import nonogram, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 5 or parts[0] != 'japanesesums' or not all(v.isdigit() for v in parts[1:4]):
        raise ValueError('invalid Japanese Sums path')
    w, h, limit = map(int, parts[1:4])
    if min(w, h) < 2 or not 1 <= limit <= 9:
        raise ValueError('invalid Japanese Sums dimensions or number range')
    body = parts[4]
    count = w * ((h + 1) // 2) + h * ((w + 1) // 2)
    outside, pos, i = {}, 0, 0
    while pos < count and i < len(body):
        ch = body[i]
        if 'g' <= ch <= 'z':
            pos += ord(ch) - ord('g') + 1
            i += 1
        else:
            if ch == '.':
                value, length = -2, 1
            elif ch in '123456789abcdef':
                value, length = int(ch, 16), 1
            elif ch == '-' and len(body[i+1:i+3]) == 2 and all(c in '0123456789abcdef' for c in body[i+1:i+3]):
                value, length = int(body[i+1:i+3], 16), 3
                if value == 0:
                    raise ValueError('sum clues must be positive or unknown')
            else:
                raise ValueError('invalid Japanese Sums outside clue')
            outside[pos] = value
            pos += 1
            i += length
    if pos != count:
        raise ValueError('incomplete Japanese Sums outside clues')
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body[i:]}').cells if body[i:] else {}
    if any(not isinstance(v, int) or not 1 <= v <= limit for v in cells.values()):
        raise ValueError('invalid Japanese Sums given number')
    return Puzzle('japanesesums', h, w, cells=cells, borders=outside, body=body, rule_flag=str(limit))


def encode(p):
    return f'https://puzz.link/p?japanesesums/{p.cols}/{p.rows}/{p.rule_flag}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    result = [['q' + str(p.cells[(r,c)]) if (r,c) in p.cells else None for c in range(p.cols)] for r in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Japanese Sums answer coordinate')
            if kind == 'block':
                value = '-'
            elif isinstance(kind, dict) and kind.get('kind') == 'text' and kind.get('data', '').isdigit():
                value = kind['data']
            else:
                raise RuntimeError('invalid Japanese Sums answer')
            result[y // 2][x // 2] = value
    return result


def fileio(p, ans):
    text = nonogram.fileio(Puzzle('nonogram', p.rows, p.cols, cells=p.borders), ans)
    return text.replace(f'pzprv3\nnonogram\n{p.rows}\n{p.cols}\n', f'pzprv3\njapanesesums\n{p.rows}\n{p.cols}\n{p.rule_flag}\n', 1)
