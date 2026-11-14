"""Outside-clue Latin-square puzzles and their native pzpr state."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle


def _numbers(body, length):
    values = []
    i = 0
    while len(values) < length and i < len(body):
        ch = body[i]
        if 'g' <= ch <= 'z':
            values.extend([None] * (ord(ch) - ord('g') + 1))
            i += 1
        elif ch in '0123456789abcdef':
            values.append(int(ch, 16))
            i += 1
        elif ch == '-' and len(body[i + 1:i + 3]) == 2 and all(c in '0123456789abcdef' for c in body[i + 1:i + 3]):
            values.append(int(body[i + 1:i + 3], 16))
            i += 3
        else:
            raise ValueError('cspuz outside clues require numbers 0–255')
    if len(values) != length:
        raise ValueError('invalid outside clues')
    return values, body[i:]


class OutsideNumberAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) not in (4, 5) or parts[0] != self.name or not parts[1].isdigit() or not parts[2].isdigit():
            raise ValueError('invalid outside-number puzzle path')
        pid, w, h = parts[0], int(parts[1]), int(parts[2])
        if w < 2 or h < 2 or (pid != 'easyasabc' and w != h):
            raise ValueError('cspuz requires valid dimensions and square Skyscrapers/Doppelblock boards')
        if pid == 'easyasabc':
            if len(parts) != 5 or not parts[3].isdigit() or not 1 <= int(parts[3]) <= min(w, h, 26):
                raise ValueError('invalid Easy as ABC letter count')
            limit, body, flag = int(parts[3]), parts[4], parts[3]
        else:
            if len(parts) != 4:
                raise ValueError('invalid outside-number puzzle variant')
            limit, body, flag = (w if pid == 'skyscrapers' else w - 2), parts[3], ''
        count = w + h if pid == 'doppelblock' else 2 * (w + h)
        outside, inside = _numbers(body, count)
        if any(v is not None and (v < (0 if pid == 'doppelblock' else 1) or v > (255 if pid == 'doppelblock' else limit)) for v in outside):
            raise ValueError('cspuz cannot represent these outside clues')
        cells = shading.decode_shading(f'nurikabe/{w}/{h}/{inside}').cells if inside else {}
        if any(not isinstance(v, int) or not 1 <= v <= limit for v in cells.values()):
            raise ValueError('cspuz cannot represent these cell clues')
        p = Puzzle(pid, h, w, cells, body=body, rule_flag=flag)
        p.outside = outside
        prefix = flag + '/' if flag else ''
        url = f'https://puzz.link/p?{pid}/{w}/{h}/{prefix}{body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) if v is not None else '.' for v in values) + ' \n'
        w, h = p.cols, p.rows
        outside = p.outside
        up = outside[:w]
        if p.puzzle_type == 'doppelblock':
            left = outside[w:]
            down = right = None
        else:
            down, left, right = outside[w:2*w], outside[2*w:2*w+h], outside[2*w+h:]
        values = [['.'] * w for _ in range(h)]
        for (r, c), v in p.cells.items():
            values[r][c] = 'q' + str(v)
        for item in board['data']:
            if item['color'] != 'green':
                continue
            r, c = item['y'] // 2 - 1, item['x'] // 2 - 1
            kind = item['item']
            if isinstance(kind, dict):
                value = kind['data']
                if p.puzzle_type == 'easyasabc':
                    value = ord(value) - ord('A') + 1
            elif p.puzzle_type == 'doppelblock':
                value = {'block': '-', 'circle': '+'}[kind]
            else:
                value = '-'
            values[r][c] = value
        out = [f'pzprv3\n{p.puzzle_type}\n{h}\n{w}\n']
        if p.rule_flag:
            out.append(p.rule_flag + '\n')
        out.append(row([None] + up + ([None] if down is not None else [])))
        for r in range(h):
            out.append(row([left[r]] + values[r] + ([right[r]] if right is not None else [])))
        if down is not None:
            out.append(row([None] + down + [None]))
        return ''.join(out)
