"""School Trip clues, shaded cells, and futon placements."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) != 4 or parts[0] != 'shugaku' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid School Trip path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz School Trip requires at least two rows and columns')
    cells, pos = {}, 0
    for ch in parts[3]:
        if ch in '012345':
            if pos >= h*w:
                raise ValueError('School Trip clues exceed grid')
            cells[divmod(pos, w)] = '?' if ch == '5' else int(ch)
            pos += 1
        elif ch in '6789abcdefghijklmnopqrstuvwxyz':
            pos += int(ch, 36) - 5
        else:
            raise ValueError('invalid School Trip clue')
        if pos > h*w:
            raise ValueError('School Trip clues exceed grid')
    return Puzzle('shugaku', h, w, cells=cells, body=parts[3])


def encode(p):
    return f'https://puzz.link/p?shugaku/{p.cols}/{p.rows}/{p.body}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    pillows = set()
    pairs = []
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if y % 2 == 1 and x % 2 == 1:
                r, c = y // 2, x // 2
                if kind == 'block':
                    result[r][c] = '#'
                elif kind == 'square':
                    pillows.add((r,c))
                    result[r][c] = 'a'
                elif kind != 'dot':
                    raise RuntimeError('invalid School Trip cell answer')
            elif kind == 'cross':
                if y % 2 == 1 and x % 2 == 0:
                    pairs.append(((y//2, x//2-1), (y//2, x//2), 'e', 'd', 'j', 'i'))
                elif y % 2 == 0 and x % 2 == 1:
                    pairs.append(((y//2-1, x//2), (y//2, x//2), 'c', 'b', 'h', 'g'))
                else:
                    raise RuntimeError('invalid School Trip border answer')
            elif kind != 'boldWall':
                raise RuntimeError('invalid School Trip answer')
        for a, b, pillow_a, pillow_b, other_a, other_b in pairs:
            if a in pillows:
                result[a[0]][a[1]], result[b[0]][b[1]] = pillow_a, other_b
            elif b in pillows:
                result[a[0]][a[1]], result[b[0]][b[1]] = other_a, pillow_b
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nshugaku\n{p.rows}\n{p.cols}\n']
    out.extend(row(['5' if p.cells.get((r,c)) == '?' else p.cells[(r,c)] if (r,c) in p.cells else answers[r][c] or '.' for c in range(p.cols)]) for r in range(p.rows))
    return ''.join(out)
