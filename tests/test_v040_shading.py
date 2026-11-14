"""URL, cspuz, native FileIO and trace-state acceptance tests."""
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import zlib

import pytest
import puzzlekit

BASELINE = json.loads((Path(__file__).parent / 'fixtures/v040_samples.json').read_text())

# Small real samples from puzzlekit-dataset/puzzlink_crawlers/logs/merged_puzzles.csv.
SAMPLES = [
    'nurikabe/4/1/2h1', 'nurikabe/3/2/i2g2',
    'hitori/6/4/114514123456456123364364', 'hitori/5/5/2141545324512133415222351',
    'kurodoko/3/3/g3g3j3', 'kurodoko/4/4/g3k64k5g',
    'cave/5/3/6l2l3', 'bag/5/5/j39k3g4k25j',
    'nurimisaki/3/3/g.h.j', 'nurimisaki/3/3/g.g2j./',
]


@pytest.mark.parametrize('path', SAMPLES)
def test_real_samples(path):
    expected = BASELINE[path]
    result = puzzlekit.solve(path)
    assert result.status == 'unique'
    assert result.to_pzpr() == expected['file']
    assert json.loads(result.board_json) == result.board
    state = result.to_state()
    assert zlib.decompress(base64.urlsafe_b64decode(state + '=' * (-len(state) % 4)), -15).decode() == result.to_pzpr()
    assert result.to_trace_url() == f'https://pzpr-trace.net/p?state={state}&{result.normalized_url.split("?", 1)[1]}'


@pytest.mark.parametrize('url', [
    'https://puzz.link/p?nurikabe/2/2/1i',
    'https://puzz.link/?p=nurikabe/2/2/1i',
    'https://pzplus.tck.mn/p.html?nurikabe/2/2/1i',
    'https://pzpr-trace.net/p?state=ignored&nurikabe/2/2/1i',
    'https://pzpr-trace.net/p?nurikabe/2/2/1i&state=ignored',
    '?p=nurikabe/2/2/1i', '?nurikabe/2/2/1i', 'nurikabe/2/2/1i',
])
def test_url_forms(url):
    result = puzzlekit.solve(url)
    assert result.normalized_url == 'https://puzz.link/p?nurikabe/2/2/1i'
    assert result.status == 'unique'


def test_multiple_and_no_solution():
    result = puzzlekit.solve('nurikabe/2/2/2i')
    assert result.status == 'multiple'
    assert result.to_pzpr().endswith('2 . \n. # \n')
    bad = puzzlekit.solve('nurikabe/2/2/1111')
    assert bad.status == 'no_solution'
    with pytest.raises(ValueError):
        bad.to_state()


@pytest.mark.parametrize('multiple,unsatisfiable', [
    ('hitori/2/2/....', 'hitori/2/2/1111'),
    ('kurodoko/2/2/j', 'kurodoko/2/2/4i'),
    ('cave/2/2/j', 'cave/2/2/4i'),
    ('nurimisaki/2/2/j', 'nurimisaki/2/2/4i'),
])
def test_other_puzzles_preserve_unknowns_and_reject_no_solution(multiple, unsatisfiable):
    result = puzzlekit.solve(multiple)
    assert result.status == 'multiple'
    assert result.to_pzpr() == BASELINE[multiple]['file']
    assert result.to_state()
    bad = puzzlekit.solve(unsatisfiable)
    assert bad.status == 'no_solution'
    with pytest.raises(ValueError):
        bad.to_pzpr()


def test_number_encodings_and_literal_hitori_percent():
    result = puzzlekit.solve('https://puzz.link/?p=nurikabe/2/1/+100g')
    assert '+100' in result.normalized_url
    with pytest.raises(ValueError, match='cspuz'):
        puzzlekit.solve('https://puzz.link/p?hitori/3/1/%20')


@pytest.mark.parametrize('url', [
    'nurikabe/2/2/1zz', 'nurikabe/0/2/1', 'nurikabe/2/2/-a',
    'nurikabe/b/2/2/1i', 'nurikabe/2/2/1i/extra',
    'https://puzz.link/p?nurikabe/2/2/1i&rules=other',
])
def test_rejects_bad_or_unhandled_input(url):
    with pytest.raises(ValueError):
        puzzlekit.solve(url)


@pytest.mark.parametrize('path', ['hitori/2/1/0.', 'hitori/1/1/-10',
                                 'hitori/1/1/@', 'nurikabe/1/1/=000'])
def test_codec_support_does_not_overstate_backend_limits(path):
    with pytest.raises(ValueError, match='cspuz'):
        puzzlekit.solve(path)


def test_real_pzpr_state_import():
    root = Path(os.environ.get('PUZZLEKIT_PZPRJS', Path(__file__).resolve().parents[2] / 'pzprjs'))
    node = shutil.which('node')
    if not node or not (root / 'dist/js/pzpr.js').exists():
        pytest.skip('custom pzprjs checkout and Node 24+ required')
    version = subprocess.check_output([node, '-p', 'process.versions.node'], text=True)
    if int(version.split('.')[0]) < 24:
        pytest.skip('pzpr state decoder requires Node 24+')
    cases = []
    for source in SAMPLES + ['nurikabe/2/2/2i', 'hitori/2/2/....',
                             'kurodoko/2/2/j', 'cave/2/2/j', 'nurimisaki/2/2/j']:
        result = puzzlekit.solve(source)
        data = BASELINE[source]
        cases.append({'url': result.normalized_url, 'state': result.to_state(),
                      'file': result.to_pzpr(), 'type': data['type'],
                      'clues': data['clues'], 'answers': data['answers'],
                      'complete': data['complete']})
    script = Path(__file__).parent / 'integration/pzpr_state_check.js'
    subprocess.run([node, str(script), str(root)], input=json.dumps(cases), text=True, check=True)
