"""Litherslink clues and vertex-grid lines."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import extended, shading


class LitherslinkAdapter(Adapter):
    def parse(self, source):
        path = shading.puzzle_path(source)
        if not path.startswith('lither/'):
            raise ValueError('invalid Litherslink path')
        p = extended.decode_extended('slither/' + path[len('lither/'):])
        if min(p.rows, p.cols) < 2:
            raise ValueError('Litherslink requires at least two rows and columns')
        p.puzzle_type = 'lither'
        url = extended.encode_extended(replace(p, puzzle_type='slither')).replace('?slither/', '?lither/', 1)
        return p, url, url

    def fileio(self, p, board, status):
        base = replace(p, puzzle_type='slither')
        return extended.fileio(base, extended.answer(base, board, status)).replace('\nslither\n', '\nlither\n', 1)


ADAPTER = LitherslinkAdapter('lither', ('lither',), 'lither')
