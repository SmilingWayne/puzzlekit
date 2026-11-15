"""Nurikabe Loop numbers and cell-loop edges."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import extended, shading


class NuriloopAdapter(Adapter):
    def parse(self, source):
        path = shading.puzzle_path(source)
        if not path.startswith('nuriloop/'):
            raise ValueError('unsupported Nurikabe Loop path')
        p = shading.decode_shading('nurikabe/' + path[len('nuriloop/'):])
        if min(p.rows, p.cols) < 2 or any(not isinstance(v, int) or not 0 < v < 4096 for v in p.cells.values()):
            raise ValueError('Nurikabe Loop requires clues 1–4095 and at least 2x2')
        if sum(p.cells.values()) >= p.rows * p.cols:
            raise ValueError('clues must force a nonempty loop')
        p.puzzle_type = 'nuriloop'
        url = shading.encode_shading(replace(p, puzzle_type='nurikabe')).replace('?nurikabe/', '?nuriloop/', 1)
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        ans = extended.answer(replace(p, puzzle_type='mashu'), board, status)
        out = [f'pzprv3\nnuriloop\n{p.rows}\n{p.cols}\n']
        out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
        out.extend(row([0] * p.cols) for _ in range(p.rows))
        for lines in (ans['vertical'], ans['horizontal']):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
        return ''.join(out)


ADAPTER = NuriloopAdapter('nuriloop', ('nuriloop',), 'nuriloop')
