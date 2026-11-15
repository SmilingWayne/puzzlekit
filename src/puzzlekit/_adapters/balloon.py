"""Balloon Box room partitions and connecting lines."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) > 4 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    flag = len(parts) == 5 and parts[1] == 'a'
    if flag:
        parts.pop(1)
    if len(parts) != 4 or parts[0] != 'balloon' or not all(v.isdigit() for v in parts[1:3]):
        raise ValueError('invalid Balloon Box path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 2:
        raise ValueError('cspuz Balloon Box requires at least two rows and columns')
    body = parts[3]
    count = (h*w + 4) // 5
    bits = body[:count]
    if len(bits) != count or any(c not in '0123456789abcdefghijklmnopqrstuv' for c in bits):
        raise ValueError('invalid Balloon Box region cells')
    values = [bool(int(c, 32) & (1 << (4-j))) for c in bits for j in range(5)]
    if any(values[h*w:]):
        raise ValueError('region cells exceed grid')
    holes = {divmod(i, w): True for i, v in enumerate(values[:h*w]) if v}
    cells = shading.decode_shading(f'nurikabe/{w}/{h}/{body[count:]}').cells
    if not cells or any(isinstance(v, int) and v >= 4096 for v in cells.values()):
        raise ValueError('Balloon Box requires clues below 4096 or ?')
    if any(k in holes for k in cells):
        raise ValueError('number clues cannot overlap region cells')
    return Puzzle('balloon', h, w, cells=cells, holes=holes, body=body, rule_flag='a' if flag else '')


def encode(p):
    flag = 'a/' if p.rule_flag else ''
    return f'https://puzz.link/p?balloon/{flag}{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    vertical = [[[0, 0] for _ in range(p.cols-1)] for _ in range(p.rows)]
    horizontal = [[[0, 0] for _ in range(p.cols)] for _ in range(p.rows-1)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if y % 2 == 1 and x % 2 == 0:
                r, c, target = y//2, x//2-1, vertical
                a, b = (r,c), (r,c+1)
            elif y % 2 == 0 and x % 2 == 1:
                r, c, target = y//2-1, x//2, horizontal
                a, b = (r,c), (r+1,c)
            else:
                raise RuntimeError('invalid Balloon Box answer coordinate')
            if kind == 'boldWall':
                target[r][c][0] = 1
            elif kind == 'line':
                target[r][c][1] = 1
            elif kind == 'cross':
                if a in p.holes and b in p.holes:
                    target[r][c][0] = -1
                else:
                    target[r][c][1] = -1
            else:
                raise RuntimeError('invalid Balloon Box answer')
    return vertical, horizontal


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nballoon\n{p.rows}\n{p.cols}\n']
    if p.rule_flag:
        out.append('a\n')
    out.extend(row(['#' if (r,c) in p.holes else '-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(p.cols)]) for r in range(p.rows))
    for i in (0, 1):
        for lines in ans:
            out.extend(row([v[i] for v in line]) for line in lines)
    return ''.join(out)
