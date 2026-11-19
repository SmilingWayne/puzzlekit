"""Kouchoku vertex clues and free line segments."""
from puzzlekit._adapters import shading
from puzzlekit._adapters.model import Puzzle


def decode(source):
    parts = shading.puzzle_path(source).split('/')
    if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
        parts.pop()
    if len(parts) != 4 or parts[0] != 'kouchoku' or not all(x.isdigit() for x in parts[1:3]):
        raise ValueError('invalid Kouchoku path')
    w, h = map(int, parts[1:3])
    if min(w, h) < 1:
        raise ValueError('invalid Kouchoku dimensions')
    cells, pos = {}, 0
    for ch in parts[3]:
        if ch in '0123456789':
            pos += int(ch) + 1
        elif ch == '.' or 'a' <= ch <= 'z':
            if pos >= (h+1)*(w+1):
                raise ValueError('Kouchoku clues exceed grid')
            cells[divmod(pos, w+1)] = '?' if ch == '.' else ord(ch) - ord('a') + 1
            pos += 1
        else:
            raise ValueError('invalid Kouchoku clue')
        if pos > (h+1)*(w+1):
            raise ValueError('Kouchoku clues exceed grid')
    if not cells:
        raise ValueError('Kouchoku requires at least one clue')
    return Puzzle('kouchoku', h, w, cells, body=parts[3])


def encode(p):
    return f'https://puzz.link/p?kouchoku/{p.cols}/{p.rows}/{p.body}' + ('/' if p.body.endswith('.') else '')


def answer(p, board, status):
    result = []
    if status != 'no_solution':
        for item in board['data']:
            if item['color'] == 'green':
                kind = item['item']
                if not isinstance(kind, dict) or kind.get('kind') != 'lineTo':
                    raise RuntimeError('unexpected Kouchoku answer')
                result.append((item['x']-1, item['y']-1, kind['destX']-1, kind['destY']-1))
    return result


def fileio(p, segments):
    def row(values): return ' '.join(map(str, values)) + ' \n'
    out = [f'pzprv3\nkouchoku\n{p.rows}\n{p.cols}\n']
    out.extend(row(['-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(p.cols+1)]) for r in range(p.rows+1))
    out.append(f'{len(segments)}\n')
    out.extend(' '.join(map(str, segment)) + '\n' for segment in segments)
    return ''.join(out)
