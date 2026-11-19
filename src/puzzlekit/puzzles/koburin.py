"""Koburin clues, shading and loop edges."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import extended, shading, yajilin


class KoburinAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) > 4 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if not parts or parts[0] != 'koburin':
            raise ValueError('invalid Koburin path')
        flags = parts.pop(1) if len(parts) == 5 else ''
        if flags not in ('', 'o', 'm', 'b', 'om', 'ob', 'mb', 'omb') or len(parts) != 4:
            raise ValueError('unsupported Koburin variant')
        p = extended.decode_extended('/'.join(['slither', *parts[1:]]))
        if min(p.rows, p.cols) < 2:
            raise ValueError('Koburin requires at least two rows and columns')
        yajilin.check_backend_rules(replace(p, cells={k: (1, 0) for k in p.cells}))
        p.puzzle_type, p.rule_flag = 'koburin', flags
        body = extended.encode_extended(replace(p, puzzle_type='slither')).split('?', 1)[1].split('/', 3)[3]
        url = f'https://puzz.link/p?koburin/{flags + "/" if flags else ""}{p.cols}/{p.rows}/{body}'
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        a = yajilin.answer(p, board, status)
        out = [f'pzprv3\nkoburin\n{p.rows}\n{p.cols}\n']
        for flag in 'omb':
            if flag in p.rule_flag: out.append(flag + '\n')
        out.extend(row(['-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(p.cols)]) for r in range(p.rows))
        out.extend(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]) for line in a['cells'])
        for name in ('vertical', 'horizontal'):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in a[name])
        return ''.join(out)


ADAPTER = KoburinAdapter('koburin', ('koburin',), 'koburin')
