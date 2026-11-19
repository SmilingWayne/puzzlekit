"""Reflect Link triangle and crossing clues with cell-loop answers."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import extended, shading
from puzzlekit._adapters.model import Puzzle


class ReflectAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'reflect' or not all(x.isdigit() for x in parts[1:3]):
            raise ValueError('unsupported Reflect Link path or rule variant')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('cspuz Reflect Link requires at least 2x2')
        body = parts[3]
        cells = {}; pos = i = 0
        while i < len(body):
            c = body[i]
            if 'a' <= c <= 'z':
                pos += ord(c) - ord('a') + 1
                i += 1
                continue
            if pos >= w * h:
                raise ValueError('puzzle data exceeds grid')
            if c == '5':
                cells[divmod(pos, w)] = '+'
                i += 1
            elif c in '1234' and i + 1 < len(body) and body[i + 1] in '0123456789abcdef':
                n = int(body[i + 1], 16)
                cells[divmod(pos, w)] = c + (str(n) if n else '')
                i += 2
            else:
                raise ValueError('cspuz Reflect Link supports triangle numbers 0–15')
            pos += 1
        if pos > w * h or not cells:
            raise ValueError('cspuz Reflect Link requires a clue and valid grid data')
        p = Puzzle('reflect', h, w, cells=cells)
        url = 'https://puzz.link/p?' + '/'.join(parts)
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        a = extended.answer(replace(p, puzzle_type='mashu'), board, status)
        out = [f'pzprv3\nreflect\n{p.rows}\n{p.cols}\n']
        out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
        for lines in (a['vertical'], a['horizontal']):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
        return ''.join(out)


ADAPTER = ReflectAdapter('reflect', ('reflect',), 'reflect')
