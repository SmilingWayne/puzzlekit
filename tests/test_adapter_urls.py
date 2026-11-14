"""Shared puzzle URL behavior and adapter-specific input limits."""
import base64
import zlib

import pytest

import puzzlekit


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


def test_trace_url_carries_fileio_and_normalized_path():
    result = puzzlekit.solve('bag/5/5/j39k3g4k25j')
    state = result.to_state()
    compressed = base64.urlsafe_b64decode(state + '=' * (-len(state) % 4))
    assert zlib.decompress(compressed, -15).decode() == result.to_pzpr()
    assert result.to_trace_url() == f'https://pzpr-trace.net/p?state={state}&cave/5/5/j39k3g4k25j'
