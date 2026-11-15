"""Hebi-Ichigo arrow clues and snake numbers."""
from puzzlekit._adapters import shading, yajilin


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'hebi':
        raise ValueError('invalid Hebi-Ichigo path')
    p = yajilin.decode('/'.join(['yajilin', *parts[1:]]))
    if any(v != '?' and v >= 256 for _, v in p.cells.values()):
        raise ValueError('cspuz Hebi-Ichigo supports arrow numbers up to 255')
    if not any(d and isinstance(v, int) and v > 0 for d, v in p.cells.values()):
        raise ValueError('a positive arrow clue is required to ensure a snake')
    p.puzzle_type = 'hebi'
    p.body = parts[3]
    return p


def encode(p):
    return f'https://puzz.link/p?hebi/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    result = [[None] * p.cols for _ in range(p.rows)]
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            if y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                raise RuntimeError('invalid Hebi-Ichigo answer coordinate')
            if kind == 'dot':
                value = '+'
            elif isinstance(kind, dict) and kind.get('kind') == 'text' and kind.get('data') in ('1', '2', '3', '4', '5'):
                value = kind['data']
            else:
                raise RuntimeError('invalid Hebi-Ichigo answer')
            result[y // 2][x // 2] = value
    return result


def fileio(p, answers):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    out = [f'pzprv3\nhebi\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        line = []
        for c in range(p.cols):
            clue = p.cells.get((r, c))
            line.append('.' if clue is None else f'{clue[0]},{"-" if clue[1] == "?" else clue[1]}')
        out.append(row(line))
    out.extend(row([v if v is not None else '.' for v in line]) for line in answers)
    return ''.join(out)
