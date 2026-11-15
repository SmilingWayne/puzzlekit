"""Tetro Chain-Y arrow clues and shading."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import regions, yajilin, yajikazu


class TetrochainAdapter(Adapter):
    def parse(self, source):
        path = yajikazu.puzzle_path(source)
        if not path.startswith('tetrochain/'):
            raise ValueError('unsupported Tetro Chain path')
        p = yajilin.decode('yajilin/' + path[len('tetrochain/'):])
        forces_shading = False
        for (r, c), (direction, value) in p.cells.items():
            if direction not in (1, 2, 3, 4) or value != '?' and value >= 256:
                raise ValueError('Tetro Chain requires arrows numbered 0–255 or ?')
            inside = (direction == 1 and r > 0 or direction == 2 and r < p.rows - 1 or
                      direction == 3 and c > 0 or direction == 4 and c < p.cols - 1)
            if not inside and value not in (0, '?'):
                raise ValueError('positive arrows must point into the grid')
            forces_shading |= inside and isinstance(value, int) and value > 0
        if not forces_shading:
            raise ValueError('a positive arrow is required to exclude empty shading')
        p.puzzle_type = 'tetrochain'
        url = yajilin.encode(replace(p, puzzle_type='yajilin')).replace('?yajilin/', '?tetrochain/', 1)
        return p, url, url

    def fileio(self, p, board, status):
        return yajikazu.fileio(p, regions.answer(p, board, status)).replace('\nyajikazu\n', '\ntetrochain\n', 1)


ADAPTER = TetrochainAdapter('tetrochain', ('tetrochain',), 'tetrochain')
