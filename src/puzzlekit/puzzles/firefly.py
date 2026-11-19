"""Hotaru Beam arrows and connecting lines."""
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import shading, yajilin


class FireflyAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if len(parts) != 4 or parts[0] != 'firefly':
            raise ValueError('unsupported Firefly path or rule variant')
        p = yajilin.decode('/'.join(['yajilin', *parts[1:]]))
        if not p.cells or any(d == 0 or (v != '?' and v >= 256) for d, v in p.cells.values()):
            raise ValueError('cspuz Firefly requires directed arrows numbered 0–255 or ?')
        p.puzzle_type = 'firefly'
        url = 'https://puzz.link/p?' + '/'.join(parts) + ('/' if parts[-1].endswith('.') else '')
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        out = [f'pzprv3\nfirefly\n{p.rows}\n{p.cols}\n']
        for r in range(p.rows):
            cells = []
            for c in range(p.cols):
                clue = p.cells.get((r, c))
                cells.append('.' if clue is None else f'{clue[0]},{"-" if clue[1] == "?" else clue[1]}')
            out.append(row(cells))
        vertical = [[0] * (p.cols - 1) for _ in range(p.rows)]
        horizontal = [[0] * p.cols for _ in range(p.rows - 1)]
        for item in board['data']:
            if item['color'] != 'green': continue
            y, x, kind = item['y'], item['x'], item['item']
            if kind not in ('boldWall', 'cross'):
                raise RuntimeError('unexpected Firefly answer')
            value = 1 if kind == 'boldWall' else -1
            if y % 2 == 0 and x % 2 == 1:
                vertical[y // 2][x // 2] = value
            elif y % 2 == 1 and x % 2 == 0:
                horizontal[y // 2][x // 2] = value
            else:
                raise RuntimeError('invalid Firefly answer coordinate')
        out.extend(row(line) for line in vertical)
        out.extend(row(line) for line in horizontal)
        return ''.join(out)


ADAPTER = FireflyAdapter('firefly', ('firefly',), 'firefly')
