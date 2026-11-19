"""Barns ice cells, walls and loop edges."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters import extended, shading


class BarnsAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'barns' or not all(x.isdigit() for x in parts[1:3]):
            raise ValueError('invalid Barns path')
        w,h = map(int, parts[1:3])
        if min(w,h) < 2:
            raise ValueError('Barns requires at least two rows and columns')
        body = parts[3]
        n = (w*h+4)//5
        border_count = (h*(w-1)+4)//5 + ((h-1)*w+4)//5
        if len(body) != n + border_count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body):
            raise ValueError('invalid Barns ice cells or walls')
        bits = [bool(int(ch,32) & (1 << (4-j))) for ch in body[:n] for j in range(5)]
        if any(bits[w*h:]):
            raise ValueError('Barns ice cells exceed grid')
        cells = {divmod(i,w): 1 for i, v in enumerate(bits[:w*h]) if v}
        borders, _ = BorderCodec().decode(body[n:], h, w)
        p = Puzzle('barns', h, w, cells, borders, body=body)
        url = f'https://puzz.link/p?barns/{w}/{h}/{body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        ans = extended.answer(replace(p, puzzle_type='mashu'), board, status)
        h,w = p.rows,p.cols
        out = [f'pzprv3\nbarns\n{h}\n{w}\n']
        out.extend(row([1 if (r,c) in p.cells else '.' for c in range(w)]) for r in range(h))
        out.extend(row([int(r*(w-1)+c in p.borders) for c in range(w-1)]) for r in range(h))
        out.extend(row([int(h*(w-1)+r*w+c in p.borders) for c in range(w)]) for r in range(h-1))
        for lines in (ans['vertical'], ans['horizontal']):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
        return ''.join(out)


ADAPTER = BarnsAdapter('barns', ('barns',), 'barns')
