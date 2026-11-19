"""No Three dot clues and shaded cells."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle


class NoThreeAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'nothree' or not all(x.isdigit() for x in parts[1:3]):
            raise ValueError('invalid No Three path')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('cspuz No Three requires at least two rows and columns')
        dw, size = 2 * w - 1, (2 * w - 1) * (2 * h - 1)
        dots, pos = {}, 0
        for ch in parts[3]:
            if pos >= size:
                raise ValueError('No Three clues exceed grid')
            if ch in '02468ace':
                dots[divmod(pos, dw)] = 1
                pos += int(ch, 16) // 2 + 1
            elif ch in 'ghijklmnopqrstuvwxyz':
                pos += ord(ch) - ord('g') + 1
                if pos > size:
                    raise ValueError('No Three clues exceed grid')
            else:
                raise ValueError('cspuz No Three only supports ordinary dot clues')
        if not dots:
            raise ValueError('cspuz No Three requires a dot to ensure shaded cells')
        p = Puzzle('nothree', h, w, dots, body=parts[3])
        url = f'https://puzz.link/p?nothree/{w}/{h}/{p.body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(values) + ' \n'
        marks = [['.'] * p.cols for _ in range(p.rows)]
        if status != 'no_solution':
            for item in board['data']:
                if item['color'] != 'green':
                    continue
                y, x, kind = item['y'], item['x'], item['item']
                if kind not in ('block', 'dot') or y % 2 != 1 or x % 2 != 1 or not (0 <= y // 2 < p.rows and 0 <= x // 2 < p.cols):
                    raise RuntimeError('unexpected No Three answer')
                marks[y // 2][x // 2] = '#' if kind == 'block' else '+'
        out = [f'pzprv3\nnothree\n{p.rows}\n{p.cols}\n']
        out.extend(''.join('1' if (r,c) in p.cells else '.' for c in range(2*p.cols-1)) + '\n' for r in range(2*p.rows-1))
        out.extend(row(line) for line in marks)
        return ''.join(out)


ADAPTER = NoThreeAdapter('nothree', ('nothree',), 'nothree')
