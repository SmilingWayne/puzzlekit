#!/usr/bin/env python3
"""Read-only small-corpus audit using subprocess timeouts and real pzprjs.

Requires the current puzzlekit installed, Node 24+, and the custom pzprjs
checkout. No dataset files are modified. See docs/V040_EXTENDED_ADAPTERS.md.
"""
import argparse
import collections
import csv
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parent
KINDS = {'slitherlink', 'masyu', 'akari', 'kurotto', 'shikaku', 'heyawake',
         'aqre', 'lits', 'norinori', 'yajilin', 'nurikabe', 'hitori',
         'kurodoko', 'cave', 'nurimisaki'}
WORKER = '''import json,puzzlekit,sys
r=puzzlekit.solve(sys.argv[1]); o={'status':r.status}
if r.status in ('unique','multiple'):
    o.update({'source':sys.argv[1], 'url':r.normalized_url, 'state':r.to_state(),
              'file':r.to_pzpr(), 'complete':r.status == 'unique'})
print(json.dumps(o))'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=WORKSPACE / 'puzzlekit-dataset/puzzlink_crawlers/logs/merged_puzzles.csv')
    parser.add_argument('--pzprjs', type=Path, default=WORKSPACE / 'pzprjs')
    parser.add_argument('--per-type', type=int, default=12)
    parser.add_argument('--max-side', type=int, default=7)
    parser.add_argument('--timeout', type=float, default=4.0)
    args = parser.parse_args()
    if args.per_type < 1 or args.max_side < 2 or args.timeout <= 0:
        parser.error('per-type and timeout must be positive; max-side must be at least 2')
    node = shutil.which('node')
    if not node or not (args.pzprjs / 'dist/js/pzpr.js').is_file():
        parser.error('Node 24+ and the built custom pzprjs checkout are required')
    version = subprocess.check_output([node, '-p', 'process.versions.node'], text=True)
    if int(version.split('.')[0]) < 24:
        parser.error('the state importer requires Node 24+')
    candidates = collections.defaultdict(list)
    with args.csv.open(newline='', encoding='utf-8') as source:
        for row in csv.DictReader(source):
            kind, url = row['puzzle_type'], row['puzz_link_url']
            match = re.search(r'/(\d+)/(\d+)/', url)
            if kind not in KINDS or not match:
                continue
            width, height = map(int, match.groups())
            if 2 <= width <= args.max_side and 2 <= height <= args.max_side:
                candidates[kind].append((width * height, row['name'], url))
    cases, report = [], {}
    for kind in sorted(KINDS):
        counts = collections.Counter()
        failures = []
        for _, name, url in sorted(candidates[kind])[:args.per_type]:
            try:
                run = subprocess.run([sys.executable, '-c', WORKER, url], text=True,
                                     capture_output=True, timeout=args.timeout, cwd=PROJECT)
            except subprocess.TimeoutExpired:
                counts['timeout'] += 1
                failures.append({'id': name, 'reason': 'timeout'})
                continue
            if run.returncode:
                counts['error'] += 1
                failures.append({'id': name, 'reason': run.stderr.splitlines()[-1] if run.stderr else 'worker failed'})
                continue
            item = json.loads(run.stdout)
            counts[item['status']] += 1
            if 'state' in item:
                cases.append(item)
        report[kind] = {'counts': dict(counts), 'failures': failures}
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    check = PROJECT / 'tests/integration/pzpr_extended_check.js'
    result = subprocess.run([node, str(check), str(args.pzprjs)], input=json.dumps(cases),
                            text=True, capture_output=True, timeout=max(60, len(cases)))
    print(result.stdout, end='')
    if result.returncode:
        print(result.stderr, file=sys.stderr, end='')
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
