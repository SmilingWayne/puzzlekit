"""Lohkous segment clues and partition boundaries."""
from puzzlekit._adapters import partition, shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle


class LohkousAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) != 4 or parts[0] != 'lohkous' or not all(x.isdigit() for x in parts[1:3]):
            raise ValueError('invalid Lohkous path')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('cspuz Lohkous requires at least two rows and columns')
        body, cells, pos, i, after_clue = parts[3], {}, 0, 0, False
        while i < len(body):
            if pos >= w * h:
                raise ValueError('Lohkous clues exceed grid')
            ch = body[i]
            if ch in '0123456789':
                start = i
                while i < len(body) and body[i] in '0123456789':
                    i += 1
                cells[divmod(pos, w)] = tuple('?' if x == '0' else int(x) for x in body[start:i])
                pos += 1
                after_clue = True
            elif ch in 'abcdefghijklmnopqrstuvwxyz':
                pos += ord(ch) - ord('a') + (0 if after_clue else 1)
                if pos > w * h:
                    raise ValueError('Lohkous clues exceed grid')
                i += 1
                after_clue = False
            else:
                raise ValueError('invalid Lohkous clue')
        if not cells:
            raise ValueError('cspuz Lohkous requires a clue')
        p = Puzzle('lohkous', h, w, cells, body=body)
        url = f'https://puzz.link/p?lohkous/{w}/{h}/{body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        vertical, horizontal, _ = partition.answer(p, board, status)
        out = [f'pzprv3\nlohkous\n{p.rows}\n{p.cols}\n']
        for r in range(p.rows):
            out.append(row([','.join('-' if v == '?' else str(v) for v in p.cells[r,c]) if (r,c) in p.cells else '.' for c in range(p.cols)]))
        for lines in (vertical, horizontal):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
        return ''.join(out)


ADAPTER = LohkousAdapter('lohkous', ('lohkous',), 'lohkous')
