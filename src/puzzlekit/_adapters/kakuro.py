"""Kakuro sum clues and cell numbers in native pzpr state."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle


def _number(ch):
    if ch == '-': return -1
    if '0' <= ch <= '9': return int(ch)
    if 'a' <= ch <= 'j': return ord(ch) - ord('a') + 10
    if 'A' <= ch <= 'Z': return ord(ch) - ord('A') + 20
    raise ValueError('Kakuro sums must be 0–45 or empty clues')


class KakuroAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'kakuro' or not parts[1].isdigit() or not parts[2].isdigit():
            raise ValueError('invalid Kakuro path')
        w, h, body = int(parts[1]), int(parts[2]), parts[3]
        if min(w, h) < 1:
            raise ValueError('invalid Kakuro dimensions')
        pos = i = 0
        cells = {}
        while pos < w * h and i < len(body):
            ch = body[i]
            if 'k' <= ch <= 'z':
                pos += ord(ch) - ord('k') + 1
                i += 1
            elif ch == '.':
                cells[divmod(pos, w)] = (-1, -1)
                pos += 1
                i += 1
            else:
                if i + 1 >= len(body): raise ValueError('incomplete Kakuro cell clue')
                down, right = _number(ch), _number(body[i + 1])
                cells[divmod(pos, w)] = (down, right)
                pos += 1
                i += 2
        if pos != w * h:
            raise ValueError('invalid Kakuro grid data')
        needed = sum((0, c) not in cells for c in range(w)) + sum((r, 0) not in cells for r in range(h))
        if len(body) - i != needed:
            raise ValueError('invalid Kakuro outside clues')
        nums = iter(_number(ch) for ch in body[i:])
        up = [next(nums) if (0, c) not in cells else -1 for c in range(w)]
        left = [next(nums) if (r, 0) not in cells else -1 for r in range(h)]
        p = Puzzle('kakuro', h, w, cells, body=body)
        p.up, p.left = up, left
        url = f'https://puzz.link/p?kakuro/{w}/{h}/{body}'
        # pzpr treats zero as an unspecified sum, while cspuz constrains it.
        backend = f'https://puzz.link/p?kakuro/{w}/{h}/{body.replace("0", "-")}'
        return p, url, backend

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        h, w = p.rows, p.cols
        out = [f'pzprv3\nkakuro\n{h}\n{w}\n', row([0] + p.up)]
        for r in range(h):
            values = []
            for c in range(w):
                clue = p.cells.get((r, c))
                values.append('.' if clue is None else f'{clue[1]},{clue[0]}')
            out.append(row([p.left[r]] + values))
        answer = [['.'] * w for _ in range(h)]
        for item in board['data']:
            if item['color'] == 'green':
                answer[item['y'] // 2 - 1][item['x'] // 2 - 1] = item['item']['data']
        out.extend(row(line) for line in answer)
        return ''.join(out)
