"""All or Nothing room clues and cell-loop edges."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import doubleback, regions, shading


class NothingAdapter(Adapter):
    def parse(self, source):
        path = shading.puzzle_path(source)
        if not path.startswith('nothing/'):
            raise ValueError('invalid All or Nothing path')
        p = regions.decode_regions('lits/' + path[len('nothing/'):])
        if not p.borders:
            raise ValueError('a room boundary is required to exclude an empty loop')
        p.puzzle_type = 'nothing'
        url = regions.encode_regions(replace(p, puzzle_type='lits')).replace('?lits/', '?nothing/', 1)
        return p, url, url

    def fileio(self, p, board, status):
        return doubleback.fileio(p, doubleback.answer(p, board, status))


ADAPTER = NothingAdapter('nothing', ('nothing',), 'nothing')
