"""Regional Yajilin room clues, shading and loop edges."""
from dataclasses import replace
from puzzlekit._adapters.adapter import Adapter
from puzzlekit._adapters import regions, shading, yajilin
from puzzlekit._adapters.grid import border_to_region_grid


class RegionalYajilinAdapter(Adapter):
    def parse(self, source):
        parts = shading.puzzle_path(source).split('/')
        if len(parts) == 6 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if len(parts) == 5 and parts[-1] == '' and parts[-2].endswith('.'):
            parts.pop()
        if not parts or parts[0] not in ('yajilin-regions', 'yajirin-regions'):
            raise ValueError('invalid Regional Yajilin path')
        outside = len(parts) == 5 and parts[1] == 'o'
        if outside:
            parts.pop(1)
        if len(parts) != 4:
            raise ValueError('unsupported Regional Yajilin variant')
        p = regions.decode_regions('/'.join(['heyawake', *parts[1:]]))
        if any(isinstance(v, int) and v >= 4096 for v in p.cells.values()):
            raise ValueError('Regional Yajilin clues must be below 4096')
        p.puzzle_type, p.rule_flag = 'yajilin-regions', 'o' if outside else ''
        base = regions.encode_regions(replace(p, puzzle_type='heyawake', rule_flag=''))
        url = base.replace('?heyawake/', '?yajilin-regions/' + ('o/' if outside else ''), 1)
        return p, url, url

    def fileio(self, p, board, status):
        def row(values): return ' '.join(str(v) for v in values) + ' \n'
        h,w = p.rows,p.cols
        a = yajilin.answer(replace(p, cells={}), board, status)
        grid, last = border_to_region_grid(p.borders, h, w)
        out = [f'pzprv3\nyajilin-regions\n{h}\n{w}\n']
        if p.rule_flag: out.append('o\n')
        out.append(f'{last+1}\n')
        out.extend(row(line) for line in grid)
        out.extend(row(['-' if p.cells.get((r,c)) == '?' else p.cells.get((r,c), '.') for c in range(w)]) for r in range(h))
        out.extend(row(['#' if v == 'black' else '+' if v == 'white' else '.' for v in line]) for line in a['cells'])
        for name in ('vertical', 'horizontal'):
            out.extend(row([1 if v is True else -1 if v is False else 0 for v in line]) for line in a[name])
        return ''.join(out)


ADAPTER = RegionalYajilinAdapter('yajilin-regions', ('yajilin-regions', 'yajirin-regions'), 'yajilin-regions')
