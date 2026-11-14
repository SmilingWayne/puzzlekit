"""Real-corpus and independent pzprjs acceptance for the second batch."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest
import puzzlekit

BASELINE = json.loads((Path(__file__).parent / 'fixtures/v040_samples.json').read_text())

# Record IDs and URLs from puzzlekit-dataset/puzzlink_crawlers/logs/merged_puzzles.csv.
SAMPLES = [
    ('slitherlink0446', 'slither/3/2/h17d'), ('slitherlink3255', 'slither/2/3/716c'),
    ('masyu0860', 'mashu/3/3/313'), ('masyu1033', 'mashu/3/3/k0k'),
    ('akari0915', 'akari/2/3/bhb'), ('akari1441', 'akari/3/3/cl'),
    ('kurotto0063', 'kurotto/5/5/c2g5zg'), ('kurotto0122', 'kurotto/5/5/0i0l0j2j09h'),
    ('shikaku0489', 'shikaku/4/2/11i24g'), ('shikaku0144', 'shikaku/4/4/1111111111111111'),
    ('heyawake1414', 'heyawake/3/3/fgtgm'), ('heyawake2325', 'heyawake/3/3/pgmg1g111'),
    ('aqre0115', 'aqre/5/2/70jg011'), ('aqre0075', 'aqre/3/5/i9r6o1g001'),
    # Irregular rooms: pzpr anchors a clue in the leftmost, then topmost cell.
    ('aqre_irregular', 'aqre/5/5/v5kmlael1g010070'),
    ('lits0927', 'lits/4/3/64cg'), ('lits0192', 'lits/5/4/89104r4'),
    ('norinori0356', 'norinori/8/2/804vs'), ('norinori0406', 'norinori/4/4/n804jo'),
    ('yajilin12296', 'yajilin/3/3/c40e'), ('yajilin12618', 'yajilin/3/3/d20d'),
]

PARTIAL = [
    ('slither/2/2/1i', 'slither/2/2/4444'),
    ('mashu/3/3/030', 'mashu/3/3/900'),
    ('lightup/2/2/j', 'lightup/2/2/4444'),
    ('kurotto/2/2/j', 'kurotto/2/2/fi'),
    ('shikaku/2/2/2h2', 'shikaku/2/2/j'),
    ('heyawake/2/2/00g', 'heyawake/2/2/004'),
    ('aqre/2/2/00g', 'aqre/2/2/005'),
    ('lits/4/3/0000', 'lits/2/2/00'),
    ('norinori/2/2/00', 'norinori/2/2/vv'),
    ('yajilin/3/3/i', 'yajilin/3/3/14h'),
]


@pytest.mark.parametrize('record,path', SAMPLES)
def test_real_samples(record, path):
    result = puzzlekit.solve(path)
    assert result.status == 'unique', record
    assert result.to_pzpr() == BASELINE[path]['file'], record
    assert json.loads(result.board_json) == result.board
    assert result.to_trace_url().startswith('https://pzpr-trace.net/p?state=')


@pytest.mark.parametrize('multiple,no_solution', PARTIAL)
def test_multiple_and_no_solution(multiple, no_solution):
    result = puzzlekit.solve(multiple)
    assert result.status == 'multiple'
    assert result.to_pzpr() == BASELINE[multiple]['file']
    assert result.to_state()
    bad = puzzlekit.solve(no_solution)
    assert bad.status == 'no_solution'
    with pytest.raises(ValueError):
        bad.to_pzpr()


@pytest.mark.parametrize('path', ['slither/2/2/0000', 'slither/2/2/j',
                                   'mashu/3/3/000', 'yajilin/2/2/20202020'])
def test_rejects_models_that_could_count_empty_loops(path):
    with pytest.raises(ValueError, match='empty .*loop'):
        puzzlekit.solve(path)


@pytest.mark.parametrize('path', ['slither/f/3/3/gdk', 'mashu/f/4/4/0003i0',
                                   'aqre/b/3/3/00g', 'yajilin/o/3/3/i'])
def test_rule_variants_not_silently_dropped(path):
    with pytest.raises(ValueError):
        puzzlekit.solve(path)


@pytest.mark.parametrize('path', ['yajilin/3/3/-1100h', 'aqre/2/2/00=000'])
def test_codec_keeps_clues_outside_cspuz_limits(path):
    with pytest.raises(ValueError, match='cspuz'):
        puzzlekit.solve(path)


def test_yajilin_display_flag_is_preserved():
    result = puzzlekit.solve('yajirin/b/3/3/c40e')
    assert '?yajilin/b/3/3/' in result.normalized_url
    assert result.status == 'unique'


@pytest.mark.parametrize('record,path', SAMPLES)
def test_link_forms(record, path):
    expected = puzzlekit.solve(path)
    for source in (f'?p={path}', f'https://puzz.link/p?{path}',
                   f'https://pzplus.tck.mn/p.html?{path}',
                   f'https://pzpr-trace.net/p?state=ignored&{path}'):
        actual = puzzlekit.solve(source)
        assert actual.normalized_url == expected.normalized_url
        assert actual.board == expected.board


def test_real_pzpr_state_import():
    root = Path(os.environ.get('PUZZLEKIT_PZPRJS', Path(__file__).resolve().parents[2] / 'pzprjs'))
    node = shutil.which('node')
    if not node or not (root / 'dist/js/pzpr.js').exists(): pytest.skip('custom pzprjs and Node 24+ required')
    if int(subprocess.check_output([node, '-p', 'process.versions.node'], text=True).split('.')[0]) < 24:
        pytest.skip('Node 24+ required for pzpr state decoder')
    cases = []
    for path in [p for _, p in SAMPLES] + [p for p, _ in PARTIAL]:
        result = puzzlekit.solve(path)
        data = BASELINE[path]
        cases.append({'source': path, 'url': result.normalized_url, 'state': result.to_state(),
                      'file': result.to_pzpr(), 'type': data['type'], 'width': data['width'],
                      'height': data['height'], 'answers': data['answers'], 'complete': data['complete']})
    script = Path(__file__).parent / 'integration/pzpr_extended_check.js'
    subprocess.run([node, str(script), str(root)], input=json.dumps(cases), text=True, check=True)
