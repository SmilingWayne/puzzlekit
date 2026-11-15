"""Kurarin dot clues, cell shading and a loop."""
from puzzlekit._adapters import packed, regions
from puzzlekit.puzzles.tetrochaink import TetrochainKAdapter


class KurarinAdapter(TetrochainKAdapter):
    def parse(self, source):
        p, url, backend = super().parse(source)
        if not any(v in (2, 3) for v in p.cells.values()):
            raise ValueError('Kurarin needs a gray or white dot to exclude an empty loop')
        return p, url, backend

    def fileio(self, p, board, status):
        def row(values): return ' '.join(map(str, values)) + ' \n'
        cells = {'data': [{**i, 'item': 'block' if i['item'] == 'fill' else i['item']}
                          for i in board['data'] if i['color'] != 'green' or i['item'] in ('fill', 'dot')]}
        lines = {'data': [i for i in board['data'] if i['color'] != 'green' or i['item'] in ('line', 'cross')]}
        ans = regions.answer(p, cells, status)
        edges = packed.answer(p, lines, status)
        out = [f'pzprv3\nkurarin\n{p.rows}\n{p.cols}\n']
        out.extend(''.join(str(p.cells.get((r,c), '.')) for c in range(2*p.cols-1)) + '\n' for r in range(2*p.rows-1))
        out.extend(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]) for line in ans)
        for line_group in edges:
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in line_group)
        return ''.join(out)


ADAPTER = KurarinAdapter('kurarin', ('kurarin',), 'kurarin')
