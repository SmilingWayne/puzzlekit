"""The generated puzzle table stays consistent with the registry and snapshot."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'puzzle_table.py'
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason='scripts/ is not part of the sdist')


@pytest.fixture(scope='module')
def table():
    spec = importlib.util.spec_from_file_location('puzzle_table', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope='module')
def rows(table):
    return table.derive_fields(json.loads(table.SNAPSHOT.read_text(encoding='utf-8'))['puzzles'])


def test_generated_files_are_current(table):
    assert table.main(['render', '--check']) == 0


def test_every_adapter_has_one_pzpr_pid(table, rows):
    from puzzlekit.registry import ADAPTERS
    assert sum(row['supported'] for row in rows) == len(ADAPTERS)


def test_rows_use_pzpr_ids_without_duplicates(rows):
    pids = [row['pid'] for row in rows]
    assert len(pids) == len(set(pids))
    assert all(pid == pid.lower() and ' ' not in pid for pid in pids)
    assert {'yajilin', 'slither', 'mashu', 'nurikabe'} <= set(pids)


def test_dataset_columns(table, rows):
    by_pid = {row['pid']: row for row in rows}
    assert by_pid['yajilin']['supported']
    assert 0 < by_pid['yajilin']['solutions'] <= by_pid['yajilin']['problems']
    assert table.max_size({'max_size': [18, 10]}) == '18x10'
    assert table.max_size({}) == '—'


def test_size_is_columns_by_rows(table):
    assert table.problem_size('10 18\n- -') == (18, 10)
    assert table.problem_size('') is None


def test_inject_replaces_only_marked_block(table):
    text = 'a\n<!-- x:start -->\nold\n<!-- x:end -->\nb\n'
    assert table.inject(text, 'x', 'new', ROOT / 'README.md') == 'a\n<!-- x:start -->\nnew\n<!-- x:end -->\nb\n'
    assert table.inject(table.inject(text, 'x', 'new', ROOT / 'README.md'), 'x', 'new', ROOT / 'README.md').count('new') == 1
