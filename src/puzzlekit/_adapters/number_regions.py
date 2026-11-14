"""Roma and Star Battle room clues and native answer marks."""
from puzzlekit._adapters import number10, shading
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters.codecs import BorderCodec
from puzzlekit._adapters.grid import border_to_region_grid
from puzzlekit._adapters.model import Puzzle


class NumberRegionAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) not in (4, 5) or parts[0] != self.name or not parts[1].isdigit() or not parts[2].isdigit():
            raise ValueError('invalid room puzzle path')
        pid, w, h = parts[0], int(parts[1]), int(parts[2])
        if min(w, h) < 2:
            raise ValueError('cspuz room puzzles require at least two rows and columns')
        if pid == 'starbattle':
            if len(parts) != 5 or w != h or not parts[3].isdigit() or not 1 <= int(parts[3]) <= w:
                raise ValueError('cspuz Star Battle requires a square board and positive star count')
            count, body = parts[3], parts[4]
        else:
            if len(parts) != 4:
                raise ValueError('invalid Roma path')
            count, body = '', parts[3]
        n = (h * (w - 1) + 4) // 5 + ((h - 1) * w + 4) // 5
        if len(body) < n or any(ch not in '0123456789abcdefghijklmnopqrstuv' for ch in body[:n]):
            raise ValueError('invalid room borders')
        borders, _ = BorderCodec().decode(body, h, w)
        if BorderCodec().encode(borders, h, w) != body[:n]:
            raise ValueError('invalid room border padding')
        rest = body[n:]
        if pid == 'roma':
            cells = number10.decode(rest, h, w, {str(i): i for i in range(1, 6)})
            if 5 not in cells.values():
                raise ValueError('cspuz Roma requires a goal')
            rest = number10.encode(cells, h, w, {i: str(i) for i in range(1, 6)})
        else:
            if rest:
                raise ValueError('unexpected Star Battle data')
            cells = {}
        p = Puzzle(pid, h, w, cells, borders, rule_flag=count)
        prefix = count + '/' if count else ''
        url = f'https://puzz.link/p?{pid}/{w}/{h}/{prefix}{body[:n]}{rest}'
        return p, url, url

    def fileio(self, p, board, status):
        grid, max_id = border_to_region_grid(p.borders, p.rows, p.cols)
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        out = [f'pzprv3\n{p.puzzle_type}\n{p.rows}\n{p.cols}\n']
        if p.puzzle_type == 'starbattle':
            out.append(p.rule_flag + '\n')
        out.append(str(max_id + 1) + '\n')
        out.extend(row(line) for line in grid)
        if p.puzzle_type == 'roma':
            out.extend(row([p.cells.get((r, c), '.') for c in range(p.cols)]) for r in range(p.rows))
        answer = [['.'] * p.cols for _ in range(p.rows)]
        arrows = {'arrowUp': 1, 'arrowDown': 2, 'arrowLeft': 3, 'arrowRight': 4}
        for item in board['data']:
            if item['color'] != 'green':
                continue
            r, c, kind = item['y'] // 2, item['x'] // 2, item['item']
            if p.puzzle_type == 'roma':
                answer[r][c] = arrows[kind]
            else:
                answer[r][c] = {'filledCircle': '#', 'dot': '+'}[kind]
        out.extend(row(line) for line in answer)
        return ''.join(out)
