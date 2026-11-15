"""Snake endpoint clues, outside counts and shaded cells."""
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle
from puzzlekit._adapters import shading
from puzzlekit._adapters.outside_numbers import _numbers


class SnakeAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'snake' or not all(s.isdigit() for s in parts[1:3]):
            raise ValueError('invalid Snake path')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('Snake requires at least two rows and columns')
        body = parts[3]
        count = (w * h + 2) // 3
        packed = body[:count]
        if len(packed) != count or any(ch not in '0123456789abcdefghijklmnopq' for ch in packed):
            raise ValueError('invalid Snake circles')
        digits = [n for ch in packed for n in (int(ch, 36) // 9, int(ch, 36) // 3 % 3, int(ch, 36) % 3)]
        if any(digits[w*h:]):
            raise ValueError('Snake circles exceed grid')
        outside, rest = _numbers(body[count:], w + h)
        if rest or any(v is not None and v > (h if i < w else w) for i, v in enumerate(outside)):
            raise ValueError('invalid Snake outside clues')
        p = Puzzle('snake', h, w, {divmod(i, w): n for i, n in enumerate(digits[:w*h]) if n}, body=body)
        p.outside = outside
        url = f'https://puzz.link/p?snake/{w}/{h}/{body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        marks = [[0] * p.cols for _ in range(p.rows)]
        for item in board['data']:
            if item['color'] != 'green':
                continue
            y, x, kind = item['y'], item['x'], item['item']
            r, c = y // 2 - 1, x // 2 - 1
            if kind not in ('block', 'dot') or not (0 <= r < p.rows and 0 <= c < p.cols):
                raise RuntimeError('invalid Snake answer')
            marks[r][c] = 4 if kind == 'block' else 8
        out = [f'pzprv3\nsnake\n{p.rows}\n{p.cols}\n']
        out.append(row(['.'] + [v if v is not None else '.' for v in p.outside[:p.cols]]))
        for r in range(p.rows):
            left = p.outside[p.cols + r]
            out.append(row([left if left is not None else '.'] + [p.cells.get((r, c), 0) + marks[r][c] for c in range(p.cols)]))
        return ''.join(out)


ADAPTER = SnakeAdapter('snake', ('snake',), 'snake')
