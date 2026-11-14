"""Double Choco cell colors, clues, and answer borders."""
from puzzlekit._adapters import partition, shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'dbchoco' or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError('invalid Double Choco path')
    w, h, body = int(parts[1]), int(parts[2]), parts[3]
    if w < 2 or h < 2:
        raise ValueError('cspuz Double Choco requires at least two rows and columns')
    count = (w * h + 4) // 5
    color_body = body[:count]
    if len(color_body) != count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in color_body):
        raise ValueError('invalid Double Choco colors')
    bits = [(int(ch, 36) >> shift) & 1 for ch in color_body for shift in range(4, -1, -1)]
    if any(bits[w * h:]):
        raise ValueError('nonempty Double Choco padding')
    colors = {divmod(i, w): bit for i, bit in enumerate(bits[:w * h]) if bit}
    clues = shading.decode_shading(f'nurikabe/{w}/{h}/{body[count:]}').cells
    if any(v != '?' and (v == 0 or v >= 4096) for v in clues.values()):
        raise ValueError('cspuz Double Choco supports positive clues up to 4095 and ?')
    return Puzzle('dbchoco', h, w, clues, colors, body=body[:count])


def encode(p):
    clue_body = shading.encode_shading(Puzzle('nurikabe', p.rows, p.cols, p.cells)).split('?', 1)[1].split('/', 3)[3].rstrip('/')
    body = p.body + clue_body
    return f'https://puzz.link/p?dbchoco/{p.cols}/{p.rows}/{body}' + ('/' if body.endswith('.') else '')


def answer(p, board, status):
    return partition.answer(p, board, status)


def fileio(p, ans):
    def row(values): return ' '.join(str(v) for v in values) + ' \n'
    vertical, horizontal, _ = ans
    out = [f'pzprv3\ndbchoco\n{p.rows}\n{p.cols}\n']
    for r in range(p.rows):
        cells = []
        for c in range(p.cols):
            clue = p.cells.get((r, c))
            token = '' if clue is None else '0' if clue == '?' else str(clue)
            token = ('-' if (r, c) in p.borders else '') + token
            cells.append(token or '.')
        out.append(row(cells))
    for lines in (vertical, horizontal):
        out.extend(row([1 if x is True else -1 if x is False else 0 for x in line]) for line in lines)
    return ''.join(out)
