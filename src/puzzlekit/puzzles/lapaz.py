"""La Paz clues, region boundaries and shading."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import extended, regions, shading


class LapazAdapter(Adapter):
    def parse(self, source):
        path = shading.puzzle_path(source)
        if not path.startswith('lapaz/'):
            raise ValueError('invalid La Paz path')
        p = shading.decode_shading('nurikabe/' + path[len('lapaz/'):])
        if min(p.rows, p.cols) < 2 or any(isinstance(v, int) and v >= 4096 for v in p.cells.values()):
            raise ValueError('La Paz requires at least 2x2 and clues below 4096')
        p.puzzle_type = 'lapaz'
        url = shading.encode_shading(replace(p, puzzle_type='nurikabe')).replace('?nurikabe/', '?lapaz/', 1)
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        cell_items = [i for i in board['data'] if i['color'] != 'green' or i['item'] in ('block', 'dot')]
        border_items = [i for i in board['data'] if i['color'] != 'green' or i['item'] in ('boldWall', 'cross')]
        cells = regions.answer(p, {'data': cell_items}, status)
        borders = extended.answer(replace(p, puzzle_type='shikaku'), {'data': border_items}, status)
        out = [f'pzprv3\nlapaz\n{p.rows}\n{p.cols}\n']
        out.extend(row(['-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(p.cols)]) for r in range(p.rows))
        for lines in (borders['vertical'], borders['horizontal']):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
        out.extend(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]) for line in cells)
        return ''.join(out)


ADAPTER = LapazAdapter('lapaz', ('lapaz',), 'lapaz')
