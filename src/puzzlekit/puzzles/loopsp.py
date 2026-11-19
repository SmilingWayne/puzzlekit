"""Loop Special clues and loop edges."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.model import Puzzle
from puzzlekit._adapters import extended, shading


class LoopSpecialAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if len(parts) != 4 or parts[0] != 'loopsp' or not all(s.isdigit() for s in parts[1:3]):
            raise ValueError('invalid Loop Special path')
        w, h = map(int, parts[1:3])
        if min(w, h) < 2:
            raise ValueError('Loop Special requires at least two rows and columns')
        body, cells, pos, i = parts[3], {}, 0, 0
        while i < len(body):
            ch = body[i]
            if 'n' <= ch <= 'z':
                pos += ord(ch) - ord('n') + 1
                i += 1
            else:
                if ch in 'ghijklm':
                    value, size = chr(ord('a') + ord(ch) - ord('g')), 1
                elif ch == '.':
                    value, size = -2, 1
                else:
                    size = 3 if ch == '-' else 4 if ch == '+' else 1
                    digits = body[i+1:i+size] if size > 1 else ch
                    if size > 1 and len(digits) != size - 1:
                        raise ValueError('invalid Loop Special clue')
                    if any(d not in '0123456789abcdef' for d in digits):
                        raise ValueError('invalid Loop Special clue')
                    value = int(digits, 16)
                    if not 1 <= value < 4096:
                        raise ValueError('Loop Special numbers must be 1–4095 or ?')
                if pos >= w*h:
                    raise ValueError('Loop Special clues exceed grid')
                cells[divmod(pos, w)] = value
                pos += 1
                i += size
            if pos > w*h:
                raise ValueError('Loop Special clues exceed grid')
        p = Puzzle('loopsp', h, w, cells, body=body)
        url = f'https://puzz.link/p?loopsp/{w}/{h}/{body}' + ('/' if body.endswith('.') else '')
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        ans = extended.answer(replace(p, puzzle_type='mashu'), board, status)
        out = [f'pzprv3\nloopsp\n{p.rows}\n{p.cols}\n']
        out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
        for lines in (ans['vertical'], ans['horizontal']):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in lines)
        return ''.join(out)


ADAPTER = LoopSpecialAdapter('loopsp', ('loopsp',), 'loopsp')
