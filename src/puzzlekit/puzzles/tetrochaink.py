"""Tetro Chain-K dot clues and shaded cells."""
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle
from puzzlekit._adapters import regions, shading


class TetrochainKAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != self.name or not all(s.isdigit() for s in parts[1:3]):
            raise ValueError('invalid dot-clue puzzle path')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('Tetro Chain-K requires at least two rows and columns')
        size = (2*h-1) * (2*w-1)
        packed = shading.decode_shading(f'nurikabe/{(size+1)//2}/1/{parts[3]}')
        if any(not isinstance(v, int) or v > 15 for v in packed.cells.values()):
            raise ValueError('invalid Tetro Chain-K dots')
        digits = []
        for i in range((size+1)//2):
            value = packed.cells.get((0, i), 0)
            digits.extend((value // 4, value % 4))
        if digits[size-1] or digits[size]:
            raise ValueError('the backend cannot preserve the bottom-right dot')
        if self.name == 'tetrochaink' and not any(v in (1, 2) for v in digits[:size]):
            raise ValueError('a black or gray dot is required to exclude empty shading')
        if self.name == 'sansaroad' and any(v > 1 for i, v in enumerate(digits[:size]) if (i // (2*w-1)) % 2 == 0 and (i % (2*w-1)) % 2 == 0):
            raise ValueError('Sansa Road cell clues must be triangles')
        p = Puzzle(self.name, h, w, {divmod(i, 2*w-1): v for i, v in enumerate(digits[:size]) if v}, body=parts[3])
        url = f'https://puzz.link/p?{self.name}/{w}/{h}/{p.body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(values) + ' \n'
        out = [f'pzprv3\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n']
        out.extend(''.join(str(p.cells.get((r, c), '.')) for c in range(2*p.cols-1)) + '\n' for r in range(2*p.rows-1))
        # The renderer omits white cell facts beneath a dot.
        ans = regions.answer(p, {'data': [{**i, 'item': 'block' if i['item'] == 'fill' else i['item']} for i in board['data']]}, status)
        for r, line in enumerate(ans):
            out.append(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]))
        return ''.join(out)


ADAPTER = TetrochainKAdapter('tetrochaink', ('tetrochaink',), 'tetrochaink')
