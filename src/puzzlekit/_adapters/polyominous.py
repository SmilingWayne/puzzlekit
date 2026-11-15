"""Polyomino clues and region boundaries for Pentominous and Tetrominous."""
from dataclasses import replace
from puzzlekit._adapters import extended, shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.model import Puzzle

_SHAPES = {
    'tetrominous': ['1:1111', '2:010111', '2:1111', '2:011110', '2:011101'],
    'pentominous': ['3:001111010', '1:11111', '2:01010111', '2:01011110',
                    '2:011111', '3:001111001', '2:110111', '3:001001111',
                    '3:001011110', '3:010111010', '2:01011101', '3:001111100'],
}


def _canonical(points):
    variants = []
    for swap in (False, True):
        for sy in (-1, 1):
            for sx in (-1, 1):
                transformed = [(sy * (c if swap else r), sx * (r if swap else c)) for r, c in points]
                top, left = min(r for r, _ in transformed), min(c for _, c in transformed)
                variants.append(tuple(sorted((r - top, c - left) for r, c in transformed)))
    return min(variants)


def _shapes(pid):
    result = {}
    for i, pattern in enumerate(_SHAPES[pid]):
        width, bits = pattern.split(':')
        width = int(width)
        points = [divmod(k, width) for k, value in enumerate(bits) if value == '1']
        result[_canonical(points)] = i
    return result


class PolyominousAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if len(parts) != 4 or parts[0] != self.name or not all(s.isdigit() for s in parts[1:3]):
            raise ValueError('invalid polyomino puzzle path')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('polyomino puzzles require at least two rows and columns')
        body, cells, pos, i = parts[3], {}, 0, 0
        while i < len(body) and pos < w*h:
            ch = body[i]
            if 'g' <= ch <= 'z':
                pos += ord(ch) - ord('g') + 1
            else:
                if ch == 'c': value = '*'
                elif ch == '.': value = '?'
                elif ch in '0123456789ab' and int(ch, 16) < len(_SHAPES[self.name]): value = int(ch, 16)
                else: raise ValueError('invalid polyomino clue')
                cells[divmod(pos, w)] = value
                pos += 1
            i += 1
        if pos != w*h:
            raise ValueError('incomplete polyomino clue data')
        remainder = body[i:]
        count = (h*(w-1)+4)//5 + ((h-1)*w+4)//5
        if remainder and (len(remainder) != count or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in remainder)):
            raise ValueError('invalid polyomino given boundaries')
        borders = BorderCodec().decode(remainder, h, w)[0] if remainder else {}
        p = Puzzle(self.name, h, w, cells, borders, body=body)
        url = f'https://puzz.link/p?{self.name}/{w}/{h}/{body}' + ('/' if body.endswith('.') else '')
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        ans = extended.answer(replace(p, puzzle_type='shikaku'), board, status)
        vertical, horizontal = ans['vertical'], ans['horizontal']
        h, w = p.rows, p.cols
        for i in p.borders:
            if i < h*(w-1): vertical[i//(w-1)][i%(w-1)] = True
            else:
                j = i - h*(w-1)
                horizontal[j//w][j%w] = True
        values = [[None]*w for _ in range(h)]
        unseen = {(r,c) for r in range(h) for c in range(w) if p.cells.get((r,c)) != '*'}
        shapes = _shapes(p.puzzle_type)
        piece_size = 5 if p.puzzle_type == 'pentominous' else 4
        while unseen:
            start = unseen.pop()
            group, stack = {start}, [start]
            while stack:
                r,c = stack.pop()
                adjacent = []
                if c and vertical[r][c-1] is False: adjacent.append((r,c-1))
                if c+1 < w and vertical[r][c] is False: adjacent.append((r,c+1))
                if r and horizontal[r-1][c] is False: adjacent.append((r-1,c))
                if r+1 < h and horizontal[r][c] is False: adjacent.append((r+1,c))
                for point in adjacent:
                    if point in unseen:
                        unseen.remove(point)
                        group.add(point)
                        stack.append(point)
            if len(group) == piece_size:
                value = shapes[_canonical(group)]
                for r,c in group:
                    if (r,c) not in p.cells: values[r][c] = value
        out = [f'pzprv3\n{p.puzzle_type}\n{h}\n{w}\n']
        out.extend(row(['-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(w)]) for r in range(h))
        out.extend(row([v if v is not None else '.' for v in line]) for line in values)
        for r, line in enumerate(vertical):
            out.append(row(['X' if r*(w-1)+c in p.borders else 1 if v is True else -1 if v is False else 0 for c,v in enumerate(line)]))
        for r, line in enumerate(horizontal):
            out.append(row(['X' if h*(w-1)+r*w+c in p.borders else 1 if v is True else -1 if v is False else 0 for c,v in enumerate(line)]))
        return ''.join(out)
