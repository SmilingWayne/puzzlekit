"""Detour: a full cell loop with a count of turns in each room."""
from dataclasses import replace

from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import extended, regions, shading


class DetourAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if len(parts) != 4 or parts[0] != 'detour':
            raise ValueError('unsupported Detour path or rule variant')
        puzzle = regions.decode_regions('/'.join(['heyawake', *parts[1:]]))
        if any(isinstance(v, int) and v >= 4096 for v in puzzle.cells.values()):
            raise ValueError('cspuz cannot represent this room clue')
        puzzle.puzzle_type = 'detour'
        url = regions.encode_regions(replace(puzzle, puzzle_type='heyawake')).replace('?heyawake/', '?detour/', 1)
        return puzzle, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        h, w = p.rows, p.cols
        answer = extended.answer(replace(p, puzzle_type='mashu'), board, status)
        n = h * (w - 1)
        out = [f'pzprv3.2\ndetour\n{h}\n{w}\n']
        out.extend(row([int(r * (w - 1) + c in p.borders) for c in range(w - 1)]) for r in range(h))
        out.extend(row([int(n + r * w + c in p.borders) for c in range(w)]) for r in range(h - 1))
        out.extend(row(['-' if p.cells.get((r, c)) == '?' else p.cells.get((r, c), '.') for c in range(w)]) for r in range(h))
        for lines in (answer['vertical'], answer['horizontal']):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
        out.extend(row([0] * w) for _ in range(h))
        return ''.join(out)


ADAPTER = DetourAdapter('detour', ('detour',), 'detour')
