"""Solve fixed puzzle samples and verify native pzpr export."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

import puzzlekit

FIXTURES = Path(__file__).parent / 'fixtures' / 'adapters'
CASES = [
    case
    for fixture in sorted(FIXTURES.glob('*.json'))
    for case in json.loads(fixture.read_text(encoding='utf-8'))
]


@pytest.mark.parametrize('case', CASES, ids=[case.get('record', case['path']) for case in CASES])
def test_adapter(case):
    result = puzzlekit.solve(case['path'])
    assert result.status == case['status']
    if result.status == 'no_solution':
        for export in (result.to_pzpr, result.to_state, result.to_trace_url):
            with pytest.raises(ValueError):
                export()
    else:
        assert result.to_pzpr() == case['fileio']


def test_pzprjs_state_import():
    default_checkout = Path(__file__).resolve().parents[2] / 'pzprjs'
    checkout = Path(os.environ.get('PUZZLEKIT_PZPRJS', default_checkout)).resolve()
    node = shutil.which('node')
    if not node or not (checkout / 'dist/js/pzpr.js').is_file():
        pytest.skip('Node 24+ and a built custom pzprjs checkout are required')
    major = subprocess.check_output([node, '-p', 'process.versions.node.split(".")[0]'], text=True)
    if int(major) < 24:
        pytest.skip('The pzpr state decoder requires Node 24+')

    cases = []
    for case in CASES:
        if 'fileio' not in case:
            continue
        result = puzzlekit.solve(case['path'])
        cases.append({
            'source': case['path'],
            'url': result.normalized_url,
            'state': result.to_state(),
            'file': case['fileio'],
            'complete': case['status'] == 'unique',
        })

    script = Path(__file__).parent / 'integration' / 'pzpr_state_check.js'
    subprocess.run([node, str(script), str(checkout)], input=json.dumps(cases), text=True, check=True)
