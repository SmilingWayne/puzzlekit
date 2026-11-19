#!/usr/bin/env python3
"""Generate the puzzle coverage table (pzpr puzzles x PuzzleKit / dataset).

Two steps, so CI never needs the sibling repositories:

``collect``  Read the sibling ``pzprjs`` checkout and ``puzzlekit-dataset``
             and write a committed snapshot, ``docs/puzzle_table.json``.
``render``   Build the markdown table from the snapshot plus the live adapter
             registry, and inject it between marker comments (``--write``) or
             verify the files are current (``--check``).

Rows are pzpr puzzle IDs (the names pzpr-trace accepts, e.g. ``yajilin``).

Adding a column
---------------
* Data that needs the sibling repositories: add a *collector* to ``COLLECTORS``
  (``fn(ctx) -> {pid: {field: value}}``); it runs in ``collect`` only and its
  fields are stored in the snapshot.
* Data derivable from the snapshot or PuzzleKit itself: add a field in
  ``derive_fields``.
* Then add a ``Column`` to ``COLUMNS``. Nothing else changes.
"""
import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parent
SNAPSHOT = PROJECT / 'docs' / 'puzzle_table.json'
SNAPSHOT_VERSION = 1

# Dataset directory -> pzpr PID, for names that cannot be matched automatically.
DATASET_PID_OVERRIDES = {
    'ABCEndView': 'easyasabc',
    'Galaxies': 'tentaisho',
    'GokigenNaname': 'gokigen',
    'Kuromasu': 'kurodoko',
    'Kuroshuto': 'kurochute',
    'Shirokuro': 'wblink',
    'Tent': 'tents',
}

# Dataset directories that are not pzpr puzzles; expected, so not reported.
DATASET_IGNORED = {
}

NODE_LIST_VARIETIES = r'''
const pzpr = require(process.argv[1]);
const out = pzpr.variety.getList().map((pid) => {
  const v = pzpr.variety(pid);
  return {pid, en: v.en, urlid: v.urlid, aliases: Object.values(v.alias || {})};
});
console.log(JSON.stringify(out));
'''


# --------------------------------------------------------------------- collect

@dataclass
class Context:
    pzprjs: Path
    dataset: Path
    varieties: list
    verbose: bool = False


def git_rev(path: Path) -> str:
    try:
        return subprocess.check_output(['git', '-C', str(path), 'rev-parse', '--short=12', 'HEAD'],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return 'unknown'


def list_varieties(pzprjs: Path) -> list:
    built = pzprjs / 'dist/js/pzpr.js'
    if not built.is_file():
        raise SystemExit(f'built pzprjs not found: {built} (run its build first)')
    out = subprocess.check_output(['node', '-e', NODE_LIST_VARIETIES, str(built.resolve())], text=True)
    return json.loads(out)


def squash(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text.lower())


def normalize_problem(problem: str) -> str:
    lines = problem.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return '\n'.join(' '.join(line.split()) for line in lines).strip()


def load_cases(directory: Path) -> dict:
    """Merge the legacy monolith and numbered shards like cleaners.io.union_cases."""
    name = directory.name
    shard = re.compile(re.escape(name) + r'_dataset_(\d{3})\.json')
    files = []
    legacy = directory / f'{name}_dataset.json'
    if legacy.is_file():
        files.append(legacy)
    files += sorted((p for p in directory.iterdir() if shard.fullmatch(p.name)),
                    key=lambda p: int(shard.fullmatch(p.name).group(1)))
    union, seen = {}, {}
    for path in files:
        payload = json.loads(path.read_text(encoding='utf-8'))
        for cid, case in (payload.get('data') or {}).items():
            if not isinstance(case, dict):
                continue
            key = normalize_problem(str(case.get('problem') or ''))
            if key and seen.get(key, cid) != cid:
                union.pop(seen[key], None)
            union[cid] = case
            if key:
                seen[key] = cid
    return union


def problem_size(problem: str):
    """Return (cols, rows) from the dataset header line ``rows cols``."""
    parts = (problem or '').strip().split('\n')[0].split()
    if len(parts) < 2 or not (parts[0].isdigit() and parts[1].isdigit()):
        return None
    return int(parts[1]), int(parts[0])


def match_dataset(varieties: list, dataset_dirs: list):
    """Map each dataset directory to a PID; return (mapping, unmatched)."""
    names = {}
    for variety in varieties:
        for label in [variety['pid'], variety['urlid'], variety['en'], *variety['aliases']]:
            names.setdefault(squash(label), set()).add(variety['pid'])
    pids = {variety['pid'] for variety in varieties}
    mapping, unmatched = {}, []
    for directory in dataset_dirs:
        if directory in DATASET_PID_OVERRIDES:
            pid = DATASET_PID_OVERRIDES[directory]
            if pid not in pids:
                raise SystemExit(f'override {directory} -> {pid}: unknown pzpr PID')
            mapping[directory] = pid
            continue
        found = names.get(squash(directory), set())
        if len(found) == 1:
            mapping[directory] = next(iter(found))
        elif directory not in DATASET_IGNORED:
            unmatched.append((directory, sorted(found)))
    return mapping, unmatched


def collect_dataset(ctx: Context) -> dict:
    root = ctx.dataset / 'assets/data'
    dirs = sorted(p.name for p in root.iterdir() if p.is_dir() and any(p.glob('*_dataset*.json')))
    mapping, unmatched = match_dataset(ctx.varieties, dirs)
    taken = {}
    for directory, pid in mapping.items():
        if pid in taken:
            raise SystemExit(f'{directory} and {taken[pid]} both map to {pid}; add an override')
        taken[pid] = directory
    ambiguous = [(d, c) for d, c in unmatched if c]
    if ambiguous:
        raise SystemExit('ambiguous dataset directories (add overrides): ' + ', '.join(
            f'{d} -> {"/".join(c)}' for d, c in ambiguous))
    if unmatched:
        print(f'note: {len(unmatched)} dataset directories have no pzpr PID and are not listed',
              file=sys.stderr)
        if ctx.verbose:
            print('      ' + ', '.join(d for d, _ in unmatched), file=sys.stderr)
    result = {}
    for directory, pid in mapping.items():
        cases = load_cases(root / directory)
        sizes = [s for s in (problem_size(c.get('problem', '')) for c in cases.values()) if s]
        biggest = max(sizes, key=lambda s: (s[0] * s[1], s[0]), default=None)
        result[pid] = {
            'dataset_dir': directory,
            'problems': len(cases),
            'solutions': sum(1 for c in cases.values() if str(c.get('solution', '')).strip()),
            'max_size': list(biggest) if biggest else None,
        }
    return result


COLLECTORS: list[Callable[[Context], dict]] = [collect_dataset]


def collect(args) -> int:
    varieties = list_varieties(args.pzprjs)
    ctx = Context(args.pzprjs, args.dataset, varieties, args.verbose)
    rows = {v['pid']: {'pid': v['pid'], 'name': v['en'], 'urlid': v['urlid'],
                       'aliases': sorted(set(v['aliases']))} for v in varieties}
    for collector in COLLECTORS:
        for pid, fields in collector(ctx).items():
            rows[pid].update(fields)
    snapshot = {
        'version': SNAPSHOT_VERSION,
        'sources': {'pzprjs': git_rev(args.pzprjs), 'puzzlekit-dataset': git_rev(args.dataset)},
        'puzzles': [rows[pid] for pid in sorted(rows)],
    }
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'wrote {SNAPSHOT.relative_to(PROJECT)}: {len(rows)} puzzles', file=sys.stderr)
    return 0


# ---------------------------------------------------------------------- render

def adapter_pids(rows: list) -> dict:
    """Map each verified adapter to its pzpr PID through its URL tokens."""
    try:
        from puzzlekit.registry import ADAPTERS
    except ImportError:
        sys.path.insert(0, str(PROJECT / 'src'))
        from puzzlekit.registry import ADAPTERS
    lookup = {}
    for row in rows:
        for label in [row['pid'], row['urlid'], *row['aliases']]:
            lookup[label] = row['pid']
    result = {}
    for adapter in ADAPTERS:
        pids = {lookup[token] for token in (adapter.name, *adapter.aliases) if token in lookup}
        if len(pids) != 1:
            raise SystemExit(f'adapter {adapter.name!r} resolves to {sorted(pids) or "no pzpr PID"}')
        pid = next(iter(pids))
        if pid in result:
            raise SystemExit(f'adapters {result[pid]!r} and {adapter.name!r} share pzpr PID {pid}')
        result[pid] = adapter.name
    return result


def derive_fields(rows: list) -> list:
    """Add values computed at render time (not stored in the snapshot)."""
    supported = adapter_pids(rows)
    return [{**row, 'supported': row['pid'] in supported} for row in rows]


@dataclass(frozen=True)
class Column:
    header: str
    cell: Callable[[dict], str]
    align: str = 'left'
    sort_key: Callable[[dict], object] = None


def count(field):
    return lambda row: f'{row.get(field, 0):,}'


def max_size(row):
    size = row.get('max_size')
    return f'{size[0]}x{size[1]}' if size else '—'


COLUMNS = [
    Column('Puzzle', lambda row: f'`{row["pid"]}`'),
    Column('s?', lambda row: '✓' if row['supported'] else '', 'center'),
    Column('#.P', count('problems'), 'right'),
    Column('#.S', count('solutions'), 'right'),
    Column('MS', max_size, 'right'),
]
_ALIGN = {'left': ':---', 'center': ':---:', 'right': '---:'}


def render_table(rows: list) -> str:
    lines = ['| ' + ' | '.join(c.header for c in COLUMNS) + ' |',
             '| ' + ' | '.join(_ALIGN[c.align] for c in COLUMNS) + ' |']
    lines += ['| ' + ' | '.join(c.cell(row) for c in COLUMNS) + ' |' for row in rows]
    return '\n'.join(lines)


def render_summary(rows: list, sources: dict) -> str:
    supported = sum(r['supported'] for r in rows)
    with_data = sum(1 for r in rows if r.get('problems'))
    problems = sum(r.get('problems', 0) for r in rows)
    solutions = sum(r.get('solutions', 0) for r in rows)
    return (f'PuzzleKit currently supports **{supported}** of the **{len(rows)}** puzzle types '
            f'registered in pzpr. [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset) '
            f'holds {problems:,} problems ({solutions:,} with answers) for {with_data} of them.')


def render_legend(sources: dict) -> str:
    return '\n'.join([
        '- **Puzzle** — pzpr puzzle ID, as accepted by [pzpr-trace](https://pzpr-trace.net/).',
        '- **s?** — `✓` when PuzzleKit has a verified adapter (URL solving, pzpr FileIO and '
        'pzpr-trace state).',
        '- **#.P** — problems in [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset).',
        '- **#.S** — problems in the dataset that have an answer.',
        '- **MS** — largest board in the dataset by area, written `columns`x`rows`; `—` means '
        'no data.',
        '',
        f'Snapshot: pzprjs `{sources["pzprjs"]}`, puzzlekit-dataset `{sources["puzzlekit-dataset"]}`.',
    ])


# (file, marker name, renderer(rows, sources))
TARGETS = [
    (PROJECT / 'docs/PUZZLES.md', 'puzzle-table', lambda rows, src: render_table(rows)),
    (PROJECT / 'docs/PUZZLES.md', 'puzzle-legend', lambda rows, src: render_legend(src)),
    (PROJECT / 'README.md', 'puzzle-summary', lambda rows, src: render_summary(rows, src)),
]


def inject(text: str, marker: str, body: str, path: Path) -> str:
    pattern = re.compile(rf'(<!-- {marker}:start -->\n).*?(<!-- {marker}:end -->)', re.S)
    if not pattern.search(text):
        raise SystemExit(f'{path.relative_to(PROJECT)}: missing <!-- {marker}:start/end --> markers')
    return pattern.sub(lambda m: m.group(1) + body + '\n' + m.group(2), text, count=1)


def render(args) -> int:
    snapshot = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    if snapshot.get('version') != SNAPSHOT_VERSION:
        raise SystemExit('snapshot version mismatch; re-run `collect`')
    rows = derive_fields(snapshot['puzzles'])
    sources = snapshot['sources']
    outputs = {}
    for path, marker, renderer in TARGETS:
        text = outputs.get(path) or path.read_text(encoding='utf-8')
        outputs[path] = inject(text, marker, renderer(rows, sources), path)
    stale = [p for p, text in outputs.items() if p.read_text(encoding='utf-8') != text]
    if args.check:
        for path in stale:
            print(f'{path.relative_to(PROJECT)} is out of date; run '
                  f'`python scripts/puzzle_table.py render --write`', file=sys.stderr)
        return 1 if stale else 0
    if args.write:
        for path in stale:
            path.write_text(outputs[path], encoding='utf-8')
            print(f'updated {path.relative_to(PROJECT)}', file=sys.stderr)
        return 0
    print(render_table(rows))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p_collect = sub.add_parser('collect', help='refresh docs/puzzle_table.json from sibling repositories')
    p_collect.add_argument('--pzprjs', type=Path, default=WORKSPACE / 'pzprjs')
    p_collect.add_argument('--dataset', type=Path, default=WORKSPACE / 'puzzlekit-dataset')
    p_collect.add_argument('-v', '--verbose', action='store_true', help='list unmatched dataset directories')
    p_render = sub.add_parser('render', help='render the table from the snapshot')
    mode = p_render.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='update docs/PUZZLES.md and README.md')
    mode.add_argument('--check', action='store_true', help='exit 1 if generated files are stale')
    args = parser.parse_args(argv)
    return collect(args) if args.command == 'collect' else render(args)


if __name__ == '__main__':
    sys.exit(main())
