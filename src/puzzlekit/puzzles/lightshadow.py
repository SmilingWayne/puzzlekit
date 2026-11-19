"""Light and Shadow clue colors and answer shading."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle


class LightShadowAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'lightshadow':
            raise ValueError('invalid Light and Shadow path')
        p = shading.decode_shading('/'.join(['nurikabe', *parts[1:]]))
        if p.rows < 2 or p.cols < 2 or not p.cells:
            raise ValueError('cspuz Light and Shadow requires a clue and at least two rows and columns')
        if any(v == '?' or v >= 4096 for v in p.cells.values()):
            raise ValueError('cspuz cannot represent this Light and Shadow clue')
        p.puzzle_type = 'lightshadow'
        p.body = parts[3]
        url = f'https://puzz.link/p?lightshadow/{p.cols}/{p.rows}/{p.body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        marks = [[0] * p.cols for _ in range(p.rows)]
        if status != 'no_solution':
            for item in board['data']:
                if item['color'] != 'green':
                    continue
                y, x, kind = item['y'], item['x'], item['item']
                if kind not in ('block', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                    raise RuntimeError('unexpected Light and Shadow answer')
                marks[y // 2][x // 2] = 1 if kind == 'block' else 2
        out = [f'pzprv3\nlightshadow\n{p.rows}\n{p.cols}\n']
        for r in range(p.rows):
            out.append(row(['.' if (r, c) not in p.cells else f"{p.cells[r,c] % 2},{p.cells[r,c] // 2 or -2}" for c in range(p.cols)]))
        out.extend(row(line) for line in marks)
        return ''.join(out)


ADAPTER = LightShadowAdapter('lightshadow', ('lightshadow',), 'lightshadow')
