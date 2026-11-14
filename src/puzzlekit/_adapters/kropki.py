"""Kropki border circles and cell-number answers."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.codecs import Number3Codec
from puzzlekit._adapters.model import Puzzle


class KropkiAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'kropki' or not parts[1].isdigit() or not parts[2].isdigit():
            raise ValueError('invalid Kropki path')
        w, h, body = int(parts[1]), int(parts[2]), parts[3]
        if w != h or w < 2:
            raise ValueError('cspuz Kropki requires a square board at least 2×2')
        count = h * (w - 1) + (h - 1) * w
        if len(body) != (count + 2) // 3 or any(c not in '0123456789abcdefghijklmnopq' for c in body):
            raise ValueError('invalid Kropki circle data')
        values = Number3Codec().decode(body)
        if any(values[count:]):
            raise ValueError('invalid Kropki circle padding')
        p = Puzzle('kropki', h, w, borders={i: v for i, v in enumerate(values[:count]) if v})
        url = f'https://puzz.link/p?kropki/{w}/{h}/{body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        h, w = p.rows, p.cols
        out = [f'pzprv3\nkropki\n{h}\n{w}\n']
        out.extend(row([p.borders.get(r * (w - 1) + c, 0) for c in range(w - 1)]) for r in range(h))
        start = h * (w - 1)
        out.extend(row([p.borders.get(start + r * w + c, 0) for c in range(w)]) for r in range(h - 1))
        answer = [['.'] * w for _ in range(h)]
        for item in board['data']:
            if item['color'] == 'green':
                answer[item['y'] // 2][item['x'] // 2] = item['item']['data']
        out.extend(row(line) for line in answer)
        return ''.join(out)
