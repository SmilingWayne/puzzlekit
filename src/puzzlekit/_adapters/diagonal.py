"""Number4 clues and diagonal answers for Slant and Shakashaka."""
from puzzlekit._adapters import extended, shading
from puzzlekit._adapters.model import Puzzle


def _requires_triangle(cells, h, w):
    if any(isinstance(v, int) and v > 0 for v in cells.values()):
        return True
    # Without triangles, each connected white area must itself be rectangular.
    remaining = {(r, c) for r in range(h) for c in range(w) if (r, c) not in cells}
    while remaining:
        start = remaining.pop()
        component, stack = {start}, [start]
        while stack:
            r, c = stack.pop()
            for point in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    stack.append(point)
        height = max(r for r, _ in component) - min(r for r, _ in component) + 1
        width = max(c for _, c in component) - min(c for _, c in component) + 1
        if len(component) != height * width:
            return True
    return False


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] not in {'gokigen', 'shakashaka'}:
        raise ValueError('unsupported diagonal puzzle or rule variant')
    pid = parts[0]
    if not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid puzzle dimensions')
    w, h = int(parts[1]), int(parts[2])
    if w < 2 or h < 2:
        raise ValueError('cspuz diagonal puzzles require at least two rows and columns')
    offset = 1 if pid == 'gokigen' else 0
    tmp = extended.decode_extended(f'slither/{w + offset}/{h + offset}/{parts[3]}')
    if pid == 'shakashaka' and not _requires_triangle(tmp.cells, h, w):
        raise ValueError('cspuz Shakashaka may count an answer without triangles')
    return Puzzle(pid, h, w, tmp.cells)


def encode(p):
    offset = 1 if p.puzzle_type == 'gokigen' else 0
    tmp = Puzzle('slither', p.rows + offset, p.cols + offset, p.cells)
    body = extended.encode_extended(tmp).split('?', 1)[1].split('/', 3)[3]
    return f'https://puzz.link/p?{p.puzzle_type}/{p.cols}/{p.rows}/{body}'


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status == 'no_solution':
        return result
    mapping = ({'backslash': '1', 'slash': '2'} if p.puzzle_type == 'gokigen' else
               {'aboloUpperLeft': '5', 'aboloUpperRight': '4',
                'aboloLowerLeft': '2', 'aboloLowerRight': '3', 'dot': '+'})
    for item in board['data']:
        if item['color'] != 'green':
            continue
        y, x, kind = item['y'], item['x'], item['item']
        if kind not in mapping or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
            raise RuntimeError('invalid diagonal answer')
        if p.puzzle_type == 'shakashaka' and (y // 2, x // 2) in p.cells:
            raise RuntimeError('answer on a Shakashaka clue')
        result[y // 2][x // 2] = mapping[kind]
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(x) for x in values) + ' \n'
    out = [f'pzprv3\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n']
    offset = 1 if p.puzzle_type == 'gokigen' else 0
    for r in range(p.rows + offset):
        line = []
        for c in range(p.cols + offset):
            clue = p.cells.get((r, c))
            line.append('.' if clue is None else ('-' if offset else '5') if clue == '?' else clue)
        out.append(row(line))
    out.extend(row([v if v is not None else '.' for v in line]) for line in answers)
    return ''.join(out)
