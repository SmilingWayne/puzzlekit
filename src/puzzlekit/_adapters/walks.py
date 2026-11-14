"""Shared codecs for the ice, forest, water and morning walk puzzles."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import extended, shading


class WalkAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) == 6 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if not parts or parts[0] != self.name:
            raise ValueError('unsupported Walk puzzle')
        full = len(parts) == 5 and parts[1] == 'f'
        if full:
            parts.pop(1)
        if len(parts) != 4 or not all(x.isdigit() for x in parts[1:3]):
            raise ValueError('unsupported Walk puzzle path or rule variant')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('cspuz Walk puzzles require at least 2x2')
        body = parts[3]
        count = (w * h + 4) // 5
        packed = body[:count]
        if len(packed) != count or any(c not in '0123456789abcdefghijklmnopqrstuv' for c in packed):
            raise ValueError('invalid colored-cell data')
        bits = [int(c, 32) & (1 << (4 - j)) != 0 for c in packed for j in range(5)]
        if any(bits[h * w:]):
            raise ValueError('colored cells exceed grid')
        p = shading.decode_shading(f'nurikabe/{w}/{h}/{body[count:]}')
        if any(v == 0 or isinstance(v, int) and v >= 4096 for v in p.cells.values()):
            raise ValueError('cspuz Walk clues must be positive, below 4096 or ?')
        p.puzzle_type = self.name
        p.holes = {divmod(i, w): True for i, bit in enumerate(bits[:h * w]) if bit}
        if any(key in p.holes for key in p.cells):
            raise ValueError('colored cells cannot carry numbers in native pzpr FileIO')
        p.rule_flag = 'f' if full else ''
        flag = 'f/' if full else ''
        url = f'https://puzz.link/p?{p.puzzle_type}/{flag}{w}/{h}/{body}' + ('/' if body.endswith('.') else '')
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        a = extended.answer(replace(p, puzzle_type='mashu'), board, status)
        out = [f'pzprv3\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n']
        if p.rule_flag:
            out.append('f\n')
        out.extend(row(['#' if (r,c) in p.holes else '-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(p.cols)]) for r in range(p.rows))
        def mark(v): return 1 if v is True else -1 if v is False else 0
        out.extend(row([0] + [mark(v) for v in line] + [0]) for line in a['vertical'])
        out.append(row([0] * p.cols))
        out.extend(row([mark(v) for v in line]) for line in a['horizontal'])
        out.append(row([0] * p.cols))
        return ''.join(out)
